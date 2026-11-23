@echo off
setlocal
echo =======================================================
echo    NexusPilot Fleet Multi-Agent MCP Installer
echo =======================================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install-fleet.ps1" %*
echo.
pause
