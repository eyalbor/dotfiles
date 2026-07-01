#!/usr/bin/env python3
"""
Enable AWS Bedrock Model Invocation Logging

Enables model invocation logging to CloudWatch Logs for exact usage and cost tracking.

Requirements:
    pip install boto3

Usage:
    python bedrock_enable_logging.py
    python bedrock_enable_logging.py --profile <aws-profile>
    python bedrock_enable_logging.py --log-group /aws/bedrock/invocations
    python bedrock_enable_logging.py --status
"""

import argparse
import json
import sys

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print('Error: boto3 is required. Install with: pip install boto3')
    sys.exit(1)

DEFAULT_LOG_GROUP = '/aws/bedrock/model-invocations'
DEFAULT_ROLE_NAME = 'BedrockModelInvocationLoggingRole'

# Trust policy allowing Bedrock to assume the role
BEDROCK_TRUST_POLICY = {
    'Version': '2012-10-17',
    'Statement': [{
        'Effect': 'Allow',
        'Principal': {
            'Service': 'bedrock.amazonaws.com'
        },
        'Action': 'sts:AssumeRole'
    }]
}

# Policy allowing writing to CloudWatch Logs
CLOUDWATCH_LOGS_POLICY = {
    'Version':
        '2012-10-17',
    'Statement': [{
        'Effect': 'Allow',
        'Action': ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
        'Resource': 'arn:aws:logs:*:*:log-group:/aws/bedrock/*'
    }]
}


def get_or_create_logging_role(session: boto3.Session, role_name: str) -> str:
    """Get existing role ARN or create a new role for Bedrock logging."""
    iam = session.client('iam')

    # Check if role already exists
    try:
        response = iam.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"Using existing IAM role: {role_arn}")
        return role_arn
    except ClientError as e:
        if 'NoSuchEntity' not in str(e):
            raise

    # Create the role
    print(f"Creating IAM role: {role_name}")
    try:
        response = iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(BEDROCK_TRUST_POLICY),
                                   Description='Role for Bedrock to write model invocation logs to CloudWatch', Tags=[
                                       {
                                           'Key': 'CreatedBy',
                                           'Value': 'bedrock-enable-logging-script'
                                       },
                                   ])
        role_arn = response['Role']['Arn']
        print(f"Created IAM role: {role_arn}")

        # Attach inline policy for CloudWatch Logs
        print('Attaching CloudWatch Logs policy...')
        iam.put_role_policy(RoleName=role_name, PolicyName='BedrockCloudWatchLogsPolicy', PolicyDocument=json.dumps(CLOUDWATCH_LOGS_POLICY))

        # Wait a moment for IAM propagation
        import time
        print('Waiting for IAM role propagation (10 seconds)...')
        time.sleep(10)

        return role_arn
    except ClientError as e:
        if 'EntityAlreadyExists' in str(e):
            # Race condition - role was created by another process
            response = iam.get_role(RoleName=role_name)
            return response['Role']['Arn']
        raise


def get_current_config(bedrock_client) -> dict:
    """Get current logging configuration."""
    try:
        response = bedrock_client.get_model_invocation_logging_configuration()
        return response.get('loggingConfig', {})
    except ClientError as e:
        if 'ResourceNotFoundException' in str(e):
            return {}
        raise


def create_log_group_if_needed(logs_client, log_group_name: str) -> bool:
    """Create CloudWatch log group if it doesn't exist. Returns True if created."""
    try:
        logs_client.create_log_group(logGroupName=log_group_name)
        print(f"Created CloudWatch log group: {log_group_name}")
        return True
    except ClientError as e:
        if 'ResourceAlreadyExistsException' in str(e):
            print(f"Log group already exists: {log_group_name}")
            return False
        raise


def set_log_retention(logs_client, log_group_name: str, retention_days: int) -> None:
    """Set retention policy on log group."""
    try:
        logs_client.put_retention_policy(logGroupName=log_group_name, retentionInDays=retention_days)
        print(f"Set log retention to {retention_days} days")
    except ClientError as e:
        print(f"Warning: Could not set retention policy: {e}")


def enable_logging(
    session: boto3.Session,
    region: str,
    log_group_name: str,
    retention_days: int,
    log_text: bool,
    log_image: bool,
    force: bool,
    role_name: str,
    skip_prompts: bool = False,
) -> bool:
    """Enable Bedrock model invocation logging."""
    bedrock = session.client('bedrock', region_name=region)
    logs = session.client('logs', region_name=region)

    # Check current configuration
    print('Checking current logging configuration...')
    current_config = get_current_config(bedrock)

    if current_config:
        cw_config = current_config.get('cloudWatchConfig', {})
        s3_config = current_config.get('s3Config', {})

        if cw_config.get('logGroupName'):
            print(f"\nLogging is already enabled to CloudWatch: {cw_config['logGroupName']}")
            print('Current configuration:')
            print(json.dumps(current_config, indent=2, default=str))

            if not force and not skip_prompts:
                response = input('\nDo you want to update the configuration? (y/N): ')
                if response.lower() != 'y':
                    print('Keeping existing configuration.')
                    return True

        if s3_config.get('bucketName'):
            print(f"\nLogging is currently configured for S3: {s3_config['bucketName']}")
            if not force and not skip_prompts:
                response = input('Do you want to switch to CloudWatch logging? (y/N): ')
                if response.lower() != 'y':
                    print('Keeping existing S3 configuration.')
                    return True

    # Get or create IAM role for Bedrock logging
    print('\nSetting up IAM role for Bedrock logging...')
    role_arn = get_or_create_logging_role(session, role_name)

    # Create log group if needed
    print(f"\nSetting up CloudWatch log group: {log_group_name}")
    create_log_group_if_needed(logs, log_group_name)

    # Set retention policy
    set_log_retention(logs, log_group_name, retention_days)

    # Build logging configuration
    logging_config = {
        'cloudWatchConfig': {
            'logGroupName': log_group_name,
            'roleArn': role_arn,
        },
        'textDataDeliveryEnabled': log_text,
        'imageDataDeliveryEnabled': log_image,
        'embeddingDataDeliveryEnabled': False,
    }

    print('\nEnabling Bedrock model invocation logging...')
    print(f"  IAM role: {role_arn}")
    print(f"  Log group: {log_group_name}")
    print(f"  Text logging: {log_text}")
    print(f"  Image logging: {log_image}")
    print(f"  Retention: {retention_days} days")

    try:
        bedrock.put_model_invocation_logging_configuration(loggingConfig=logging_config)
        print('\nSuccessfully enabled Bedrock model invocation logging!')
        print('\nNote: It may take a few minutes for logs to start appearing.')
        print(
            f"View logs at: https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{log_group_name.replace('/', '$252F')}"
        )
        return True
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        error_msg = e.response.get('Error', {}).get('Message', str(e))

        if 'AccessDenied' in str(e):
            print(f"\nError: Access denied. Required IAM permissions:")
            print('  - bedrock:PutModelInvocationLoggingConfiguration')
            print('  - logs:CreateLogGroup')
            print('  - logs:PutRetentionPolicy')
        else:
            print(f"\nError enabling logging ({error_code}): {error_msg}")
        return False


def show_status(session: boto3.Session, region: str) -> None:
    """Show current logging status."""
    bedrock = session.client('bedrock', region_name=region)

    print('Checking Bedrock model invocation logging status...\n')

    try:
        config = get_current_config(bedrock)

        if not config:
            print('Status: DISABLED')
            print('\nModel invocation logging is not configured.')
            print('Run this command without --status to enable it.')
            return

        print('Status: ENABLED\n')
        print('Configuration:')
        print(json.dumps(config, indent=2, default=str))

        cw_config = config.get('cloudWatchConfig', {})
        if cw_config.get('logGroupName'):
            print(f"\nCloudWatch log group: {cw_config['logGroupName']}")
            print(
                f"View logs: https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{cw_config['logGroupName'].replace('/', '$252F')}"
            )

        s3_config = config.get('s3Config', {})
        if s3_config.get('bucketName'):
            print(f"\nS3 bucket: {s3_config['bucketName']}")
            if s3_config.get('keyPrefix'):
                print(f"S3 prefix: {s3_config['keyPrefix']}")

    except ClientError as e:
        if 'AccessDenied' in str(e):
            print('Error: Access denied. Need bedrock:GetModelInvocationLoggingConfiguration permission.')
        else:
            print(f"Error: {e}")


def disable_logging(session: boto3.Session, region: str, force: bool, skip_prompts: bool = False) -> bool:
    """Disable Bedrock model invocation logging."""
    bedrock = session.client('bedrock', region_name=region)

    print('Checking current logging configuration...')
    config = get_current_config(bedrock)

    if not config:
        print('Logging is already disabled.')
        return True

    print('Current configuration:')
    print(json.dumps(config, indent=2, default=str))

    if not force and not skip_prompts:
        response = input('\nAre you sure you want to disable logging? (y/N): ')
        if response.lower() != 'y':
            print('Cancelled.')
            return False

    try:
        bedrock.delete_model_invocation_logging_configuration()
        print('\nSuccessfully disabled Bedrock model invocation logging.')
        return True
    except ClientError as e:
        if 'ResourceNotFoundException' in str(e):
            print('Logging was already disabled.')
            return True
        print(f"Error disabling logging: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Enable AWS Bedrock model invocation logging to CloudWatch')
    parser.add_argument(
        '--profile',
        '-p',
        help='AWS profile name to use',
        default=None,
    )
    parser.add_argument(
        '--region',
        '-r',
        help='AWS region (default: us-east-1)',
        default='us-east-1',
    )
    parser.add_argument(
        '--log-group',
        '-g',
        help=f"CloudWatch log group name (default: {DEFAULT_LOG_GROUP})",
        default=DEFAULT_LOG_GROUP,
    )
    parser.add_argument(
        '--retention',
        '-t',
        help='Log retention in days (default: 30)',
        type=int,
        default=30,
    )
    parser.add_argument(
        '--no-text',
        action='store_true',
        help='Disable logging of text input/output data',
    )
    parser.add_argument(
        '--no-image',
        action='store_true',
        help='Disable logging of image input/output data',
    )
    parser.add_argument(
        '--status',
        '-s',
        action='store_true',
        help='Show current logging status only',
    )
    parser.add_argument(
        '--disable',
        action='store_true',
        help='Disable model invocation logging',
    )
    parser.add_argument(
        '--force',
        '-f',
        action='store_true',
        help='Skip confirmation prompts',
    )
    parser.add_argument(
        '--role-name',
        help=f"IAM role name for Bedrock logging (default: {DEFAULT_ROLE_NAME})",
        default=DEFAULT_ROLE_NAME,
    )
    parser.add_argument(
        '--yes',
        '-y',
        action='store_true',
        help='Skip confirmation prompts (for non-interactive use)',
    )

    args = parser.parse_args()

    try:
        session_kwargs = {}
        if args.profile:
            session_kwargs['profile_name'] = args.profile
        session = boto3.Session(**session_kwargs)

        if args.status:
            show_status(session, args.region)
        elif args.disable:
            success = disable_logging(session, args.region, args.force, skip_prompts=args.yes)
            sys.exit(0 if success else 1)
        else:
            success = enable_logging(
                session=session,
                region=args.region,
                log_group_name=args.log_group,
                retention_days=args.retention,
                log_text=not args.no_text,
                log_image=not args.no_image,
                force=args.force,
                role_name=args.role_name,
                skip_prompts=args.yes,
            )
            sys.exit(0 if success else 1)

    except NoCredentialsError:
        print('Error: AWS credentials not found.')
        print('Configure credentials via:')
        print('  - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)')
        print('  - AWS credentials file (~/.aws/credentials)')
        print('  - IAM role (if running on AWS)')
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nCancelled.')
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
