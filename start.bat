@echo off
echo ============================================================
echo  AUTONOMOUS EMAIL CHECKER - QUICK START
echo ============================================================
echo.

REM Check Python
echo [1/5] Checking Python...
D:\ai-email-checker\.venv\Scripts\python.exe --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python virtual environment not found
    echo Run: python -m venv .venv
    pause
    exit /b 1
)
echo OK - Python virtual environment found
echo.

REM Check Docker
echo [2/5] Checking Docker services...
docker-compose ps
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker Compose not working
    echo Make sure Docker Desktop is running
    pause
    exit /b 1
)
echo.

REM Check Ollama
echo [3/5] Checking Ollama...
curl -s http://localhost:11434 > nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Ollama not responding on port 11434
    echo Start it with: docker-compose up -d ollama
) else (
    echo OK - Ollama is running
)
echo.

REM Install dependencies
echo [4/5] Checking dependencies...
D:\ai-email-checker\.venv\Scripts\python.exe -c "import telegram" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing dependencies...
    D:\ai-email-checker\.venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    echo OK - Dependencies installed
)
echo.

REM Start autonomous system
echo [5/5] Starting autonomous system...
echo.
echo ============================================================
echo  SYSTEM READY!
echo ============================================================
echo.
echo Telegram Bot: @hackingmasterr
echo Admin ID: 796354588
echo.
echo Commands:
echo   /auto_scan - Start autonomous processing
echo   /ml_status - Check ML learning metrics
echo   /quality_report - Quality validation stats
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.

D:\ai-email-checker\.venv\Scripts\python.exe start_autonomous.py

pause
