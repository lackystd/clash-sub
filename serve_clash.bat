@echo off
echo ========================================
echo   Clash Config Local Server
echo ========================================
echo.
echo Serving: clash_config.txt
echo Subscription URL:
echo.
echo   http://127.0.0.1:18901/clash_config.txt
echo.
echo Paste this URL into Clash Verge subscription.
echo Press Ctrl+C to stop the server.
echo ========================================
echo.
python -m http.server 18901 --directory "%~dp0"
