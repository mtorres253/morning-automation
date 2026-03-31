# AWS Lambda Setup - Complete Index

Welcome! This directory contains everything needed to set up three Lambda functions that automate your morning routine.

---

## 📚 Documentation

### Quick Reference
- **[QUICK_START.md](QUICK_START.md)** - 7-step setup (5 minutes)
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Step-by-step checklist

### Complete Guides
- **[README.md](README.md)** - Full setup with detailed explanations
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - What was created, costs, next steps
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and fixes

---

## 🛠 Deployment Tools

### Recommended: Automated Deploy
```bash
python3 deploy.py
```
**File:** [deploy.py](deploy.py)  
**Time:** 5-10 minutes  
**What it does:** Packages functions, uploads to AWS, creates EventBridge rules

### Alternative: CloudFormation
```bash
aws cloudformation create-stack \
  --stack-name morning-automation \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-west-2
```
**File:** [cloudformation.yaml](cloudformation.yaml)  
**Time:** 2 minutes  
**What it does:** Infrastructure-as-code deployment

### Manual: AWS Console
See [README.md](README.md) for step-by-step AWS console instructions

---

## 📦 Lambda Function Code

Located in `lambda_functions/` directory:

1. **[morning_journal_lambda.py](lambda_functions/morning_journal_lambda.py)**
   - Sends journal prompt email
   - Polls Gmail for responses (1 hour)
   - Stores journal to S3
   - **Runs:** 9 AM PT daily

2. **[job_search_lambda.py](lambda_functions/job_search_lambda.py)**
   - Runs job search script
   - Formats results
   - Sends email
   - **Runs:** 9 AM PT daily

3. **[gmail_digest_lambda.py](lambda_functions/gmail_digest_lambda.py)**
   - Fetches emails from last 24h
   - Creates summary
   - Sends digest email
   - **Runs:** 9 AM PT daily

---

## 📋 Getting Started

### Path A: I Want Quick Setup (5 min)
1. Read: [QUICK_START.md](QUICK_START.md)
2. Follow: 7 steps in terminal
3. Test: Verify functions work

### Path B: I Want Step-by-Step (30 min)
1. Read: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
2. Complete: Each checkbox
3. Verify: Each step

### Path C: I Want Full Details (60 min)
1. Read: [README.md](README.md)
2. Understand: Each component
3. Customize: As needed

### Path D: I Have Problems
1. Check: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Find: Your error
3. Apply: Solution

---

## 🎯 What You'll Deploy

### 3 Lambda Functions
- **morning-journal-lambda** (3600s timeout, 512 MB)
- **job-search-lambda** (300s timeout, 256 MB)
- **gmail-digest-lambda** (60s timeout, 256 MB)

### AWS Infrastructure
- **S3 Bucket:** `michael-journal-entries`
- **IAM Role:** `lambda-morning-automation-role`
- **EventBridge Rule:** `morning-automation-rule` (9 AM PT daily)

### Total Cost
Approximately **$0.35/month** (with free SES tier)

---

## ⚡ Quick Commands

```bash
# Deploy everything
python3 deploy.py

# Test a function
aws lambda invoke --function-name morning-journal-lambda --region us-west-2 /tmp/response.json

# View logs
aws logs tail /aws/lambda/morning-journal-lambda --follow --region us-west-2

# List all functions
aws lambda list-functions --region us-west-2 --query 'Functions[].FunctionName'

# Check EventBridge rule
aws events describe-rule --name morning-automation-rule --region us-west-2
```

---

## 📊 File Structure

```
aws-lambda-setup/
├── INDEX.md                        ← You are here
├── QUICK_START.md                  ← Start here for speed
├── DEPLOYMENT_CHECKLIST.md         ← Use this to verify each step
├── README.md                       ← Full documentation
├── DEPLOYMENT_SUMMARY.md           ← What was created
├── TROUBLESHOOTING.md              ← Common issues
│
├── deploy.py                       ← Run this to deploy
├── cloudformation.yaml             ← Alternative deployment
├── requirements.txt                ← Python dependencies
│
└── lambda_functions/
    ├── morning_journal_lambda.py   ← Journal function code
    ├── job_search_lambda.py        ← Job search function code
    └── gmail_digest_lambda.py      ← Gmail digest function code
```

---

## ✅ Prerequisites

Before starting, ensure you have:

- [ ] AWS account (with us-west-2 access)
- [ ] AWS CLI installed: `pip install awscli`
- [ ] AWS credentials configured: `aws configure`
- [ ] Gmail OAuth token at: `/Users/michaeltorres/.openclaw/workspace/secrets/gmail_oauth.json`
- [ ] Job search config at: `/Users/michaeltorres/.openclaw/workspace/skills/job-search/job-search-config.json`

Verify with:
```bash
aws sts get-caller-identity
```

---

## 🚀 Next Steps

### Immediate (Right Now)
1. Choose your path (A, B, C, or D above)
2. Follow the guide
3. Run the deployment

### After Deployment (Today)
1. Verify all tests pass
2. Check CloudWatch logs
3. Confirm emails arrive

### Ongoing (Every Day)
1. Functions run automatically at 9 AM PT
2. Check S3 for journal entries
3. Monitor CloudWatch logs occasionally

---

## 🆘 Getting Help

**Stuck?** Check in this order:

1. **QUICK_START.md** - Most common setup
2. **TROUBLESHOOTING.md** - Your specific error
3. **README.md** - Detailed explanations
4. **CloudWatch logs** - Function errors: `aws logs tail /aws/lambda/{name} --follow`

---

## 📞 Support Resources

- **AWS Documentation:** https://docs.aws.amazon.com/lambda/
- **AWS Support Console:** https://console.aws.amazon.com/support/
- **CloudWatch Logs:** View function execution logs
- **EventBridge Console:** Monitor scheduled executions

---

## 💡 Tips

1. **Test before scheduling:** Run `python3 deploy.py` and test each function
2. **Monitor logs:** Keep CloudWatch Logs console open while testing
3. **Check SES status:** Verify email is in production (not sandbox)
4. **Start simple:** Deploy and test before making customizations
5. **Keep credentials safe:** Don't commit OAuth tokens to git

---

## 📝 Files You May Edit

To customize, edit:
- `lambda_functions/morning_journal_lambda.py` - Change journal prompt
- `lambda_functions/job_search_lambda.py` - Change job search behavior
- `lambda_functions/gmail_digest_lambda.py` - Change digest format
- `cloudformation.yaml` - Change resource names/sizes

Then redeploy:
```bash
python3 deploy.py
```

---

## Version History

- **v1.0** (2026-03-28) - Initial release
  - 3 Lambda functions
  - EventBridge scheduling
  - S3 storage
  - SES email integration
  - Gmail OAuth integration

---

## License & Attribution

Created for Michael Torres  
AWS Lambda setup  
2026-03-28

---

## 🎉 You're Ready!

Pick a path above and get started. Most people finish in 30 minutes.

**Questions?** Check the docs.  
**Stuck?** See TROUBLESHOOTING.md.  
**Ready to deploy?** Run `python3 deploy.py`.

Good luck! 🚀
