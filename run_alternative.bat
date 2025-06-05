@echo off
REM Alternative simulation script for Windows without Vivado
REM This script provides options for different simulation tools

echo ========================================
echo RISC-V Processor - Alternative Simulation
echo ========================================
echo.

echo Vivado not found in PATH. Here are alternative options:
echo.

echo [1] Download and install Vivado (Recommended)
echo [2] Use online Verilog simulator
echo [3] Install Icarus Verilog for Windows
echo [4] Use WSL (Windows Subsystem for Linux)
echo [5] Manual Vivado setup instructions
echo [6] Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto :download_vivado
if "%choice%"=="2" goto :online_sim
if "%choice%"=="3" goto :icarus_windows
if "%choice%"=="4" goto :wsl_setup
if "%choice%"=="5" goto :manual_vivado
if "%choice%"=="6" goto :exit
goto :invalid

:download_vivado
echo.
echo Opening Xilinx download page...
echo.
echo Please download Vivado WebPACK (free version) from:
echo https://www.xilinx.com/support/download.html
echo.
echo After installation, add this path to your system PATH:
echo C:\Xilinx\Vivado\2024.1\bin
echo.
echo Then run run_vivado.bat again.
start https://www.xilinx.com/support/download.html
goto :end

:online_sim
echo.
echo You can use online Verilog simulators:
echo.
echo 1. EDA Playground: https://www.edaplayground.com/
echo 2. HDLBits: https://hdlbits.01xz.net/wiki/Iverilog
echo 3. Verilog Online: https://verilogonline.com/
echo.
echo Copy the contents of src/riscv_processor_fixed.v and 
echo src/riscv_processor_tb_fixed.v to the online simulator.
echo.
start https://www.edaplayground.com/
goto :end

:icarus_windows
echo.
echo Installing Icarus Verilog for Windows:
echo.
echo 1. Download from: http://bleyer.org/icarus/
echo 2. Install the Windows version
echo 3. Add to PATH or use full path
echo 4. Run: iverilog -o test.vvp src\riscv_processor_fixed.v src\riscv_processor_tb_fixed.v
echo 5. Run: vvp test.vvp
echo.
start http://bleyer.org/icarus/
goto :end

:wsl_setup
echo.
echo Using Windows Subsystem for Linux (WSL):
echo.
echo 1. Install WSL: wsl --install
echo 2. Open WSL terminal
echo 3. Install tools: sudo apt install iverilog gtkwave
echo 4. Navigate to project: cd /mnt/c/path/to/your/project
echo 5. Run: make iverilog
echo.
echo This provides a full Linux environment on Windows.
goto :end

:manual_vivado
echo.
echo Manual Vivado Setup Instructions:
echo.
echo If Vivado is already installed but not in PATH:
echo.
echo 1. Find your Vivado installation (usually C:\Xilinx\Vivado\VERSION\)
echo 2. Open Vivado GUI manually
echo 3. In TCL Console, run these commands:
echo    cd "C:\path\to\RISC-V-Single-Cycle-Processor"
echo    source create_vivado_project.tcl
echo.
echo Or add Vivado to your system PATH:
echo 1. Right-click "This PC" ^> Properties
echo 2. Advanced system settings ^> Environment Variables
echo 3. Edit PATH variable
echo 4. Add: C:\Xilinx\Vivado\2024.1\bin
echo.
goto :end

:invalid
echo.
echo Invalid choice. Please enter 1-6.
goto :end

:exit
echo.
echo Exiting...
goto :end

:end
echo.
echo For more help, see WINDOWS_SETUP.md
pause