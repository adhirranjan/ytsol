@echo off
setlocal enabledelayedexpansion

REM ===================================================================
REM  Push local files to YouTube_Solutions folder on GitHub (ytsol repo)
REM  Run this .bat file from inside the folder with your files,
REM  OR just double-click it and it will use its own folder location.
REM ===================================================================

cd /d "%~dp0"

echo.
echo === Step 1: Checking git repo status ===
if not exist ".git" (
    echo No git repo found here. Initializing...
    git init
) else (
    echo Git repo already initialized.
)

echo.
echo === Step 2: Setting up remote 'origin' ===
git remote get-url origin >nul 2>&1
if %errorlevel%==0 (
    echo Remote 'origin' already set. Updating URL just in case...
    git remote set-url origin https://github.com/adhirranjan/ytsol.git
) else (
    echo Adding remote 'origin'...
    git remote add origin https://github.com/adhirranjan/ytsol.git
)

echo.
echo === Step 3: Pulling latest content from GitHub ===
git pull origin main --allow-unrelated-histories
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Pull failed or had conflicts. Please resolve manually before continuing.
    pause
    exit /b 1
)

echo.
echo === Step 4: Reminder ===
echo All changed and new files in this folder will be staged and pushed.
echo Make sure everything is ready before continuing.
pause

echo.
echo === Step 5: Staging all changed files ===
git add -A

echo.
set /p commitmsg="Enter a commit message (or press Enter for default): "
if "%commitmsg%"=="" set commitmsg=Add new files to YouTube_Solutions

git commit -m "%commitmsg%"
if %errorlevel% neq 0 (
    echo.
    echo Nothing to commit, or commit failed. Skipping push.
    pause
    exit /b 0
)

echo.
echo === Step 6: Checking branch name ===
for /f "tokens=*" %%b in ('git branch --show-current') do set currentbranch=%%b
echo Current branch: %currentbranch%

if not "%currentbranch%"=="main" (
    echo Renaming branch "%currentbranch%" to "main"...
    git branch -M main
)

echo.
echo === Step 7: Pushing to GitHub ===
echo When prompted, enter your GitHub username and your Personal Access Token
echo (paste the token in place of the password).
echo.
git push -u origin main

echo.
echo ===================================================================
echo  Done! Check https://github.com/adhirranjan/ytsol/tree/main/YouTube_Solutions
echo ===================================================================
pause
