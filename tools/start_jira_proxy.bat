@echo off
cd /d "%~dp0"
title Jira proxy - Retailer Data Health Monitor
python jira_proxy.py %*
if errorlevel 1 py jira_proxy.py %*
pause
