$ErrorActionPreference = "Stop"

$ProjectDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython   = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$LauncherPath = Join-Path $ProjectDir "launcher.py"
$Shortcut     = Join-Path ([Environment]::GetFolderPath("Programs")) "Claude Control.lnk"

if (Test-Path $VenvPython) {
  & $VenvPython $LauncherPath --stop 2>$null
}

if (Test-Path $Shortcut) {
  Remove-Item $Shortcut -Force
  Write-Host "✓ Start Menu shortcut removed."
} else {
  Write-Host "  (No shortcut found — already uninstalled?)"
}

Write-Host "  To remove project files: Remove-Item -Recurse -Force `"$ProjectDir`""
