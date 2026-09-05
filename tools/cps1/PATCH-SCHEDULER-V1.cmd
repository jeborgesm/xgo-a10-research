@echo off
setlocal
if "%~1"=="" (
  echo.
  echo XGO Scheduler V1
  echo.
  echo Drag your current mapper-v19 bios\bisrv.asd onto this CMD file.
  echo The input must have SHA-256:
  echo 466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab
  echo.
  pause
  exit /b 1
)

set "INPUT=%~f1"
set "OUTPUT=%~dp1bisrv.scheduler-v1.asd"
set "PATCHER=%~dp0patch_mapper_v19_stock_scheduler.py"

where py >nul 2>&1
if not errorlevel 1 (
  py -3 "%PATCHER%" "%INPUT%" "%OUTPUT%"
  goto done
)

where python >nul 2>&1
if not errorlevel 1 (
  python "%PATCHER%" "%INPUT%" "%OUTPUT%"
  goto done
)

echo.
echo ERROR: Python 3 was not found.
echo Run the patcher on a machine with Python 3 installed.
exit /b 1

:done
if errorlevel 1 (
  echo.
  echo Patch failed. Your original file was not changed.
  pause
  exit /b 1
)

echo.
echo Candidate created:
echo %OUTPUT%
echo.
echo Your original mapper-v19 firmware was not changed.
echo Follow README-SCHEDULER-V1.txt before copying the candidate to the test card.
pause
