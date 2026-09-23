@echo off
cd /d "%~dp0"
python -m pip install Flask
python create_db.py
python app.py
pause
