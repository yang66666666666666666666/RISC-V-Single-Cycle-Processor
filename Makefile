# Makefile for RISC-V Single Cycle Processor
# Compatible with various Verilog simulators

# Default simulator (can be overridden)
SIM ?= iverilog

# Source files
SRC = src/riscv_processor.v
TB = src/riscv_processor_tb.v

# Output files
VVP = riscv_processor.vvp
VCD = riscv_processor.vcd

# Default target
all: simulate

# Compile and simulate with Icarus Verilog
iverilog: $(VVP)
	vvp $(VVP)

$(VVP): $(SRC) $(TB)
	iverilog -o $(VVP) $(SRC) $(TB)

# Simulate with ModelSim/QuestaSim
modelsim:
	vlib work
	vlog $(SRC) $(TB)
	vsim -c -do "run -all; quit" riscv_processor_tb

# Simulate with Verilator
verilator:
	verilator --cc --exe --build -j 0 -Wall $(SRC) $(TB)
	./obj_dir/Vriscv_processor_tb

# Clean generated files
clean:
	rm -f $(VVP) $(VCD)
	rm -rf work/
	rm -rf obj_dir/
	rm -f transcript
	rm -f vsim.wlf

# Help target
help:
	@echo "Available targets:"
	@echo "  all        - Default target (same as simulate)"
	@echo "  iverilog   - Compile and simulate with Icarus Verilog"
	@echo "  modelsim   - Simulate with ModelSim/QuestaSim"
	@echo "  verilator  - Simulate with Verilator"
	@echo "  clean      - Remove generated files"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "For Windows users:"
	@echo "  Use run_vivado.bat to create Vivado project"
	@echo "  Or install WSL/MSYS2 to use this Makefile"

.PHONY: all iverilog modelsim verilator clean help simulate

# Alias for default simulation
simulate: iverilog