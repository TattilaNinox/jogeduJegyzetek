@echo off
REM FFmpeg telepítő script Windows-ra
echo FFmpeg telepítési script
echo ========================
echo.

REM 1. Próbáljuk meg winget-tel
echo [1/3] Próbálkozás winget-tel...
where winget >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Winget található, telepítés...
    winget install --id=Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    if %ERRORLEVEL% == 0 (
        echo ✓ FFmpeg sikeresen telepítve winget-tel!
        pause
        exit /b 0
    )
) else (
    echo Winget nem elérhető.
)

REM 2. Próbáljuk meg Chocolatey-vel
echo.
echo [2/3] Próbálkozás Chocolatey-vel...
where choco >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Chocolatey található, telepítés...
    choco install ffmpeg -y
    if %ERRORLEVEL% == 0 (
        echo ✓ FFmpeg sikeresen telepítve Chocolatey-vel!
        pause
        exit /b 0
    )
) else (
    echo Chocolatey nem elérhető.
)

REM 3. Manuális telepítési útmutató
echo.
echo [3/3] Manuális telepítési útmutató:
echo.
echo Az automatikus telepítés nem sikerült. Kérlek, telepítsd manuálisan:
echo.
echo 1. Látogasd meg: https://www.gyan.dev/ffmpeg/builds/
echo 2. Töltsd le a 'ffmpeg-release-essentials.zip' fájlt
echo 3. Csomagold ki a ZIP fájlt
echo 4. Másold a 'bin' mappát valahová (pl. C:\ffmpeg)
echo 5. Add hozzá a PATH környezeti változóhoz:
echo    - Nyisd meg: Rendszer -^> Speciális rendszerbeállítások -^> Környezeti változók
echo    - Szerkeszd a PATH változót és add hozzá: C:\ffmpeg\bin
echo 6. Indíts újra a terminált
echo.
echo Vagy használd a Chocolatey-t (ha telepítve van):
echo   choco install ffmpeg -y
echo.
echo Vagy használd a winget-et (Windows 10/11):
echo   winget install --id=Gyan.FFmpeg -e
echo.
pause























