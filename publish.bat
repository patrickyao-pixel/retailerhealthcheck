@echo off
REM Double-click (or run "publish.bat my message") to commit and push all changes in this folder.
cd /d "%~dp0"
git ls-files --others --cached --exclude-standard | findstr /I /R "private config\.json \.xlsx$ \.csv$" >nul
if %errorlevel%==0 (
  echo.
  echo  STOP: a private / data file would be committed:
  git ls-files --others --cached --exclude-standard | findstr /I /R "private config\.json \.xlsx$ \.csv$"
  echo  Move it out of this folder or add it to .gitignore, then run again.
  pause
  exit /b 1
)
set MSG=%*
if "%MSG%"=="" set /p MSG=Commit message (e.g. v5.5 ticket groups): 
if "%MSG%"=="" set MSG=update
git pull --rebase
git add -A
git status --short
git commit -m "%MSG%"
git push
echo.
echo Done. GitHub Pages updates in about 1 minute.
pause
