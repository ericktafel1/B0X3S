
## Proof.txt Linux 1
```
whoami && hostname && ip a && cat proof.txt
```

## Proof.txt Linux 2
```
whoami && hostname && ifconfig && cat proof.txt
```

## Proof.txt Windows
```
whoami && hostname && ipconfig && type proof.txt
```


Windows
- CMD
```c
for /r C:\ %f in (proof.txt local.txt) do @echo Found: %f & type "%f"

for /r C:\ %%f in (proof.txt local.txt) do @echo Found: %%f & type "%%f"
```
- PS
 ```PowerShell
gci C:\ -Include proof.txt,local.txt -Recurse -ea SilentlyContinue | % { echo "Found: $($`_`.FullName)"; cat $`_`.FullName }
 ```             
- Possible locations:
	- C:\Users\<username>\Desktop\proof.txt
	- C:\Users\Administrator\Desktop\proof.txt
	- C:\Windows\Temp\proof.txt
	- C:\Temp\proof.txt
	- C:\ProgramData\proof.txt
	- C:\Users\Public\proof.txt
---
# Linux      
```bash
sudo find / -type f ( -name "proof.txt" -o -name "local.txt" ) 2>/dev/null -exec cat {} ;
```            
- OR
```bash                
#!/bin/bash

echo "[*] Searching for local.txt and proof.txt..."
sudo find / -type f \( -name "proof.txt" -o -name "local.txt" \) 2>/dev/null | while read -r file; do
echo "[+] Found: $file"
sudo cat "$file"
echo
done
```
- Possible locations:
	- /root/proof.txt
	- /tmp/proof.txt
	- /var/tmp/proof.txt
	- /home/<username>/proof.txt