@echo off
REM Complete RISC-V Processor Vivado Project Launcher
REM Supports R, I, U, S, B, J type instructions
REM Author: OpenHands AI Assistant
REM Date: 2025-06-05

echo ==========================================
echo Complete RISC-V Single Cycle Processor
echo ==========================================
echo.
echo This script creates a Vivado project for the complete
echo RISC-V processor supporting all instruction types:
echo.
echo ✓ R-type: add, sub, and, or, xor, sll, slt
echo ✓ I-type: addi, slli, slti, lw, jalr  
echo ✓ U-type: lui, auipc
echo ✓ S-type: sw
echo ✓ B-type: beq, bne, blt, bge
echo ✓ J-type: jal
echo.

REM Check if Vivado is in PATH
where vivado >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Vivado not found in PATH
    echo Please make sure Vivado is installed and added to your system PATH
    echo Typical Vivado installation path: C:\Xilinx\Vivado\2024.1\bin
    echo.
    echo Alternative options:
    echo 1. Run run_alternative.bat for other simulation tools
    echo 2. See ONLINE_SIMULATION_GUIDE.md for browser-based testing
    echo 3. See WINDOWS_SETUP.md for detailed setup instructions
    echo.
    pause
    exit /b 1
)

echo Vivado found! Creating complete RISC-V processor project...
echo.

REM Create Vivado project using TCL script
vivado -mode batch -source create_vivado_project_complete.tcl

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo Project Created Successfully!
    echo ==========================================
    echo.
    echo Project location: .\vivado_complete_project\
    echo.
    echo To open the project:
    echo 1. Launch Vivado
    echo 2. Open Project: .\vivado_complete_project\riscv_processor_complete.xpr
    echo.
    echo Or run Vivado with the project directly:
    echo vivado .\vivado_complete_project\riscv_processor_complete.xpr
    echo.
    echo Next steps in Vivado:
    echo 1. Run Simulation ^(Flow ^> Run Simulation ^> Run Behavioral Simulation^)
    echo 2. Run Synthesis ^(Flow ^> Run Synthesis^)
    echo 3. Run Implementation ^(Flow ^> Run Implementation^)
    echo 4. Generate Bitstream ^(Flow ^> Generate Bitstream^)
    echo.
    
    set /p open_vivado="Would you like to open Vivado with the project now? (y/n): "
    if /i "%open_vivado%"=="y" (
        echo Opening Vivado...
        start vivado .\vivado_complete_project\riscv_processor_complete.xpr
    )
) else (
    echo.
    echo ERROR: Failed to create Vivado project
    echo Please check the error messages above
    echo.
    echo Troubleshooting:
    echo 1. Make sure all source files exist in src/ directory
    echo 2. Check Vivado installation and licensing
    echo 3. Try running Vivado manually and sourcing the TCL script
    echo.
)

echo.
echo For more help, see:
echo - WINDOWS_SETUP.md ^(detailed Windows setup guide^)
echo - ONLINE_SIMULATION_GUIDE.md ^(browser-based testing^)
echo - run_alternative.bat ^(alternative simulation tools^)
echo.
pause