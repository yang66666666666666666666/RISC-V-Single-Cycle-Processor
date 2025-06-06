# RISC-V Single Cycle Processor - Windows Setup Guide

This guide will help you set up and run the RISC-V single cycle processor on Windows.

## Prerequisites

### Option 1: Xilinx Vivado (Recommended)
- **Xilinx Vivado 2024.1 or later** (Free WebPACK edition is sufficient)
- Download from: https://www.xilinx.com/support/download.html
- Minimum system requirements:
  - Windows 10/11 (64-bit)
  - 8 GB RAM (16 GB recommended)
  - 100 GB free disk space

### Option 2: Alternative Simulators
- **ModelSim Intel FPGA Edition** (Free)
- **Icarus Verilog** (Open source)
- **GTKWave** for waveform viewing

## Quick Start with Vivado

### Method 1: Automated Setup (Easiest)

1. **Open Command Prompt or PowerShell**
   ```cmd
   cd path\to\RISC-V-Single-Cycle-Processor
   ```

2. **Run the setup script**
   ```cmd
   run_vivado.bat
   ```

3. **Open the project in Vivado GUI**
   - The script will create a project in `vivado_project` folder
   - Open Vivado
   - File → Open Project
   - Navigate to `vivado_project\riscv_single_cycle.xpr`

### Method 2: Manual Setup

1. **Open Vivado**

2. **Create New Project**
   - File → New Project
   - Project name: `riscv_single_cycle`
   - Choose project location
   - Select "RTL Project"
   - Don't specify sources at this time
   - Choose target device (e.g., Artix-7 xc7a35tcpg236-1)

3. **Add Source Files**
   - Add Sources → Add or create design sources
   - Add: `src/riscv_processor.v`
   - Set as top module: `riscv_processor`

4. **Add Simulation Sources**
   - Add Sources → Add or create simulation sources
   - Add: `src/riscv_processor_tb.v`
   - Set as top module: `riscv_processor_tb`

## Running Simulation

### In Vivado

1. **Start Behavioral Simulation**
   - Click "Run Simulation" → "Run Behavioral Simulation"
   - Or use TCL command: `launch_simulation`

2. **View Results**
   - Check the TCL Console for text output
   - View waveforms in the simulation window
   - The simulation will run for 1000ns by default

3. **Analyze Waveforms**
   - Add signals to waveform viewer if needed
   - Zoom and navigate through the simulation timeline
   - Verify processor behavior matches expected results

### Expected Simulation Output

The testbench will execute the following program:
```assembly
addi x1, x0, 5      # x1 = 5
addi x2, x0, 10     # x2 = 10
add  x3, x1, x2     # x3 = 15
sub  x4, x1, x2     # x4 = -5
and  x5, x1, x2     # x5 = 0
or   x6, x1, x2     # x6 = 15
sw   x3, 0(x0)      # Store 15 to memory[0]
lw   x7, 0(x0)      # Load from memory[0] to x7
```

## Project Structure

```
RISC-V-Single-Cycle-Processor/
├── src/
│   ├── riscv_processor.v      # Main processor design
│   └── riscv_processor_tb.v   # Testbench
├── vivado_project/            # Generated Vivado project
├── create_vivado_project.tcl  # TCL script for project creation
├── run_vivado.bat            # Windows batch script
├── Makefile                  # For alternative simulators
├── WINDOWS_SETUP.md          # This file
└── README.md                 # General project information
```

## Processor Features

### Supported Instructions
- **I-type**: `addi` (Add immediate)
- **R-type**: `add`, `sub`, `and`, `or` (Register-register operations)
- **Load/Store**: `lw`, `sw` (Load/store word)
- **Branch**: `beq` (Branch if equal)

### Architecture Components
- **Program Counter (PC)**: Tracks current instruction address
- **Instruction Memory**: Contains the program instructions
- **Register File**: 32 general-purpose registers (x0-x31)
- **ALU**: Arithmetic and logic operations
- **Data Memory**: For load/store operations
- **Control Unit**: Generates control signals
- **Sign Extend**: Handles immediate values

## Troubleshooting

### Common Issues

1. **"Vivado not found in PATH"**
   - Add Vivado to your system PATH
   - Typical path: `C:\Xilinx\Vivado\2024.1\bin`
   - Or run Vivado manually and source the TCL script

2. **Simulation doesn't start**
   - Check that all source files are added correctly
   - Verify top modules are set properly
   - Check for syntax errors in the source files

3. **Unexpected simulation results**
   - Verify the instruction memory initialization
   - Check control signal generation
   - Use waveform viewer to debug signal transitions

### Getting Help

1. **Check Vivado Documentation**
   - Help → Documentation and Tutorials
   - Vivado Design Suite User Guide

2. **Xilinx Community Forums**
   - https://forums.xilinx.com/

3. **RISC-V Specification**
   - https://riscv.org/specifications/

## Advanced Usage

### Modifying the Processor

1. **Adding New Instructions**
   - Update the control unit (`main_decoder` and `alu_decoder`)
   - Modify ALU if new operations are needed
   - Update instruction memory with test cases

2. **Changing Memory Size**
   - Modify array sizes in `instruction_memory` and `data_memory`
   - Update address decoding logic if needed

3. **Adding Debug Features**
   - Expose internal signals as outputs
   - Add register file monitoring
   - Implement single-step execution

### Synthesis and Implementation

1. **Run Synthesis**
   - Click "Run Synthesis" in Vivado
   - Check for timing and resource utilization

2. **Run Implementation**
   - Click "Run Implementation"
   - Generate bitstream for FPGA deployment

3. **Target Different FPGAs**
   - Change target device in project settings
   - Adjust constraints if needed

## Performance Notes

- **Clock Frequency**: The design should achieve 50-100 MHz on most FPGAs
- **Resource Usage**: Minimal LUT and BRAM usage
- **Power Consumption**: Low power design suitable for battery applications

## License

This project is provided under the MIT License. See LICENSE file for details.

## Contributing

Feel free to submit issues and enhancement requests!