# Bedrock Usage Plugin

Track and analyze AWS Bedrock Claude API usage with detailed metrics and logging capabilities.

## Overview

This plugin provides commands for:
- Fetching AWS Bedrock usage statistics (invocations, input/output tokens, costs)
- Enabling/checking CloudWatch Logs for Bedrock model invocations
- Analyzing usage patterns and identifying cost drivers
- Supporting multiple AWS regions and time ranges

## Prerequisites

| Requirement | Purpose | Setup |
|-------------|---------|-------|
| **AWS CLI** | AWS credential management | Pre-installed on most systems or `brew install awscli` |
| **AWS Credentials** | API authentication | `aws configure` |
| **IAM Permissions** | Bedrock + CloudWatch access | See permissions section below |
| **Python 3.7+** | Script execution | Pre-installed on most systems |

## Authentication/Setup

**IMPORTANT**: This plugin uses AWS credentials from your environment or AWS configuration files. It does **NOT** use `~/.claude-sauce.json`.

### Configure AWS Credentials

There are multiple ways to configure AWS credentials:

#### Option 1: AWS CLI Configuration (Recommended)

```bash
aws configure
```

This creates `~/.aws/credentials` with your access keys.

#### Option 2: Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### Option 3: AWS SSO

```bash
aws sso login --profile your-profile
```

Then use `--profile your-profile` with commands.

### Required IAM Permissions

Your AWS credentials need the following permissions:

**For usage tracking:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:GetUsageMetrics"
      ],
      "Resource": "*"
    }
  ]
}
```

**For logging (enable/check commands):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:GetModelInvocationLoggingConfiguration",
        "bedrock:PutModelInvocationLoggingConfiguration",
        "logs:CreateLogGroup",
        "logs:DescribeLogGroups",
        "logs:PutResourcePolicy",
        "logs:DescribeResourcePolicies",
        "iam:CreateRole",
        "iam:CreatePolicy",
        "iam:AttachRolePolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

For detailed AWS credential setup, see: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html

## Commands

### /bedrock-usage

Fetch and analyze AWS Bedrock usage statistics.

**Capabilities:**
- Retrieve usage for specific time ranges
- Filter by AWS region
- Analyze multiple regions in parallel
- Display invocation counts, token usage, and estimated costs
- Support for various time period shortcuts

**Common usage:**
```
/bedrock-usage                          # Last 7 days, all regions
/bedrock-usage --days 30                # Last 30 days
/bedrock-usage --region us-west-2       # Specific region
/bedrock-usage --start 2024-01-01 --end 2024-01-31  # Date range
```

**Time period shortcuts:**
- `--today`: Today's usage
- `--yesterday`: Yesterday's usage
- `--days N`: Last N days
- `--months N`: Last N months
- `--start DATE --end DATE`: Custom date range (YYYY-MM-DD)

**Region options:**
- `--region REGION`: Single region (e.g., us-east-1)
- `--all-regions`: Analyze all Bedrock-supported regions in parallel
- No region flag: Auto-detect from AWS config or use us-east-1

For detailed command documentation, see [commands/bedrock-usage.md](commands/bedrock-usage.md).

### /bedrock-enable-logging

Enable or check CloudWatch Logs for Bedrock model invocations.

**Capabilities:**
- Check current logging configuration
- Enable logging with automatic setup (log group, IAM role, resource policy)
- Configure logging for specific regions
- Verify logging is working correctly

**Common usage:**
```
/bedrock-enable-logging                 # Check status
/bedrock-enable-logging --enable        # Enable logging
/bedrock-enable-logging --region us-west-2 --enable  # Enable for specific region
```

**What gets created:**
- CloudWatch Log Group: `/aws/bedrock/modelinvocations`
- IAM Role: `AmazonBedrockLoggingRole-<region>`
- CloudWatch Resource Policy: `BedrockLoggingPolicy-<region>`

For detailed command documentation, see [commands/bedrock-enable-logging.md](commands/bedrock-enable-logging.md).

## Usage Patterns

### Checking Recent Usage

```
/bedrock-usage --days 7
```

Shows usage for the last week across all configured regions.

### Analyzing Specific Time Period

```
/bedrock-usage --start 2024-01-01 --end 2024-01-31
```

Analyzes usage for January 2024.

### Multi-Region Analysis

```
/bedrock-usage --all-regions
```

Analyzes usage across all AWS regions in parallel (faster than sequential).

### Setting Up Logging

```
1. Check current status:
   /bedrock-enable-logging

2. Enable if not configured:
   /bedrock-enable-logging --enable

3. Verify logs are being written:
   Check CloudWatch Logs console or use AWS CLI
```

### Cost Analysis

```
/bedrock-usage --days 30
```

Shows monthly usage with cost estimates based on current Bedrock pricing.

## Output Format

**Usage Report includes:**
- Time range analyzed
- AWS region(s) analyzed
- Total invocations
- Input tokens (with unit cost)
- Output tokens (with unit cost)
- Total estimated cost
- Model-level breakdown (if available)

**Logging Status includes:**
- Current configuration state (enabled/disabled)
- Log group name and settings
- IAM role ARN
- CloudWatch resource policy status

## Troubleshooting

### "Unable to locate credentials"

**Symptoms**: AWS SDK cannot find credentials

**Solutions**:
1. Run `aws configure` to set up credentials
2. Verify credentials file exists: `~/.aws/credentials`
3. Check environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
4. For SSO: run `aws sso login --profile your-profile`

### "Access Denied" / "UnauthorizedException"

**Symptoms**: Commands fail with permission errors

**Solutions**:
1. Verify IAM permissions (see Required IAM Permissions section)
2. Check your IAM user/role has `bedrock:GetUsageMetrics` permission
3. For logging: ensure `bedrock:PutModelInvocationLoggingConfiguration` permission
4. Contact AWS administrator to grant necessary permissions

### "Invalid region specified"

**Symptoms**: Region not recognized or Bedrock not available

**Solutions**:
1. Verify region name is correct (e.g., `us-east-1`, not `us-east1`)
2. Check Bedrock is available in that region
3. Use `--all-regions` to scan all supported regions
4. See AWS Bedrock documentation for region availability

### "No usage data found"

**Symptoms**: Usage report shows zero invocations

**Solutions**:
1. Verify date range has actual Bedrock usage
2. Check correct region is specified
3. Confirm API calls were made to Bedrock in that period
4. Try expanding time range (e.g., `--days 30` instead of `--today`)

### "Log group already exists"

**Symptoms**: Error when enabling logging

**Solutions**:
1. Logging may already be configured
2. Check status first: `/bedrock-enable-logging`
3. If partially configured, may need manual cleanup via AWS Console
4. Contact AWS administrator if log group was created by someone else

### Rate Limiting / Throttling

**Symptoms**: API calls fail with throttling errors

**Solutions**:
1. Reduce parallelism when using `--all-regions`
2. Add delays between requests
3. Check AWS service quotas for Bedrock API
4. Use smaller time ranges for usage queries

## Cost Estimation

Usage costs are estimated based on current AWS Bedrock pricing:
- Input tokens: $3.00 per 1M tokens (Claude 3 Opus)
- Output tokens: $15.00 per 1M tokens (Claude 3 Opus)

Prices vary by model. See AWS Bedrock pricing page for exact rates:
https://aws.amazon.com/bedrock/pricing/

## Plugin Details

**Name**: bedrock-usage
**Version**: 1.0.0
**Author**: <AUTHOR_NAME>

---

**Quick Start**: Run `/bedrock-usage` to see your recent AWS Bedrock usage!
