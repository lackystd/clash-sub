@echo off
:: Silently update subscription
cd /d "%~dp0"
python "%~dp0jms2clash.py" --file "%~dp0subscription_url.txt" -o "%~dp0output\clash_config.txt" >nul 2>&1
:: Start HTTP server minimized (only serves output folder)
start /min cmd /c "cd /d "%~dp0output" && python -m http.server 18901"
