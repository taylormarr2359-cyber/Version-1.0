@echo off
REM run_atlas.cmd — Launch ATLAS CLI on Windows (Command Prompt)
REM Usage: scripts\run_atlas.cmd

setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

if exist "%PROJECT_ROOT%\.venv\Scripts\activate.bat" (
    call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
) else (
    echo WARNING: .venv not found -- using system Python.
    echo Run: python -m venv .venv ^&^& pip install -e .
)

cd /d "%PROJECT_ROOT%"
python -m projrvt.main

endlocal
