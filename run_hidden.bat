@echo off
REM Run NameDaysApp with virtual environment activated (hidden window)
cd /d "C:\Munka\2026\AiWorkFlows\WorkFlow-NameDaysPy"
call .venv\Scripts\activate.bat
python main.py
exit /b