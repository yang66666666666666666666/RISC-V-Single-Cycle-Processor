@echo off
REM RISC-V Single Cycle Processor Demo Script for Windows
REM This script demonstrates the processor functionality

echo ========================================
echo RISC-V Single Cycle Processor Demo
echo ========================================
echo.

echo This demo will show you how the RISC-V processor works.
echo.

REM Check if we're in the right directory
if not exist "src\riscv_processor_fixed.v" (
    echo ERROR: Please run this script from the RISC-V-Single-Cycle-Processor directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Step 1: Checking processor design files...
if exist "src\riscv_processor_fixed.v" (
    echo   ✓ Main processor design found
) else (
    echo   ✗ Main processor design missing
    goto :error
)

if exist "src\riscv_processor_tb_fixed.v" (
    echo   ✓ Testbench found
) else (
    echo   ✗ Testbench missing
    goto :error
)

echo.
echo Step 2: Processor Features
echo   • 32-bit RISC-V architecture
echo   • Single cycle execution
echo   • Supports I-type, R-type, Load/Store instructions
echo   • 32 general-purpose registers
echo   • 64-word instruction and data memory
echo.

echo Step 3: Test Program Overview
echo   The processor will execute this program:
echo.
echo   addi x1, x0, 5      # x1 = 5
echo   addi x2, x0, 10     # x2 = 10
echo   add  x3, x1, x2     # x3 = 15 (5 + 10)
echo   sub  x4, x1, x2     # x4 = -5 (5 - 10)
echo   and  x5, x1, x2     # x5 = 0 (5 & 10)
echo   or   x6, x1, x2     # x6 = 15 (5 | 10)
echo   sw   x3, 0(x0)      # Store 15 to memory[0]
echo   lw   x7, 0(x0)      # Load from memory[0] to x7
echo.

echo Step 4: Available Options
echo.
echo Choose how you want to run the processor:
echo.
echo [1] Create Vivado Project (Recommended for Windows)
echo [2] Run with Icarus Verilog (Requires installation)
echo [3] View project structure
echo [4] Open setup guide
echo [5] Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto :vivado
if "%choice%"=="2" goto :icarus
if "%choice%"=="3" goto :structure
if "%choice%"=="4" goto :guide
if "%choice%"=="5" goto :exit
goto :invalid

:vivado
echo.
echo Creating Vivado project...
echo.
if exist "run_vivado.bat" (
    call run_vivado.bat
) else (
    echo Running TCL script directly...
    where vivado >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Vivado not found. Please install Vivado or add it to PATH.
        echo Typical path: C:\Xilinx\Vivado\2024.1\bin
        goto :error
    )
    vivado -mode batch -source create_vivado_project.tcl
)
goto :end

:icarus
echo.
echo Running with Icarus Verilog...
echo.
where iverilog >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Icarus Verilog not found.
    echo Please install Icarus Verilog or use WSL.
    echo Download from: http://bleyer.org/icarus/
    goto :error
)

echo Compiling processor...
iverilog -o riscv_processor_demo.vvp src\riscv_processor_fixed.v src\riscv_processor_tb_fixed.v

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Compilation failed
    goto :error
)

echo Running simulation...
vvp riscv_processor_demo.vvp

echo.
echo Simulation completed! Check the output above for results.
goto :end

:structure
echo.
echo Project Structure:
echo.
echo RISC-V-Single-Cycle-Processor/
echo ├── src/
echo │   ├── riscv_processor_fixed.v      # Main processor design
echo │   ├── riscv_processor_tb_fixed.v   # Testbench
echo │   ├── riscv_processor.v            # Original design
echo │   └── riscv_processor_tb.v         # Original testbench
echo ├── vivado_project/                  # Vivado project (generated)
echo ├── create_vivado_project.tcl        # Vivado setup script
echo ├── run_vivado.bat                   # Windows Vivado launcher
echo ├── demo.bat                         # This demo script
echo ├── Makefile                         # Linux/Unix build file
echo ├── WINDOWS_SETUP.md                 # Detailed setup guide
echo └── README_UPDATED.md                # Updated documentation
echo.
pause
goto :end

:guide
echo.
echo Opening setup guide...
if exist "WINDOWS_SETUP.md" (
    start notepad "WINDOWS_SETUP.md"
) else (
    echo Setup guide not found. Please check WINDOWS_SETUP.md
)
goto :end

:invalid
echo.
echo Invalid choice. Please enter 1-5.
echo.
pause
goto :end

:error
echo.
echo Demo encountered an error. Please check the messages above.
echo For detailed setup instructions, see WINDOWS_SETUP.md
echo.
pause
goto :end

:exit
echo.
echo Thank you for trying the RISC-V processor demo!
goto :end

:end
echo.
echo Demo completed.
pause