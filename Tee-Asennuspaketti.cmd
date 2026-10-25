@echo off
rem ============================================================
rem TEE-ASENNUSPAKETTI - automaattinen rakennus + GitHub-julkaisu
rem Graafinen Web-Editori 4.0 (Jani Malmberg)
rem
rem Tuplaklikkaus = rakenna Asenna-WebEditori.exe, tallenna
rem muutokset GitHubiin ja julkaise uusi Release liitteineen.
rem ============================================================
title Graafinen Web-Editori - asennuspaketin rakennus
echo.
echo   Rakennetaan asennuspakettia ja julkaistaan GitHubiin...
echo   (PyInstaller-rakennus kestaa muutaman minuutin)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0WebEditori-Asennus\tee_asennuspaketti.ps1" %*
echo.
pause