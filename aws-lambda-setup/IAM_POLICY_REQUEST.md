# IAM Policy Request for Lambda Debugging

**User:** `michaels-laptop-lamdba-developer`  
**Account:** `682033478890`  
**Date:** April 16, 2026

## Problem

The current IAM user has extremely restricted permissions. We need read/debug access to:
- Lambda functions (list, get config, invoke, view logs)
- EventBridge rules (list, describe, view targets)
- CloudWatch logs (view Lambda execution logs)

## Requested Policy

Attach the following policy to the user `michaels-laptop-lamdba-developer` to enable debugging and monitoring:

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
        "ses:GetIdentityVerificationAttributes",
        "ses:ListConfigurationSets"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3ReadAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket",
        "s3:GetBucketVersioning"
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
        "iam:GetRole",
        "iam:ListAttachedUserPolicies",
        "iam:ListUserPolicies",
        "iam:GetUserPolicy"
      ],
      "Resource": [
        "arn:aws:iam::682033478890:user/michaels-laptop-lamdba-developer",
        "arn:aws:iam::682033478890:role/*"
      ]
    }
  ]
}
```

## How to Apply (AWS Admin)

1. Go to **AWS Console** → **IAM** → **Users**
2. Select `michaels-laptop-lamdba-developer`
3. Click **Add permissions** → **Attach policies**
4. Click **Create inline policy**
5. Paste the JSON above
6. Name it: `lambda-debugging-read-access`
7. Click **Create policy**

## What This Enables

✅ View Lambda function configuration and execution logs  
✅ List and describe EventBridge rules  
✅ Check CloudWatch logs for errors  
✅ View SES email delivery status  
✅ Read S3 journal bucket  
✅ View your own IAM permissions  

## What This Does NOT Enable

❌ Modify Lambda functions (create, update, delete)  
❌ Modify EventBridge rules  
❌ Delete CloudWatch logs  
❌ Send emails via SES (existing Lambda functions already have this)  

---

## Alternative: Quick Test (Without Policy Changes)

If the admin isn't available, we can work around this by:
1. Having the admin manually invoke the Lambda functions and share the results
2. Testing locally with the same code
3. Checking if emails arrived in your inbox (proof it's working)

Let me know once the policy is attached!
