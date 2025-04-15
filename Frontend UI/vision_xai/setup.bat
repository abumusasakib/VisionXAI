@echo off

:: Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed.
    echo Please install Node.js from https://nodejs.org and re-run this script.
    exit /b 1
)

:: Run the Node.js script
echo Node.js is installed. Running setup script...
node setup.js
