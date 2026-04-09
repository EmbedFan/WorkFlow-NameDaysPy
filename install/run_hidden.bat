@echo off
REM Run NameDaysApp with virtual environment activated (hidden window)
call .venv\Scripts\activate.bat
python main.py
exit /b