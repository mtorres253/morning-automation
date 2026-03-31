#!/usr/bin/env python3
"""
Deployment script for AWS Lambda functions.
Packages functions with dependencies and creates them in AWS.
"""

import os
import json
import subprocess
import zipfile
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Configuration
AWS_REGION = 'us-west-2'
S3_BUCKET = 'michael-journal-entries'
GMAIL_EMAIL = 'mtorres253@gmail.com'
SES_EMAIL = 'mtorres253@gmail.com'
ROLE_ARN_PLACEHOLDER = 'arn:aws:iam::ACCOUNT_ID:role/lambda-morning-automation-role'

# Helper functions (must be defined before LAMBDA_FUNCTIONS)
def load_gmail_oauth():
    """Load Gmail OAuth credentials."""
    oauth_path = '/Users/michaeltorres/.openclaw/workspace/secrets/gmail_oauth.json'
    try:
        with open(oauth_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load Gmail OAuth: {e}")
        return {}

def load_job_search_config():
    """Load job search configuration."""
    config_path = '/Users/michaeltorres/.openclaw/workspace/skills/job-search/job-search-config.json'
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load job search config: {e}")
        return {}

# Lambda functions to deploy
LAMBDA_FUNCTIONS = [
    {
        'name': 'morning-journal-lambda',
        'handler': 'morning_journal_lambda.lambda_handler',
        'timeout': 3600,  # 1 hour for polling
        'memory': 512,
        'env_vars': {
            'GMAIL_EMAIL': GMAIL_EMAIL,
            'SES_EMAIL': SES_EMAIL,
            'S3_BUCKET': S3_BUCKET,
            'GMAIL_OAUTH_CONFIG': json.dumps(load_gmail_oauth()),
        }
    },
    {
        'name': 'job-search-lambda',
        'handler': 'job_search_lambda.lambda_handler',
        'timeout': 300,  # 5 minutes
        'memory': 256,
        'env_vars': {
            'GMAIL_EMAIL': GMAIL_EMAIL,
            'SES_EMAIL': SES_EMAIL,
            'JOB_SEARCH_SCRIPT': '/opt/job-search/run.py',
            'JOB_SEARCH_CONFIG': '/opt/job-search/config.json',
        }
    },
    {
        'name': 'gmail-digest-lambda',
        'handler': 'gmail_digest_lambda.lambda_handler',
        'timeout': 60,
        'memory': 256,
        'env_vars': {
            'GMAIL_EMAIL': GMAIL_EMAIL,
            'SES_EMAIL': SES_EMAIL,
            'GMAIL_OAUTH_CONFIG': json.dumps(load_gmail_oauth()),
        }
    }
]

# Required Python packages
REQUIRED_PACKAGES = [
    'requests',
    'google-auth',
    'google-auth-oauthlib',
    'google-auth-httplib2',
    'google-api-python-client',
    'boto3',
]

def check_aws_credentials():
    """Check if AWS credentials are configured."""
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            print(f"✓ AWS credentials found")
            print(f"  Account: {identity['Account']}")
            print(f"  ARN: {identity['Arn']}")
            return True
        else:
            print("✗ AWS credentials not configured")
            print("  Run: aws configure")
            return False
    except Exception as e:
        print(f"✗ Error checking AWS credentials: {e}")
        return False

def package_lambda(function_config, script_dir):
    """Package Lambda function with dependencies."""
    function_name = function_config['name']
    handler_file = function_config['handler'].split('.')[0]
    
    print(f"\n📦 Packaging {function_name}...")
    
    # Create build directory
    build_dir = Path(f'/tmp/lambda-{function_name}')
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)
    
    # Copy Lambda function code
    source_file = Path(script_dir) / f'{handler_file}.py'
    if not source_file.exists():
        print(f"  ✗ Source file not found: {source_file}")
        return None
    
    shutil.copy(source_file, build_dir / f'{handler_file}.py')
    print(f"  ✓ Copied {handler_file}.py")
    
    # Install dependencies
    deps_dir = build_dir / 'python'
    deps_dir.mkdir()
    
    for package in REQUIRED_PACKAGES:
        print(f"  → Installing {package}...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package, '-t', str(deps_dir), '-q'],
            capture_output=True
        )
        if result.returncode != 0:
            print(f"    ✗ Failed to install {package}")
    
    # Create zip file
    zip_path = f'/tmp/{function_name}.zip'
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add Python files
        for file in build_dir.glob('*.py'):
            zipf.write(file, file.name)
        
        # Add dependencies
        for root, dirs, files in os.walk(deps_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, build_dir)
                zipf.write(file_path, arcname)
    
    zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"  ✓ Created {function_name}.zip ({zip_size_mb:.1f} MB)")
    
    return zip_path

def get_role_arn():
    """Get the IAM role ARN from CloudFormation stack or hardcode it."""
    # Try to get from CloudFormation stack outputs
    try:
        result = subprocess.run(
            ['aws', 'cloudformation', 'describe-stacks', '--stack-name', 'michael-morning-automation'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            stack_data = json.loads(result.stdout)
            if 'Stacks' in stack_data and len(stack_data['Stacks']) > 0:
                stack = stack_data['Stacks'][0]
                if 'Outputs' in stack:
                    for output in stack['Outputs']:
                        if output['OutputKey'] == 'LambdaExecutionRoleArn':
                            return output['OutputValue']
    except Exception as e:
        print(f"Note: Could not retrieve role from CloudFormation: {e}")
    
    # Fallback: construct the ARN based on AWS account
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            account_id = identity['Account']
            return f'arn:aws:iam::{account_id}:role/lambda-morning-automation-role'
    except Exception as e:
        print(f"Note: Could not retrieve account ID: {e}")
    
    return None

def create_lambda_function(function_config, zip_path, role_arn):
    """Create or update Lambda function in AWS."""
    function_name = function_config['name']
    handler = function_config['handler']
    timeout = function_config['timeout']
    memory = function_config['memory']
    env_vars = function_config['env_vars']
    
    print(f"\n⚙️  Deploying {function_name} to AWS...")
    
    if not role_arn:
        print(f"  ✗ IAM role ARN not found")
        print(f"     Please run the setup steps in README.md to create the role first")
        return False
    
    # Read zip file
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    try:
        # Check if function exists
        check_result = subprocess.run(
            ['aws', 'lambda', 'get-function', '--function-name', function_name, '--region', AWS_REGION],
            capture_output=True
        )
        
        if check_result.returncode == 0:
            # Update existing function
            print(f"  → Updating existing function...")
            
            # Write zip to temp file
            temp_zip = f'/tmp/{function_name}_deploy.zip'
            with open(temp_zip, 'wb') as f:
                f.write(zip_content)
            
            result = subprocess.run([
                'aws', 'lambda', 'update-function-code',
                '--function-name', function_name,
                '--region', AWS_REGION,
                '--zip-file', f'fileb://{temp_zip}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ Code updated")
            else:
                print(f"  ✗ Failed to update code: {result.stderr}")
                return False
        else:
            # Create new function
            print(f"  → Creating new function...")
            
            # Write zip to temp file
            temp_zip = f'/tmp/{function_name}_deploy.zip'
            with open(temp_zip, 'wb') as f:
                f.write(zip_content)
            
            result = subprocess.run([
                'aws', 'lambda', 'create-function',
                '--function-name', function_name,
                '--runtime', 'python3.11',
                '--role', role_arn,
                '--handler', handler,
                '--timeout', str(timeout),
                '--memory-size', str(memory),
                '--region', AWS_REGION,
                '--zip-file', f'fileb://{temp_zip}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ Function created")
            else:
                print(f"  ✗ Failed to create function: {result.stderr}")
                return False
        
        # Update environment variables
        env_vars_json = json.dumps(env_vars)
        result = subprocess.run([
            'aws', 'lambda', 'update-function-configuration',
            '--function-name', function_name,
            '--region', AWS_REGION,
            '--environment', f'Variables={env_vars_json}'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ Environment variables updated")
        else:
            print(f"  ⚠ Warning: Could not update environment variables: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def create_eventbridge_rules():
    """Create EventBridge rules to trigger at 9 AM PT."""
    print(f"\n📅 Setting up EventBridge rules...")
    
    # 9 AM PT = 16:00 UTC (or 17:00 during daylight saving)
    # Using a cron expression that works year-round
    cron_expression = "cron(0 16 * * ? *)"  # 4 PM UTC (9 AM PT when not in DST)
    
    lambda_functions = [fn['name'] for fn in LAMBDA_FUNCTIONS]
    
    for function_name in lambda_functions:
        rule_name = f"{function_name}-rule"
        
        try:
            # Create or update the rule
            print(f"  → Setting up rule for {function_name}...")
            
            result = subprocess.run([
                'aws', 'events', 'put-rule',
                '--name', rule_name,
                '--schedule-expression', cron_expression,
                '--state', 'ENABLED',
                '--region', AWS_REGION
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"    ✓ EventBridge rule created/updated")
            else:
                print(f"    ✗ Failed to create rule: {result.stderr[:200]}")
                continue
            
            # Get Lambda ARN
            lambda_arn_result = subprocess.run([
                'aws', 'lambda', 'get-function',
                '--function-name', function_name,
                '--region', AWS_REGION,
                '--query', 'Configuration.FunctionArn',
                '--output', 'text'
            ], capture_output=True, text=True)
            
            if lambda_arn_result.returncode != 0:
                print(f"    ✗ Could not get Lambda ARN")
                continue
            
            lambda_arn = lambda_arn_result.stdout.strip()
            
            # Add Lambda as target
            result = subprocess.run([
                'aws', 'events', 'put-targets',
                '--rule', rule_name,
                '--targets', json.dumps([{
                    'Id': '1',
                    'Arn': lambda_arn,
                    'RoleArn': 'arn:aws:iam::ACCOUNT_ID:role/lambda-morning-automation-role'
                }]),
                '--region', AWS_REGION
            ], capture_output=True, text=True)
            
            if result.returncode == 0 or 'already exists' in result.stderr:
                print(f"    ✓ Lambda target added")
            else:
                print(f"    ⚠ Could not add target: {result.stderr[:200]}")
            
            # Grant EventBridge permission to invoke Lambda
            result = subprocess.run([
                'aws', 'lambda', 'add-permission',
                '--function-name', function_name,
                '--statement-id', f'AllowExecutionFromEventBridge-{rule_name}',
                '--action', 'lambda:InvokeFunction',
                '--principal', 'events.amazonaws.com',
                '--source-arn', f'arn:aws:events:{AWS_REGION}:ACCOUNT_ID:rule/{rule_name}',
                '--region', AWS_REGION
            ], capture_output=True, text=True)
            
            if result.returncode == 0 or 'ResourceConflictException' in result.stderr:
                print(f"    ✓ EventBridge invocation permission granted")
            else:
                print(f"    ⚠ Could not grant permission: {result.stderr[:200]}")
            
        except Exception as e:
            print(f"    ✗ Error: {e}")

def main():
    """Main deployment function."""
    print("=" * 60)
    print("AWS Lambda Deployment Script")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    if not check_aws_credentials():
        print("\n⚠️  Please configure AWS credentials and try again.")
        sys.exit(1)
    
    # Get script directory
    script_dir = Path(__file__).parent / 'lambda_functions'
    
    if not script_dir.exists():
        print(f"✗ Lambda functions directory not found: {script_dir}")
        sys.exit(1)
    
    print(f"✓ Found Lambda functions directory")
    
    # Get IAM role ARN
    print("\n🔐 Retrieving IAM role...")
    role_arn = get_role_arn()
    
    if not role_arn:
        print("⚠️  IAM role not found. Please follow the setup steps in README.md:")
        print("  1. Create the IAM role")
        print("  2. Attach the policy")
        print("  3. Try again")
        sys.exit(1)
    
    print(f"✓ Found IAM role: {role_arn}")
    
    # Package and deploy each function
    deployed = []
    for func_config in LAMBDA_FUNCTIONS:
        zip_path = package_lambda(func_config, script_dir)
        if not zip_path:
            print(f"✗ Failed to package {func_config['name']}")
            continue
        
        if create_lambda_function(func_config, zip_path, role_arn):
            deployed.append(func_config['name'])
    
    # Create EventBridge rules
    if deployed:
        create_eventbridge_rules()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Deployment Summary")
    print("=" * 60)
    print(f"✓ Deployed {len(deployed)} Lambda function(s):")
    for func_name in deployed:
        print(f"  - {func_name}")
    
    print(f"\nS3 Bucket: {S3_BUCKET}")
    print(f"Recipient Email: {GMAIL_EMAIL}")
    print(f"Region: {AWS_REGION}")
    
    print("\n📝 Next Steps:")
    print("  1. Test the Lambda functions:")
    print(f"     aws lambda invoke --function-name morning-journal-lambda --region {AWS_REGION} /tmp/response.json")
    print("  2. Check CloudWatch logs for errors")
    print("  3. Verify SES sandbox status (may need production access)")
    print("  4. Wait for 9 AM PT to see functions run automatically")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
