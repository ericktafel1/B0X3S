---
title: Catch HTB Write-Up
machine_ip:
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
PORT     STATE SERVICE REASON         VERSION
22/tcp   open  ssh     syn-ack ttl 63 OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 48:ad:d5:b8:3a:9f:bc:be:f7:e8:20:1e:f6:bf:de:ae (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC82vTuN1hMqiqUfN+Lwih4g8rSJjaMjDQdhfdT8vEQ67urtQIyPszlNtkCDn6MNcBfibD/7Zz4r8lr1iNe/Afk6LJqTt3OWewzS2a1TpCrEbvoileYAl/Feya5PfbZ8mv77+MWEA+kT0pAw1xW9bpkhYCGkJQm9OYdcsEEg1i+kQ/ng3+GaFrGJjxqYaW1LXyXN1f7j9xG2f27rKEZoRO/9HOH9Y+5ru184QQXjW/ir+lEJ7xTwQA5U1GOW1m/AgpHIfI5j9aDfT/r4QMe+au+2yPotnOGBBJBz3ef+fQzj/Cq7OGRR96ZBfJ3i00B/Waw/RI19qd7+ybNXF/gBzptEYXujySQZSu92Dwi23itxJBolE6hpQ2uYVA8VBlF0KXESt3ZJVWSAsU3oguNCXtY7krjqPe6BZRy+lrbeska1bIGPZrqLEgptpKhz14UaOcH9/vpMYFdSKr24aMXvZBDK1GJg50yihZx8I9I367z0my8E89+TnjGFY2QTzxmbmU=
|   256 b7:89:6c:0b:20:ed:49:b2:c1:86:7c:29:92:74:1c:1f (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBH2y17GUe6keBxOcBGNkWsliFwTRwUtQB3NXEhTAFLziGDfCgBV7B9Hp6GQMPGQXqMk7nnveA8vUz0D7ug5n04A=
|   256 18:cd:9d:08:a6:21:a8:b8:b6:f7:9f:8d:40:51:54:fb (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKfXa+OM5/utlol5mJajysEsV4zb/L0BJ1lKxMPadPvR
80/tcp   open  http    syn-ack ttl 63 Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Catch Global Systems
|_http-server-header: Apache/2.4.41 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
3000/tcp open  http    Golang net/http server
| fingerprint-strings: 
|   GenericLines, Help, RTSPRequest: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.0 200 OK
|     Content-Type: text/html; charset=UTF-8
|     Set-Cookie: i_like_gitea=91400e2912341eee; Path=/; HttpOnly
|     Set-Cookie: _csrf=mF9BjhKPl8yf4ihGZ49uBfD4gAA6MTc4NjQ4Nzg1MDk2MDExNzE0MQ; Path=/; Expires=Wed, 12 Aug 2026 22:37:30 GMT; HttpOnly; SameSite=Lax
|     Set-Cookie: macaron_flash=; Path=/; Max-Age=0; HttpOnly
|     X-Frame-Options: SAMEORIGIN
|     Date: Tue, 11 Aug 2026 22:37:31 GMT
|     <!DOCTYPE html>
|     <html lang="en-US" class="theme-">
|     <head data-suburl="">
|     <meta charset="utf-8">
|     <meta name="viewport" content="width=device-width, initial-scale=1">
|     <meta http-equiv="x-ua-compatible" content="ie=edge">
|     <title> Catch Repositories </title>
|     <link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiQ2F0Y2ggUmVwb3NpdG9yaWVzIiwic2hvcnRfbmFtZSI6IkNhdGNoIFJlcG9zaXRvcmllcyIsInN0YXJ0X3VybCI6Imh0dHA6Ly9naXRlYS5jYXRjaC5odGI6MzAwMC8iLCJpY29ucyI6W3sic3JjIjoiaHR0cDovL2dpdGVhLmNhdGNoLmh0Yjoz
|   HTTPOptions: 
|     HTTP/1.0 405 Method Not Allowed
|     Set-Cookie: i_like_gitea=acc7964ba895c393; Path=/; HttpOnly
|     Set-Cookie: _csrf=5uXIPyW4oMlnTfT732iuq-xcWr86MTc4NjQ4Nzg1MjIxNjAwODczOA; Path=/; Expires=Wed, 12 Aug 2026 22:37:32 GMT; HttpOnly; SameSite=Lax
|     Set-Cookie: macaron_flash=; Path=/; Max-Age=0; HttpOnly
|     X-Frame-Options: SAMEORIGIN
|     Date: Tue, 11 Aug 2026 22:37:32 GMT
|_    Content-Length: 0
|_http-title:  Catch Repositories 
5000/tcp open  upnp?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Help, RPCCheck, RTSPRequest, SMBProgNeg, ZendJavaBridge: 
|     HTTP/1.1 400 Bad Request
|     Connection: close
|   GetRequest: 
|     HTTP/1.1 302 Found
|     X-Frame-Options: SAMEORIGIN
|     X-Download-Options: noopen
|     X-Content-Type-Options: nosniff
|     X-XSS-Protection: 1; mode=block
|     Content-Security-Policy: 
|     X-Content-Security-Policy: 
|     X-WebKit-CSP: 
|     X-UA-Compatible: IE=Edge,chrome=1
|     Location: /login
|     Vary: Accept, Accept-Encoding
|     Content-Type: text/plain; charset=utf-8
|     Content-Length: 28
|     Set-Cookie: connect.sid=s%3AA0ypTkK15Ym4SS420vNEPAuGhCDK_wcw.dciF0f4C9XvC20fxY7U5hPMWe7JyS4%2BSua0sPy2Cq%2BQ; Path=/; HttpOnly
|     Date: Tue, 11 Aug 2026 22:37:35 GMT
|     Connection: close
|     Found. Redirecting to /login
|   HTTPOptions: 
|     HTTP/1.1 200 OK
|     X-Frame-Options: SAMEORIGIN
|     X-Download-Options: noopen
|     X-Content-Type-Options: nosniff
|     X-XSS-Protection: 1; mode=block
|     Content-Security-Policy: 
|     X-Content-Security-Policy: 
|     X-WebKit-CSP: 
|     X-UA-Compatible: IE=Edge,chrome=1
|     Allow: GET,HEAD
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 8
|     ETag: W/"8-ZRAf8oNBS3Bjb/SU2GYZCmbtmXg"
|     Set-Cookie: connect.sid=s%3A4Xc_phauP7PW3VZzWFN7u6JlWAdJSPqJ.7CkAU9qI%2BYquD8W1B7WuMFHZhyhLN8lCIH6t6fPc4nE; Path=/; HttpOnly
|     Vary: Accept-Encoding
|     Date: Tue, 11 Aug 2026 22:37:39 GMT
|     Connection: close
|_    GET,HEAD
8000/tcp open  http    syn-ack ttl 62 Apache httpd 2.4.29 ((Ubuntu))
|_http-favicon: Unknown favicon MD5: 69A0E6A171C4ED8855408ED902951594
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Catch Global Systems
```

4 web servers: 1 is Catch Global Systems company page, 1 is a log of reported incidents (none), 1 is Let' Chat, last 1 is Gitea

Download button downloads `catchv1.0.apk`. Static analysis using `jadx-gui` and `mobsf` we find a subdomain (`status.catch.htb`) and hardcoded creds:
```bash
Slack token: xoxp-23984754863-2348975623103  
"gitea_token" : "b87bfb6345ae72ed5ecdcee05bcb34c83806fbd0"  
"lets_chat_token" : "NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ=="  
"slack_token" : "xoxp-23984754863-2348975623103"
```

```bash
echo "NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ==" | base64 -d
61b86aead984e2451036eb16:d588468ff8bae446379a57fa2b4e63a2368224336b5949c5
```

Enumerate port 8000 `status.catch.htb`
```bash
200      GET        1l       17w      799c http://status.catch.htb:8000/dist/js/manifest.js
200      GET        7l       44w     2670c http://status.catch.htb:8000/img/apple-touch-icon.png
200      GET       10l       69w     6229c http://status.catch.htb:8000/img/apple-touch-icon-120x120.png
200      GET        7l       44w     2670c http://status.catch.htb:8000/img/apple-touch-icon-57x57.png
200      GET        4l       24w     1588c http://status.catch.htb:8000/img/favicon.ico
200      GET       24l      121w     8717c http://status.catch.htb:8000/img/apple-touch-icon-114x114.png
200      GET       12l       44w     3550c http://status.catch.htb:8000/img/apple-touch-icon-72x72.png
200      GET       26l      157w    13486c http://status.catch.htb:8000/img/apple-touch-icon-152x152.png
302      GET       12l       22w      402c http://status.catch.htb:8000/dashboard => http://status.catch.htb:8000/auth/login
200      GET       31l      267w    11027c http://status.catch.htb:8000/img/favicon.png
200      GET       23l      159w    11766c http://status.catch.htb:8000/img/apple-touch-icon-144x144.png
200      GET       16l     1226w    79044c http://status.catch.htb:8000/dist/css/app.css
200      GET        1l      335w     8385c http://status.catch.htb:8000/dist/js/app.f266b3ff7582a248cf69.js
200      GET        1l       32w     1498c http://status.catch.htb:8000/dist/js/manifest.d41d8cd98f00b204e980.js
200      GET        6l     1594w    83381c http://status.catch.htb:8000/dist/js/vendor.885771e7cd571e4e1560.js
200      GET       19l    11816w   917300c http://status.catch.htb:8000/dist/js/all.js
200      GET        1l     5929w   540895c http://status.catch.htb:8000/dist/js/vendor.js
200      GET      301l      647w     8950c http://status.catch.htb:8000/
200      GET       11l       53w   180550c http://status.catch.htb:8000/dist/css/app.feac6a0c1283b11117bc898e9697488a.css
200      GET        1l     2986w   277026c http://status.catch.htb:8000/dist/js/app.js
200      GET        6l     3356w   992898c http://status.catch.htb:8000/dist/js/all.f3cedfb63b877d38010a6c79318e4f04.js
200      GET        6l      370w    82502c http://status.catch.htb:8000/dist/js/vendor.de6049da06819ff051e8.js
200      GET      301l      647w     8980c http://status.catch.htb:8000/index.php
200      GET        1l      304w   992893c http://status.catch.htb:8000/dist/js/all.adba40a4e1e695e94ba548e63c912d99.js
200      GET        6l     3400w   983546c http://status.catch.htb:8000/dist/js/all.933ef52c701c02556f3b7fa32b0d5f5d.js
200      GET        5l     2469w   766040c http://status.catch.htb:8000/dist/js/all.4083e75c2ea0d0e7c624e3519d24eb35.js
200      GET        6l       20w     1633c http://status.catch.htb:8000/img/favicon-high-alert.ico
200      GET       24l      113w     8774c http://status.catch.htb:8000/img/favicon-high-alert.png
200      GET       10l       45w     3599c http://status.catch.htb:8000/img/button-email--dark-grey.png
200      GET       10l       57w     4026c http://status.catch.htb:8000/img/apple-touch-icon-76x76.png
200      GET       21l       77w     4321c http://status.catch.htb:8000/img/cachet-logo.png
200      GET       25l      133w     8540c http://status.catch.htb:8000/img/cachet-logo@2x.png
200      GET        1l      515w     7240c http://status.catch.htb:8000/img/cachet-logo.svg
200      GET       19l      200w     8759c http://status.catch.htb:8000/img/cachet-icon.png
200      GET        5l       18w     1658c http://status.catch.htb:8000/img/favicon-medium-alert.ico
200      GET       24l      127w     9006c http://status.catch.htb:8000/img/favicon-medium-alert.png
200      GET       86l      194w     4236c http://status.catch.htb:8000/auth/login
302      GET       12l       22w      402c http://status.catch.htb:8000/admin => http://status.catch.htb:8000/auth/login
```

Port 3000 (Gitea v1.14.1):
```bash
200      GET        1l      214w     2119c http://status.catch.htb:3000/img/logo.svg
200      GET       13l       62w      803c http://status.catch.htb:3000/api/swagger
302      GET        2l        2w       37c http://status.catch.htb:3000/explore/ => http://status.catch.htb:3000/explore/repos
302      GET        2l        2w       27c http://status.catch.htb:3000/img => http://status.catch.htb:3000/img
200      GET       47l      313w    25954c http://status.catch.htb:3000/img/logo.png
200      GET        9l       27w     4351c http://status.catch.htb:3000/img/favicon.png
200      GET       12l       45w      912c http://status.catch.htb:3000/explore/repos
200      GET       12l       46w      912c http://status.catch.htb:3000/user/login
200      GET       21l      124w   110007c http://status.catch.htb:3000/js/licenses.txt
200      GET        1l       19w   865085c http://status.catch.htb:3000/css/index.css
200      GET        1l       20w   995775c http://status.catch.htb:3000/js/index.js
200      GET      245l     1018w    12125c http://status.catch.htb:3000/
302      GET        2l        2w       34c http://status.catch.htb:3000/admin => http://status.catch.htb:3000/user/login
302      GET        2l        2w       27c http://status.catch.htb:3000/css => http://status.catch.htb:3000/css
302      GET        2l        2w       30c http://status.catch.htb:3000/vendor => http://status.catch.htb:3000/vendor
200      GET      301l     1199w    13787c http://status.catch.htb:3000/root
```
- `/root` leads to `/string` which we are not authorized to view...

Port 5000 (Let's Chat):
```bash
200      GET      297l      345w    27845c http://status.catch.htb:5000/media/favicon.ico
200      GET      386l     1672w    13255c http://status.catch.htb:5000/media/dist/login-7837de7d77c06a887aa8ac155b65ffe5.js
200      GET     4947l     9639w    97025c http://status.catch.htb:5000/media/dist/style-8dc8edf892836803f025c4197997ae41.css
200      GET     7129l    15320w   142950c http://status.catch.htb:5000/media/dist/vendor-f5a60d1bd9e76696f088fa97a53737f1.css
200      GET     1099l     6551w   554646c http://status.catch.htb:5000/media/img/photos/lake.jpg
200      GET    17060l    62109w  1274461c http://status.catch.htb:5000/media/dist/vendor-5b9a2bb2f19551857f2c0020dc2e7795.js
200      GET       56l      147w     2621c http://status.catch.htb:5000/login
401      GET        1l        1w       12c http://status.catch.htb:5000/account

```

## 🗝️ Initial Access



## ⚡ Privilege Escalation