@echo off
chcp 65001 >nul
cd /d "%~dp0.."
python script\tetelek_html_generator.py
pause

















