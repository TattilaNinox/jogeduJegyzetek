@echo off
chcp 65001 >nul
cd /d "%~dp0.."
python script\html_to_txt_converter.py
pause

