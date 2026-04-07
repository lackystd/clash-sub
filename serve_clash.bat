@echo off
echo ========================================
echo   Clash Config Local Server
echo ========================================
echo.
echo Serving: output/clash_config.txt
echo.
echo   http://127.0.0.1:18901/clash_config.txt
echo.
echo Paste this URL into Clash Verge subscription.
echo Press Ctrl+C to stop the server.
echo ========================================
echo.
cd /d "%~dp0output"
python -m http.server 18901
