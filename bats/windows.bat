@echo off

rem Create the virtual environment
python -m venv venv

rem Activate the virtual environment

start cmd /k "venv\Scripts\activate.bat && pip install -r requirements.txt && cd backend && python server.py"
