@echo off
echo 🧪 YouTube Course Generator - Quick Test
echo ========================================
echo.

if "%1"=="" (
    echo Usage: test_url.bat "PLAYLIST_URL" [MAX_VIDEOS]
    echo.
    echo Examples:
    echo   test_url.bat "https://www.youtube.com/playlist?list=PLxxxxx"
    echo   test_url.bat "https://www.youtube.com/playlist?list=PLxxxxx" 5
    echo.
    echo Or run without parameters for interactive mode:
    echo   test_url.bat
    echo.
    choice /c YN /m "Run in interactive mode"
    if errorlevel 2 goto :end
    python test_custom_url.py
    goto :end
)

set MAX_VIDEOS=%2
if "%MAX_VIDEOS%"=="" set MAX_VIDEOS=10

echo Testing with:
echo   URL: %1
echo   Max Videos: %MAX_VIDEOS%
echo.

python yt_agent.py %1 %MAX_VIDEOS%

:end
pause
