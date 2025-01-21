@echo off

:: Define supported Python versions in one place for easier maintenance
set VERSIONS=python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python

:: Try each version in order
for %%v in (%VERSIONS%) do (
    where /q %%v && %%v src && goto :EOF
)

:: If we get here, no Python version worked
echo No supported Python version (3.8-3.13) was found on your system.
echo.
echo To install Python:
echo 1. Open the Microsoft Store
echo 2. Search for "Python"
echo 3. Choose Python 3.11 or newer
echo 4. Click "Get" or "Install"
echo.
echo Alternatively, you can download Python from:
echo https://www.python.org/downloads/
echo.
pause
exit /b 1