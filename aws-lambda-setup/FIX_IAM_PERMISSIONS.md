# Fix IAM Permissions — Complete Guide

## Problem

You're currently unable to debug or monitor Lambda functions because your IAM user (`michaels-laptop-lamdba-developer`) doesn't have the necessary permissions.

**Current errors:**
```
AccessDeniedException: User is not authorized to perform lambda:ListFunctions on resource: *
AccessDeniedException: User is not authorized to perform events:ListRules on resource: *
AccessDeniedException: User is not authorized to perform logs:GetLogEvents on resource: *
```

## Solution: Get Admin to Apply the IAM Policy

### Step 1: Identify Your AWS Admin

Who created the Lambda functions or has admin access to your AWS account?
- Is there an internal DevOps team?
- Did someone else set up the account?
- Do you have access to the AWS Organization?

### Step 2: Send Them This Policy Document

Share the file: `/Users/michaeltorres/.openclaw/workspace/aws-lambda-setup/IAM_POLICY_REQUEST.md`

Or copy-paste the policy below.

### Step 3: Admin Applies the Policy

**The admin should:**

1. Go to **AWS Console** → **IAM** → **Users**
2. Find user: `michaels-laptop-lamdba-developer`
3. Click **Add permissions** → **Create inline policy**
4. Choose **JSON** tab
5. Paste this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaReadAccess",
      "Effect": "Allow",
      "Action": [
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration",
        "lambda:ListFunctions",
        "lambda:Invoke",
        "lambda:GetFunctionCodeSigningConfig",
        "lambda:ListEventSourceMappings"
      ],
      "Resource": "*"
    },
    {
      "Sid": "EventBridgeReadAccess",
      "Effect": "Allow",
      "Action": [
        "events:DescribeRule",
        "events:ListRules",
        "events:ListTargetsByRule",
        "events:ListEventBuses"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchLogsReadAccess",
      "Effect": "Allow",
      "Action": [
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:GetLogEvents",
        "logs:FilterLogEvents"
      ],
      "Resource": "arn:aws:logs:us-west-2:682033478890:log-group:/aws/lambda/*"
    },
    {
      "Sid": "SESReadAccess",
      "Effect": "Allow",
      "Action": [
        "ses:GetAccountSendingEnabled",
        "ses:GetSendStatistics",
        "ses:ListIdentities",
        "ses:GetIdentityVerificationAttributes"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3ReadAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::michael-journal-entries",
        "arn:aws:s3:::michael-journal-entries/*"
      ]
    },
    {
      "Sid": "IAMReadAccess",
      "Effect": "Allow",
      "Action": [
        "iam:GetUser",
        "iam:ListAttachedUserPolicies",
        "iam:ListUserPolicies"
      ],
      "Resource": "arn:aws:iam::682033478890:user/michaels-laptop-lamdba-developer"
    }
  ]
}
```

6. Name the policy: `lambda-debugging-access`
7. Click **Create policy**

### Step 4: Verify It Works

Once the policy is applied, run these commands:

```bash
# Should now work (instead of AccessDenied)
aws lambda list-functions --region us-west-2

# Should show your user details
aws iam get-user

# Should show your attached policies
aws iam list-attached-user-policies --user-name michaels-laptop-lamdba-developer
```

## What This Policy Does

✅ **Allows:**
- List and describe Lambda functions
- Get Lambda function config and logs
- View EventBridge rules and targets
- Check CloudWatch logs
- View SES delivery status
- Read S3 journal bucket
- View your own IAM permissions

❌ **Does NOT allow:**
- Modify or delete Lambda functions
- Modify EventBridge rules
- Delete logs
- Send emails
- Create new resources

**Why these limits?**
- You can **debug and monitor**
- You **cannot accidentally break things**

## Troubleshooting

### Policy Applied But Still Getting AccessDenied

**Solution:**
1. Log out: `aws sso logout` or restart terminal
2. Reconfigure AWS: `aws configure`
3. Try again

### The Admin Can't Find the User

The user should exist at:
- **AWS Console** → **IAM** → **Users** → `michaels-laptop-lamdba-developer`
- **Account ID:** `682033478890` (from `aws sts get-caller-identity`)

### Still Not Working?

Ask the admin to verify:
1. Policy is attached to the correct user
2. No deny policies are blocking it
3. User's session is fresh (might need logout/login)

## Alternative: If Admin Can't Apply Policy

If the admin is unavailable, they can instead:

1. Run these commands on their machine (with admin credentials):
   ```bash
   # List Lambda functions
   aws lambda list-functions --region us-west-2
   
   # Describe EventBridge rules
   aws events list-rules --region us-west-2
   aws events list-targets-by-rule --rule job-search-lambda-rule --region us-west-2
   
   # Get Lambda logs
   aws logs tail /aws/lambda/job-search-lambda --region us-west-2 --since 7d
   aws logs tail /aws/lambda/gmail-digest-lambda --region us-west-2 --since 7d
   ```

2. Share the output with you

3. You can then manually debug based on the information

## Next: What to Check Once You Have Permissions

See: `LAMBDA_DEBUG_CHECKLIST.md`

---

**Created:** April 16, 2026  
**Account:** 682033478890  
**User:** michaels-laptop-lamdba-developer  
**Region:** us-west-2
