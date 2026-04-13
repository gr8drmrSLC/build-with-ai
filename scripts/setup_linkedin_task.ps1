# setup_linkedin_task.ps1
# Creates a Windows Task Scheduler task that posts to LinkedIn at 7am daily.
# Runs as soon as possible if the 7am window was missed (machine was offline).
#
# Run once from an elevated PowerShell prompt:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\scripts\setup_linkedin_task.ps1

$TaskName   = "LinkedInBuildWithAI"
$BatFile    = "C:\Users\V2Rst\build-with-ai\scripts\run_linkedin_post.bat"
$StartTime  = "07:00"

# Remove existing task if present
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task: $TaskName"
}

# Action: run the batch file
$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$BatFile`""

# Trigger: daily at 7am, starting tomorrow
$Trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At $StartTime

# Settings: run if missed, stop if already running, allow on battery
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -MultipleInstances IgnoreNew `
    -RunOnlyIfNetworkAvailable `
    -WakeToRun:$false

# Principal: run as current user
$Principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Highest

# Register the task
Register-ScheduledTask `
    -TaskName  $TaskName `
    -Action    $Action `
    -Trigger   $Trigger `
    -Settings  $Settings `
    -Principal $Principal `
    -Description "Posts next build-with-ai LinkedIn entry in order. Runs daily at 7am, catches up if machine was offline." `
    -Force

Write-Host ""
Write-Host "Task created: $TaskName"
Write-Host "  Schedule : Daily at $StartTime"
Write-Host "  Catch-up : Yes (StartWhenAvailable)"
Write-Host "  Network  : Required"
Write-Host ""
Write-Host "To verify:"
Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Select-Object *"
Write-Host ""
Write-Host "To run immediately:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "To remove:"
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
