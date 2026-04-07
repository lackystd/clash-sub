@echo off
:: Silently update subscription
python "%~dp0jms2clash.py" --file "%~dp0subscription_url.txt" -o "%~dp0clash_config.txt" >nul 2>&1
:: Start HTTP server minimized
start /min python -m http.server 18901 --directory "%~dp0"
