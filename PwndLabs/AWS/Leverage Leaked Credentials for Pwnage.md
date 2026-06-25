## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/leverage-leaked-credentials-for-pwnage

---
## Vulnerability Summary
The environment is vulnerable to **Information Disclosure** and **Credential Compromise** due to the exposure of configuration secrets in public-facing source code and 
insufficiently protected cloud-native secrets management.

1. **Hardcoded Secrets**: The application's `.env` file contained plain-text AWS Access 
   Keys and user credentials, which were inadvertently exposed in a Git repository.
2. **Account Enumeration**: By using `aws sts get-access-key-info`, an attacker 
   confirmed the AWS Account ID associated with the leaked access key, facilitating 
   direct navigation to the organization's AWS sign-in portal.
3. **Secrets Manager Misconfiguration**: Once authenticated, the attacker leveraged 
   excessive permissions to access the `AWS Secrets Manager` service. 
4. **Data Exfiltration**: The attacker successfully retrieved database credentials 
   for an `Amazon RDS` instance, allowing them to connect remotely and exfiltrate 
   sensitive data and application flags from the database.

---
## Walkthrough
Github repo: `https://github.com/huge-logistics/aws-react-app`

`.env` contains the username, password, and a AWS Access Key. Get Account ID:

```bash
aws sts get-access-key-info --access-key-id <Access_Key>
	Account: XXXXXXXXXX
```

Now we can login with the user we saw in the `.env`, the username and password. We can login with that at the url: `https://<Account_ID>.signin.aws.amazon.com/console`

`Secrets Manager > Secrets > employee-database > Retrieve Secret Value`

We can see username and password for `mariadb`! Login:

```bash
mysql -h employees.cwqkzlyzmm5z.us-east-1.rds.amazonaws.com -P 3306 -D employees -u reports -p
```

```sql
show databases;
show tables;
select * from employees;
select * from flag;
```

---
## Remediations
1. **Secret Scanning & Prevention**:
   - Use pre-commit hooks (e.g., `git-secrets` or `gitleaks`) to prevent developers 
     from committing `.env` files or credentials to repositories.
   - Immediately rotate any credentials discovered in source code.

2. **Secrets Management**:
   - Never store application credentials in plain-text configuration files. Utilize 
     `AWS Secrets Manager` or `AWS Systems Manager Parameter Store` for all 
     application secrets.
   - Implement IAM policies that restrict access to these secrets, ensuring only 
     the specific applications or roles that require them have the `GetSecretValue` permission.

3. **Database Security**:
   - Do not expose RDS instances to the public internet. Use private subnets 
     and restrict inbound access to the database via `Security Groups` limited 
     to the application's VPC/IP address.
   - Enforce strong database authentication and monitor for unusual query patterns 
     using `Database Activity Streams`.

4. **Monitoring**:
   - Enable `CloudTrail` to monitor for unauthorized `secretsmanager:GetSecretValue` 
     API calls, especially those originating from unexpected IAM users or 
     unauthorized IP ranges.
