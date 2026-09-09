<#
.SYNOPSIS
  Installs the Wazuh agent + registers with the manager. Designed to be
  packaged as an Intune Win32 app - see docs/04-windows-endpoints §4.7.

.NOTES
  STATUS: Requires change control in production (fleet rollout).
  Always assign to a pilot device group before widening scope.
#>

param(
    [string]$WazuhManagerIP = "<WAZUH_MANAGER_IP>",
    [string]$MsiUrl = "https://packages.wazuh.com/4.x/windows/wazuh-agent-4.9.0-1.msi"
)

$ErrorActionPreference = "Stop"
$msiPath = Join-Path $env:TEMP "wazuh-agent.msi"

Write-Output "Downloading Wazuh agent installer..."
Invoke-WebRequest -Uri $MsiUrl -OutFile $msiPath -UseBasicParsing

Write-Output "Installing Wazuh agent (manager: $WazuhManagerIP)..."
Start-Process msiexec.exe -ArgumentList @(
    "/i", $msiPath,
    "/q",
    "WAZUH_MANAGER=$WazuhManagerIP",
    "WAZUH_REGISTRATION_SERVER=$WazuhManagerIP"
) -Wait

Write-Output "Starting WazuhSvc..."
Start-Service -Name WazuhSvc

# Detection-rule anchor for Intune: confirm the service exists and is running
$svc = Get-Service -Name WazuhSvc -ErrorAction SilentlyContinue
if ($null -eq $svc -or $svc.Status -ne "Running") {
    Write-Error "WazuhSvc did not start successfully."
    exit 1
}

Write-Output "Wazuh agent installed and running."
exit 0
