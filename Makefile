# Makefile for RISC-V Single Cycle Processor
# Compatible with various Verilog simulators

# Default simulator (can be overridden)
SIM ?= iverilog

# Source files - Multiple versions available
SRC_BASIC = src/riscv_processor_fixed.v
TB_BASIC = src/riscv_processor_tb_fixed.v

SRC_COMPLETE = src/riscv_processor_complete.v
TB_COMPLETE = src/riscv_processor_complete_tb.v

# Output files
VVP_BASIC = riscv_processor_basic.vvp
VVP_COMPLETE = riscv_processor_complete.vvp
VCD_BASIC = riscv_processor_basic.vcd
VCD_COMPLETE = riscv_processor_complete.vcd

# Default target - run complete version
all: complete

# Complete version with all instruction types
complete: $(VVP_COMPLETE)
	vvp $(VVP_COMPLETE)

$(VVP_COMPLETE): $(SRC_COMPLETE) $(TB_COMPLETE)
	iverilog -o $(VVP_COMPLETE) $(SRC_COMPLETE) $(TB_COMPLETE)

# Basic version (original)
basic: $(VVP_BASIC)
	vvp $(VVP_BASIC)

$(VVP_BASIC): $(SRC_BASIC) $(TB_BASIC)
	iverilog -o $(VVP_BASIC) $(SRC_BASIC) $(TB_BASIC)

# Legacy targets for backward compatibility
iverilog: basic
simulate: basic

# Simulate with ModelSim/QuestaSim - Complete version
modelsim:
	vlib work
	vlog $(SRC_COMPLETE) $(TB_COMPLETE)
	vsim -c -do "run -all; quit" riscv_processor_complete_tb

# Simulate with ModelSim/QuestaSim - Basic version
modelsim-basic:
	vlib work
	vlog $(SRC_BASIC) $(TB_BASIC)
	vsim -c -do "run -all; quit" riscv_processor_tb_fixed

# Simulate with Verilator - Complete version
verilator:
	verilator --cc --exe --build -j 0 -Wall $(SRC_COMPLETE) $(TB_COMPLETE)
	./obj_dir/Vriscv_processor_complete_tb

# Clean generated files
clean:
	rm -f $(VVP_BASIC) $(VCD_BASIC) $(VVP_COMPLETE) $(VCD_COMPLETE)
	rm -rf work/
	rm -rf obj_dir/
	rm -f transcript
	rm -f vsim.wlf

# Help target
help:
	@echo "Available targets:"
	@echo "  all        - Default target (complete version)"
	@echo "  complete   - Run complete RISC-V processor (R,I,U,S,B,J types)"
	@echo "  basic      - Run basic RISC-V processor (original version)"
	@echo "  iverilog   - Alias for basic (backward compatibility)"
	@echo "  modelsim   - Simulate complete version with ModelSim/QuestaSim"
	@echo "  modelsim-basic - Simulate basic version with ModelSim/QuestaSim"
	@echo "  verilator  - Simulate with Verilator"
	@echo "  clean      - Remove generated files"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Instruction type support:"
	@echo "  Complete version: R, I, U, S, B, J types"
	@echo "  Basic version: R, I, S types (limited)"
	@echo ""
	@echo "For Windows users:"
	@echo "  Use run_vivado.bat to create Vivado project"
	@echo "  Or install WSL/MSYS2 to use this Makefile"

.PHONY: all complete basic iverilog modelsim modelsim-basic verilator clean help simulate