@echo off
rem ================================================================
rem  LED FROM ANYWHERE  -  one-click demo  (ESP32 Wi-Fi version)
rem
rem  Before you double-click:
rem   1. The ESP32 is running arduino\ESP32_WiFi_LED_WebAPI
rem   2. ESP32_IP in web_esp32_led_control.py is the ESP32's address
rem
rem  Two windows open:
rem   Window 1 = the web remote (keep it open)
rem   Window 2 = ngrok, which shows your WORLD LINK
rem  To stop sharing: close both windows (or press Ctrl+C in each).
rem ================================================================
cd /d "%~dp0"

set "PY=..\venv\Scripts\python.exe"
if not exist "%PY%" (
  echo Python is not set up yet. Follow "First-time setup" in python\README.md.
  pause
  exit /b 1
)

rem Use ngrok from PATH if it is installed there, otherwise the copy in Downloads.
set "NGROK=ngrok"
where ngrok >nul 2>nul || set "NGROK=%USERPROFILE%\Downloads\04_TECHNOLOGY\Software\ngrok-v3-stable-windows-amd64\ngrok.exe"
if not "%NGROK%"=="ngrok" if not exist "%NGROK%" (
  echo ngrok was not found. Download it from https://ngrok.com/download
  echo and change the NGROK line in this file to where ngrok.exe is.
  pause
  exit /b 1
)

start "Window 1 - Web remote (keep open)" cmd /k ""%PY%" web_esp32_led_control.py"
timeout /t 3 >nul

echo.
echo  ============================================================
echo   Your WORLD LINK is the  https://....ngrok-free.dev  address
echo   on the "Forwarding" line below.
echo   1. Open it yourself first and press ON.
echo   2. Then share it with your friend or class.
echo   Press Ctrl+C here to stop sharing.
echo  ============================================================
echo.
"%NGROK%" http 5000
