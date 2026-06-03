---
title: Tombwatcher HTB Write-Up
machine_ip: 10.10.11.72
os: Windows
difficulty: Medium
my_rating: 5
tags:
  - writeup
references: 
date: 2025-06-07
---
## 🌐 Enumeration

- `DC01.tombwatcher.htb`
- kerberoast using `henry / H3nry_987TGV!`
- get `alfred / basketball`
	- must sync time with `rdate`
- ENUMERATE WITH NXC OR BLOODHOUND FOR PATH TO DC compromise
	- I used nxc and did not use bloodhound, Need to enumerate with bloodhound to really visualize the steps to compromise
- ADCS
![[Pasted image 20250608172355.png]]
- Certipy - adcs
	- Find misconfigurations and list Certificate Templates
![[Pasted image 20250608191141.png]]
- find machine `ansible_dev$`
![[Pasted image 20250608193922.png]]
- enumerate groups
![[Pasted image 20250608194016.png]]
## 🗝️ Initial Access

- Modify AD Group Memberships - Add `alfred` to Infrastructure group
- Abuse Infrastructure group permissions - do `nxc` again for gmsa passwords
![[Pasted image 20250608194837.png]]
- got NTLM hash for `ansible_dev$`
	- `1c37d00093dc2a5f25176bf2d474afdc`
	- can't crack or pass the hash
- Use `ansible_dev$` to Reset User Sam Password to `giggles`
![[Pasted image 20250608195353.png]]
- Exploit ACL on John via Sam
![[Pasted image 20250608195546.png]]
- Reset John's password now owned by Sam
	- Error message said i had to wait for 3 hours...


## ⚡ Privilege Escalation




![[Pasted image 20250608195745.png]]