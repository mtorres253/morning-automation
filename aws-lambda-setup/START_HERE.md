# 🚀 START HERE

Welcome! Your AWS Lambda setup is ready to deploy.

---

## What You're Getting

Three automated email functions that run **every day at 9 AM PT**:

1. **Morning Journal** 📝  
   - Sends you a journal prompt
   - Waits 1 hour for your reply
   - Saves your journal entry to S3

2. **Job Search** 💼  
   - Runs your job search
   - Finds interesting roles
   - Sends results via email

3. **Gmail Digest** 📧  
   - Summarizes your emails from the last 24 hours
   - Sends you a daily digest

**Cost:** ~$0.35/month (dirt cheap!)

---

## The Fastest Way (5 minutes)

### Step 1: Prerequisites
```bash
aws --version                    # Make sure AWS CLI is installed
aws configure                    # Configure your AWS credentials
aws sts get-caller-identity      # Verify it worked
```

### Step 2: Deploy
```bash
cd /Users/michaeltorres/.openclaw/workspace/aws-lambda-setup
python3 deploy.py
```

Done! Your functions are now running on AWS.

### Step 3: Verify
```bash
# Check if functions exist
aws lambda list-functions --region us-west-2

# View logs
aws logs tail /aws/lambda/morning-journal-lambda --follow --region us-west-2
```

---

## The Detailed Way (30 minutes)

**Not confident with automation?** Follow the step-by-step guide:

→ [QUICK_START.md](QUICK_START.md)

It walks you through each AWS resource creation manually.

---

## Need Help?

| Question | Answer |
|----------|--------|
| "How do I deploy?" | Run `python3 deploy.py` or see [QUICK_START.md](QUICK_START.md) |
| "What gets created?" | See [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) |
| "How does it work?" | See [ARCHITECTURE.md](ARCHITECTURE.md) with diagrams |
| "Something broke" | See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| "Complete guide" | See [README.md](README.md) |
| "Step-by-step checklist" | See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) |

**Navigation hub:** [INDEX.md](INDEX.md)

---

## What's in This Directory

```
aws-lambda-setup/
├── START_HERE.md                ← You are here
├── INDEX.md                     ← Navigation
├── QUICK_START.md               ← 7-step setup (pick this!)
├── deploy.py                    ← Run this to deploy
│
├── lambda_functions/            ← Lambda function code
│   ├── morning_journal_lambda.py
│   ├── job_search_lambda.py
│   └── gmail_digest_lambda.py
│
├── Detailed Docs/ (if you want more reading)
│   ├── README.md
│   ├── DEPLOYMENT_SUMMARY.md
│   ├── ARCHITECTURE.md
│   ├── TROUBLESHOOTING.md
│   └── DEPLOYMENT_CHECKLIST.md
```

---

## Quick Reference

### Deploy (Automatic)
```bash
python3 deploy.py
```

### Deploy (Manual Step-by-Step)
```bash
# See QUICK_START.md - 7 clear steps
```

### Test a Function
```bash
aws lambda invoke \
  --function-name morning-journal-lambda \
  --region us-west-2 \
  /tmp/test.json

cat /tmp/test.json
```

### Check Logs
```bash
aws logs tail /aws/lambda/morning-journal-lambda --follow --region us-west-2
```

### Check Function Status
```bash
aws lambda get-function-configuration \
  --function-name morning-journal-lambda \
  --region us-west-2
```

### List All Functions
```bash
aws lambda list-functions --region us-west-2
```

---

## After Deployment

### What to Expect

1. **At 9 AM PT every day:**
   - You'll receive 1-3 emails
   - Journal prompt, job results, and email digest
   - All sent to mtorres253@gmail.com

2. **For the Journal:**
   - You get the prompt email
   - Reply with your journal entry
   - Function polls for 1 hour for your reply
   - Entry stored in S3 when found

3. **For Job Search:**
   - Results sent automatically
   - Based on your job-search-config.json

4. **For Gmail Digest:**
   - Summary of last 24 hours of emails
   - Sent in the morning along with other emails

### Verify It's Working

1. **Check CloudWatch logs** (real-time)
   ```bash
   aws logs tail /aws/lambda/morning-journal-lambda --follow
   ```

2. **Check S3 bucket** (journal storage)
   ```bash
   aws s3 ls s3://michael-journal-entries --recursive
   ```

3. **Check EventBridge rule** (scheduler)
   ```bash
   aws events describe-rule --name morning-automation-rule --region us-west-2
   ```

4. **Wait for 9 AM PT** 🕘  
   Check your email inbox!

---

## Most Common Issues

### "AWS credentials not found"
```bash
aws configure
# Enter your AWS Access Key, Secret Key, region (us-west-2), output (json)
```

### "Emails not arriving"
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) Section 2 (SES)  
Often just need to request SES production access.

### "Gmail API errors"
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) Section 3  
Check that refresh_token is valid.

### "Lambda timeout"
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) Section 4  
Increase timeout with:
```bash
aws lambda update-function-configuration \
  --function-name morning-journal-lambda \
  --timeout 3600 \
  --region us-west-2
```

---

## Success Checklist

You're done when:

- [ ] AWS credentials configured
- [ ] `python3 deploy.py` completed successfully
- [ ] 3 Lambda functions exist in AWS
- [ ] S3 bucket "michael-journal-entries" created
- [ ] EventBridge rule "morning-automation-rule" created
- [ ] Manual test returns StatusCode 200
- [ ] CloudWatch logs show no errors
- [ ] You get emails at 9 AM PT

---

## Next Steps

### NOW (Right now!)
👉 Run: `python3 deploy.py`

### TODAY
- Verify functions exist
- Test with manual invokes
- Check logs for errors

### TOMORROW
- Wait for 9 AM PT
- Check email inbox
- Enjoy your automated morning routine!

---

## Questions?

1. **"How do I...?"** → See [INDEX.md](INDEX.md) for navigation
2. **"Something's broken"** → See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **"Tell me more"** → See [README.md](README.md)
4. **"Show me how"** → See [QUICK_START.md](QUICK_START.md)

---

## The Simple Truth

This takes **5 minutes to deploy** with one command:

```bash
python3 deploy.py
```

That's it. Everything else is optional reading.

---

**Ready?** Let's go:

```bash
cd /Users/michaeltorres/.openclaw/workspace/aws-lambda-setup
python3 deploy.py
```

Good luck! 🚀

---

*Created: 2026-03-28*  
*For: Michael Torres*  
*Status: Ready to deploy*
