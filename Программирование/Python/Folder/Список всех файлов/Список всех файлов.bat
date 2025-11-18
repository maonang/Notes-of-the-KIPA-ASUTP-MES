@echo off
setlocal disabledelayedexpansion

chcp 65001 >nul
set "root=%cd%"

>list.txt (
    for /f "delims=" %%i in ('dir /b /s /a-d 2^>nul') do (
        set "file=%%i"
        setlocal enabledelayedexpansion
        set "relative=!file:%root%=!"
        if "!relative:~0,1!"=="\" set "relative=!relative:~1!"
        echo(!relative!
        endlocal
    )
)

endlocal
