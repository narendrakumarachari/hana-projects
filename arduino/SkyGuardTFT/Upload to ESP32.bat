@echo off
rem Double-click to compile Sky Guard and upload it to the ESP32.
rem Finds the ESP32 by its USB chip (CH340), so the port never has to be picked by hand.
rem Close the Serial Monitor in the Arduino IDE first.

set CLI="C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe"

for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "$d = Get-PnpDevice -Class Ports -PresentOnly | Where-Object { $_.FriendlyName -match 'CH340|CP210|USB-SERIAL' } | Select-Object -First 1; if ($d) { [regex]::Match($d.FriendlyName, 'COM\d+').Value }"`) do set PORT=%%P

if "%PORT%"=="" (
  echo Could not find the ESP32. Check the USB cable and try again.
  pause
  exit /b 1
)

echo Found the ESP32 on %PORT%. Uploading Sky Guard...
%CLI% compile --fqbn esp32:esp32:esp32 --libraries "%~dp0..\libraries" --upload -p %PORT% "%~dp0."
if errorlevel 1 (
  echo.
  echo Upload FAILED. See the messages above.
) else (
  echo.
  echo Upload finished! The game is starting on the ESP32.
)
pause
