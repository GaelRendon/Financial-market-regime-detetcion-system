@echo off
echo ========================================================
echo Launching Financial Market Regime Detection Dashboard...
echo ========================================================
call pvenv\Scripts\activate.bat
streamlit run app.py
pause
