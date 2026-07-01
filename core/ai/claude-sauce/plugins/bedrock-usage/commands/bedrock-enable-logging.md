---
description: Enable AWS Bedrock model invocation logging to CloudWatch for exact usage tracking
---
# Enable Bedrock Logging

This command enables Bedrock model invocation logging to CloudWatch Logs, which is required for exact cost tracking in the `/bedrock-usage` command. This is an **account-level** setting that applies to all users in the AWS account.

## Behavior
1. Detect the operating system and shell environment.
2. Execute the appropriate command based on the platform.
3. Capture stdout and stderr.
4. Display the output to the user verbatim.

## How to execute

Detect the platform from the environment information provided at the start of the conversation (Platform field), then use the appropriate command:
In case you are running on window platform, please use 'python' instead of 'python3' command to invoke the script.

### Command to Run
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/commands/scripts/bedrock_enable_logging.py" $ARGUMENTS
```

## Options
- `--status` - Show current logging status without making changes
- `--disable` - Disable model invocation logging
- `--log-group NAME` - CloudWatch log group name (default: /aws/bedrock/model-invocations)
- `--role-name NAME` - IAM role name for Bedrock logging (default: BedrockModelInvocationLoggingRole)
- `--retention N` - Log retention in days (default: 30)
- `--no-text` - Disable logging of text input/output
- `--no-image` - Disable logging of image input/output
- `--force` - Skip confirmation prompts
- `--profile NAME` - AWS profile to use
- `--region REGION` - AWS region (default: us-east-1)

## What it does
1. Creates an IAM role (if needed) with permissions for Bedrock to write to CloudWatch Logs
2. Creates the CloudWatch log group (if needed)
3. Sets log retention policy
4. Enables Bedrock model invocation logging

## Requirements
- Python 3.9+
- boto3 installed in the active environment
- AWS credentials configured
- IAM permissions:
  - `bedrock:GetModelInvocationLoggingConfiguration`
  - `bedrock:PutModelInvocationLoggingConfiguration`
  - `bedrock:DeleteModelInvocationLoggingConfiguration` (for --disable)
  - `iam:GetRole`
  - `iam:CreateRole`
  - `iam:PutRolePolicy`
  - `logs:CreateLogGroup`
  - `logs:PutRetentionPolicy`

## User output
Display the output to the user.
