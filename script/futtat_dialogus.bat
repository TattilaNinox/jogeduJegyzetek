@echo off
chcp 65001 >nul
cd /d "%~dp0"
if "%~1"=="" (
    echo Hasznalat: futtat_dialogus.bat "Tetelek\A_temakor_neve"
    echo.
    echo Pelda: futtat_dialogus.bat "Tetelek\A_specialis_karfelelossegi_alakzatok"
    exit /b 1
)
python script\dialogus_generator_natural.py "%~1"
pause














