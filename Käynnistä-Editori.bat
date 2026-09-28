@echo off
rem Kaynnistaa graafisen web-editorin
cd /d "%~dp0"
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw editori.py
) else (
    start "" python editori.py
)