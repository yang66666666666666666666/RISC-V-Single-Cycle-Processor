@echo off
REM Windows batch script to create and run RISC-V processor project in Vivado
REM Make sure Vivado is installed and in your PATH

echo ========================================
echo RISC-V Single Cycle Processor Setup
echo ========================================
echo.

REM Check if Vivado is available
where vivado >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Vivado not found in PATH
    echo Please make sure Vivado is installed and added to your system PATH
    echo Typical Vivado installation path: C:\Xilinx\Vivado\2024.1\bin
    echo.
    echo You can also run Vivado manually and source the create_vivado_project.tcl script
    pause
    exit /b 1
)

echo Creating Vivado project...
vivado -mode batch -source create_vivado_project.tcl

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Project created successfully!
    echo.
    echo To open the project:
    echo 1. Open Vivado GUI
    echo 2. File ^> Open Project
    echo 3. Navigate to vivado_project folder and open riscv_single_cycle.xpr
    echo.
    echo Or run: vivado vivado_project\riscv_single_cycle.xpr
    echo.
) else (
    echo.
    echo ERROR: Failed to create project
    echo Please check the error messages above
    echo.
)

pause