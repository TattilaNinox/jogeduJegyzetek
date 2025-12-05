@echo off
REM Jogeset Generátor API indítása Windows-on

echo ========================================
echo JOGESET GENERATOR API INDITASA
echo ========================================
echo.

REM Ellenőrizzük, hogy van-e virtual environment
if exist "..\..\.venv\Scripts\activate.bat" (
    echo Virtual environment aktiválása...
    call ..\..\.venv\Scripts\activate.bat
) else (
    echo Figyelem: Nincs virtual environment találva.
    echo A rendszer Python-t használja.
)

REM Függőségek telepítése (ha szükséges)
echo.
echo Függőségek ellenőrzése...
pip install -q -r requirements.txt

REM API indítása
echo.
echo API indítása...
echo.
python jogeset_api.py

pause

