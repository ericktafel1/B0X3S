https://pwnedlabs.io/labs/identify-the-aws-account-id-from-a-public-s3-bucket

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

![[Pasted image 20260603114432.png]]
Bonus:
To list public snapshots, supply owner ID and region:
```bash
aws ec2 describe-snapshots --owner-ids 107513503799 --region us-east-1
```
