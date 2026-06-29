---
name: security-review-standards
description: Security code review standards for all programming languages. Covers secrets management, injection flaws, authentication, authorization, supply chain security, sensitive data exposure, and IaC security. Use when performing security reviews or auditing code for vulnerabilities.
---
# Security Review

## Metadata

name: Security Review
description: Security vulnerability scanning and compliance checking for DevOps Portal services
version: 1.0.0

---

# /security-review

Invoke security analysis on changed files and infrastructure.

## Usage

```
/security-review              # Review all recent changes
/security-review lambda       # Focus on Lambda/handler security
/security-review terraform    # Focus on IaC security (IAM, encryption)
/security-review port         # Focus on Port API & authentication
/security-review secrets      # Focus on secret handling patterns
```

## Process

1. Identify security-relevant changes (auth, IAM, secrets, user input)
2. Run automated scans (secret detection, dependency audit)
3. Check AWS/Port security patterns
4. Apply project-specific security checks
5. Output findings with severity and fixes

## Automated Scans

Use the scripts in `scripts/` for automated security scanning:

```bash
# Run all security scans
./scripts/security-scan.sh all .

# Individual scans
./scripts/security-scan.sh secrets .    # Secret detection
./scripts/security-scan.sh iam .        # IAM permission audit
./scripts/security-scan.sh deps .       # Dependency vulnerabilities
./scripts/security-scan.sh terraform .  # Terraform security

# Scan specific directory
./scripts/security-scan.sh all ./campaign-self-service
```

### Available Scripts

| Script | Purpose |
|--------|---------|
| `security-scan.sh` | Orchestrator - runs all or specific scans |
| `detect-secrets.sh` | Scans for hardcoded credentials, API keys, tokens |
| `audit-iam.sh` | Checks IAM permissions in serverless.yml and Terraform |
| `audit-deps.sh` | Python (pip-audit) and Node.js (npm audit) vulnerabilities |
| `audit-terraform.sh` | Terraform security misconfigurations |

### Manual Checks

```bash
# Quick secret detection (manual)
grep -rn "AKIA\|sk-\|password\s*=\|api_key\s*=\|client_secret\s*=" \
  --include="*.py" --include="*.tf" --include="*.yml" .

# Python vulnerabilities (in service directory)
pip-audit

# Terraform security scan (requires tfsec)
tfsec terraform/
```

## Focus Areas

### 1. Port API Security

| Check | Severity | Pattern |
|-------|----------|---------|
| Hardcoded Port credentials | Critical | `PORT_CLIENT_ID`/`PORT_CLIENT_SECRET` in code |
| Token exposure in logs | High | `access_token` in logger calls |
| Missing authentication | High | API calls without `headers` parameter |
| Token not cached | Medium | Repeated `/auth/access_token` calls |

**Secure Pattern:**

```python
# SSM-based credential retrieval
def get_port_credentials():
    ssm = boto3.client('ssm')
    client_id = ssm.get_parameter(
        Name=f'{BASE_SSM_PATH}/port/client-id',
        WithDecryption=True
    )['Parameter']['Value']
    client_secret = ssm.get_parameter(
        Name=f'{BASE_SSM_PATH}/port/client-secret',
        WithDecryption=True
    )['Parameter']['Value']
    return client_id, client_secret
```

### 2. AWS IAM Security

| Check | Severity | Pattern |
|-------|----------|---------|
| Wildcard resources | High | `Resource: '*'` in IAM statements |
| Wildcard actions | Critical | `Action: '*'` in IAM statements |
| Missing encryption | Medium | S3 buckets without SSEAlgorithm |
| Overly broad managed policies | Medium | `AdministratorAccess` policy |

**Secure Pattern:**

```yaml
# serverless.yml - least privilege IAM
iam:
  role:
    statements:
      - Effect: 'Allow'
        Resource: 
          - ${ssm:/developer-portal/${opt:stage}/${self:service}/specific-arn}
        Action: 
          - 'ssm:GetParameter'
          - 'states:StartExecution'
```

```hcl
# Terraform - specific resource ARNs
resource "aws_iam_policy" "lambda_policy" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "${aws_s3_bucket.data.arn}/*"
    }]
  })
}
```

### 3. Lambda/Handler Security

| Check | Severity | Pattern |
|-------|----------|---------|
| Missing input validation | High | Direct use of `event` data without validation |
| PII in logs | High | Logging raw event payloads |
| Broad exception handling | Medium | Bare `except:` clauses |
| Secrets in environment | Medium | Secrets in `environment:` block instead of SSM |

**Secure Pattern:**

```python
@init_logger(app='service-name')
def main(event, context):
    logger = get_logger(__name__)
    # Sanitize before logging
    logger.add_invocation_data(event_type=event.get('source', 'unknown'))
    
    try:
        validated_input = validate_event(event)
        process(validated_input)
    except ValidationError as e:
        logger.warning("Invalid input: %s", e.message)  # Not full payload
        raise
    except SpecificError as e:
        logger.error("Operation failed: %s", str(e))
        raise
```

### 4. Terraform Port Provider Security

| Check | Severity | Pattern |
|-------|----------|---------|
| Hardcoded credentials | Critical | `client_id = "abc123"` in provider block |
| Missing permission restrictions | Medium | Blueprint without `port_blueprint_permissions` |
| Overly permissive actions | Medium | Actions with `roles = ["Member"]` for destructive ops |

**Secure Pattern:**

```hcl
provider "port" {
  client_id = var.port_client_id      # From tfvars (not committed)
  secret    = var.port_client_secret  # From tfvars (not committed)
}

# Restrict destructive operations to Admin
resource "port_blueprint_permissions" "secure" {
  entities = {
    unregister = {
      roles = ["Admin"]
      users = []
      teams = []
    }
  }
}
```

### 5. SSM & Secrets Management

| Check | Severity | Pattern |
|-------|----------|---------|
| Secrets in code | Critical | Inline API keys, passwords, tokens |
| Secrets in tfvars committed | Critical | `.tfvars` files with secrets in git |
| SSM without encryption | High | `ssm.get_parameter()` without `WithDecryption=True` |
| Secrets in logs | High | Logging SSM parameter values |

**Secure Pattern:**

```python
# SSM with decryption and no logging of values
def get_secret(param_name: str) -> str:
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name=param_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']  # Never log this
```

### 6. SQS Event Security

| Check | Severity | Pattern |
|-------|----------|---------|
| Missing event validation | High | No schema validation on SQS messages |
| Direct JSON parsing | Medium | `json.loads()` without error handling |
| No message filtering | Medium | Processing all messages without type check |

**Secure Pattern:**

```python
def process_sqs_event(event: dict) -> None:
    for record in event.get('Records', []):
        try:
            body = json.loads(record['body'])
            message = json.loads(body.get('Message', '{}'))
            
            # Validate expected structure
            if not validate_message_schema(message):
                logger.warning("Invalid message schema, skipping")
                continue
                
            # Filter by expected action type
            action_id = message.get('payload', {}).get('action', {}).get('identifier')
            if action_id not in ALLOWED_ACTIONS:
                logger.info("Skipping unhandled action: %s", action_id)
                continue
                
            process_message(message)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in SQS message")
            continue
```

## Security Checklist

### Pre-Commit

- [ ] No hardcoded secrets or credentials
- [ ] No PII or sensitive data in log statements
- [ ] Input validation on all event handlers
- [ ] Specific exception handling (no bare except)
- [ ] IAM policies follow least privilege

### Pre-Deploy (Terraform)

- [ ] S3 buckets have encryption enabled
- [ ] IAM roles have specific resource ARNs
- [ ] No wildcard actions on sensitive resources
- [ ] Port blueprint permissions are restrictive
- [ ] SSM parameters use SecureString type
- [ ] Lambda environment vars don't contain secrets

### Pre-Merge

- [ ] Dependency audit clean (`pip-audit`)
- [ ] No new secrets in diff
- [ ] Terraform plan reviewed for security changes
- [ ] Port action permissions reviewed

## Common Vulnerabilities in This Codebase

### 1. Exposed Port Credentials

```python
# BAD - Hardcoded credentials
credentials = {'clientId': 'abc123', 'clientSecret': 'secret456'}

# GOOD - From SSM
client = PortClient()  # Uses env vars which come from SSM
client.authenticate()
```

### 2. Overly Permissive Lambda IAM

```yaml
# BAD - Wildcard everything
statements:
  - Effect: 'Allow'
    Resource: '*'
    Action: '*'

# GOOD - Specific resources and actions
statements:
  - Effect: 'Allow'
    Resource: ${ssm:/path/to/specific/arn}
    Action: 'states:StartExecution'
```

### 3. Logging Sensitive Event Data

```python
# BAD - Full event exposure
logger.info(f"Received event: {event}")

# GOOD - Sanitized logging
logger.add_invocation_data(
    action=event.get('action_id'),
    run_id=event.get('run_id')
)
```

### 4. Missing Blueprint Permissions

```hcl
# BAD - No permissions defined
resource "port_blueprint" "my_blueprint" {
  identifier = "my_blueprint"
  # ... no permissions resource
}

# GOOD - Explicit permissions
resource "port_blueprint_permissions" "my_blueprint_permissions" {
  blueprint_identifier = port_blueprint.my_blueprint.identifier
  entities = {
    register   = { roles = ["Admin"], users = [], teams = [] }
    unregister = { roles = ["Admin"], users = [], teams = [] }
  }
}
```

## Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| Critical | Exposed secrets, credential leakage | Block merge, immediate fix |
| High | Missing auth, overly permissive IAM | Must fix before merge |
| Medium | Missing validation, broad exceptions | Should fix, can defer |
| Low | Best practice deviations | Nice to have |

## Pre-commit Hook

Install the security pre-commit hook to automatically check for secrets before each commit:

```bash
# Install hook in a repository
./scripts/install-hooks.sh /path/to/repo

# Or manually copy
cp scripts/pre-commit-security.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook blocks commits containing:
- AWS Access Keys
- Hardcoded passwords
- Private keys
- Port credentials
- GitHub tokens
- .env files
- Secrets in .tfvars

To bypass (not recommended): `git commit --no-verify`

## Related Rules

- `port.md` - Port.io standards and SDK usage
- Python coding standards for secure error handling
- Terraform standards for AWS security
