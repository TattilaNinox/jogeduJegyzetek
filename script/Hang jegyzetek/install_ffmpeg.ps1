# FFmpeg telepítő script Windows-ra
# Ez a script megpróbálja telepíteni az FFmpeg-et különböző módszerekkel

Write-Host "FFmpeg telepítési script" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# 1. Próbáljuk meg winget-tel
Write-Host "[1/3] Próbálkozás winget-tel..." -ForegroundColor Yellow
try {
    $wingetCheck = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetCheck) {
        Write-Host "Winget található, telepítés..." -ForegroundColor Green
        winget install --id=Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ FFmpeg sikeresen telepítve winget-tel!" -ForegroundColor Green
            exit 0
        }
    }
} catch {
    Write-Host "Winget nem elérhető vagy hiba történt." -ForegroundColor Red
}

# 2. Próbáljuk meg Chocolatey-vel
Write-Host ""
Write-Host "[2/3] Próbálkozás Chocolatey-vel..." -ForegroundColor Yellow
try {
    $chocoCheck = Get-Command choco -ErrorAction SilentlyContinue
    if ($chocoCheck) {
        Write-Host "Chocolatey található, telepítés..." -ForegroundColor Green
        choco install ffmpeg -y
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ FFmpeg sikeresen telepítve Chocolatey-vel!" -ForegroundColor Green
            exit 0
        }
    }
} catch {
    Write-Host "Chocolatey nem elérhető vagy hiba történt." -ForegroundColor Red
}

# 3. Manuális telepítési útmutató
Write-Host ""
Write-Host "[3/3] Manuális telepítési útmutató:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Az automatikus telepítés nem sikerült. Kérlek, telepítsd manuálisan:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Látogasd meg: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor Cyan
Write-Host "2. Töltsd le a 'ffmpeg-release-essentials.zip' fájlt" -ForegroundColor Cyan
Write-Host "3. Csomagold ki a ZIP fájlt" -ForegroundColor Cyan
Write-Host "4. Másold a 'bin' mappát valahová (pl. C:\ffmpeg)" -ForegroundColor Cyan
Write-Host "5. Add hozzá a PATH környezeti változóhoz:" -ForegroundColor Cyan
Write-Host "   - Nyisd meg: Rendszer -> Speciális rendszerbeállítások -> Környezeti változók" -ForegroundColor Cyan
Write-Host "   - Szerkeszd a PATH változót és add hozzá: C:\ffmpeg\bin" -ForegroundColor Cyan
Write-Host "6. Indíts újra a terminált" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vagy használd a Chocolatey-t (ha telepítve van):" -ForegroundColor Yellow
Write-Host "  choco install ffmpeg -y" -ForegroundColor White
Write-Host ""
Write-Host "Vagy használd a winget-et (Windows 10/11):" -ForegroundColor Yellow
Write-Host "  winget install --id=Gyan.FFmpeg -e" -ForegroundColor White
Write-Host ""




