# Gmail Digest Debug — In Progress

## Current Status

**Gmail Digest Lambda is running but producing NO output.**

### Evidence

CloudWatch logs show:
```
2026-04-16T16:00:28.461Z START RequestId: 6c40cfec-386b-4053-b39a-8752023fe593
2026-04-16T16:00:30.019Z END RequestId: 6c40cfec-386b-4053-b39a-8752023fe593
Duration: 1458.06 ms
```

**The problem:** No output between START and END
- No "Starting Gmail Digest Lambda"
- No "Fetching emails"
- No error messages
- Silent crash/exit

### Root Cause (Suspected)

**Lambda is deployed in WRONG REGION**

The logs show:
```
arn:aws:lambda:us-east-2::runtime:...
```

But it should be in `us-west-2`.

This causes:
- SES client hardcoded to us-west-2 but Lambda is in us-east-2
- Possible region mismatch error
- Function crashes silently before printing anything

### Next Steps (When You Return)

1. **Check Lambda region in AWS Console**
   - Go to Lambda → gmail-digest-lambda
   - What region is shown in top right?
   - Is it us-east-2 (WRONG) or us-west-2 (CORRECT)?

2. **Check if duplicate Lambda exists**
   - Is there a gmail-digest-lambda in us-east-2?
   - Is there one in us-west-2?
   - If both exist, we need to:
     - Delete the us-east-2 one
     - Or update EventBridge rule to point to us-west-2 one

3. **If it's in us-east-2:**
   - Either redeploy to us-west-2
   - Or update the Lambda code to use us-east-2 for SES

### Files to Check

- `aws-lambda-setup/lambda_functions/gmail_digest_lambda.py` — hardcoded to us-west-2
- EventBridge rule `morning-automation-rule` — check which gmail-digest-lambda it targets

### Quick Fix Options

**Option A: Update Lambda region in code**
```python
# Line 13
ses_client = boto3.client('ses', region_name='us-east-2')  # Change from us-west-2
```
Then redeploy.

**Option B: Delete Lambda in us-east-2, keep us-west-2 one**
- Delete: gmail-digest-lambda (us-east-2)
- Keep: gmail-digest-lambda (us-west-2)
- Update: EventBridge rule to point to us-west-2 version

**Option C: Redeploy everything to us-west-2**
- Run `python3 deploy.py` with correct region settings

---

**Status:** Waiting on region check  
**Time to fix:** 5-15 minutes once identified  
**Severity:** Medium (job search works, just gmail digest broken)
