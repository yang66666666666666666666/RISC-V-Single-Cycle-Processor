# Basys 3 Board Constraints for RISC-V Single Cycle Processor
# Compatible with Digilent Basys 3 FPGA Board

# Clock signal (100 MHz)
set_property PACKAGE_PIN W5 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports clk]

# Reset button (center button)
set_property PACKAGE_PIN U18 [get_ports reset]
set_property IOSTANDARD LVCMOS33 [get_ports reset]

# LEDs for PC output (lower 16 bits)
set_property PACKAGE_PIN U16 [get_ports {pc_out[0]}]
set_property PACKAGE_PIN E19 [get_ports {pc_out[1]}]
set_property PACKAGE_PIN U19 [get_ports {pc_out[2]}]
set_property PACKAGE_PIN V19 [get_ports {pc_out[3]}]
set_property PACKAGE_PIN W18 [get_ports {pc_out[4]}]
set_property PACKAGE_PIN U15 [get_ports {pc_out[5]}]
set_property PACKAGE_PIN U14 [get_ports {pc_out[6]}]
set_property PACKAGE_PIN V14 [get_ports {pc_out[7]}]
set_property PACKAGE_PIN V13 [get_ports {pc_out[8]}]
set_property PACKAGE_PIN V3 [get_ports {pc_out[9]}]
set_property PACKAGE_PIN W3 [get_ports {pc_out[10]}]
set_property PACKAGE_PIN U3 [get_ports {pc_out[11]}]
set_property PACKAGE_PIN P3 [get_ports {pc_out[12]}]
set_property PACKAGE_PIN N3 [get_ports {pc_out[13]}]
set_property PACKAGE_PIN P1 [get_ports {pc_out[14]}]
set_property PACKAGE_PIN L1 [get_ports {pc_out[15]}]

set_property IOSTANDARD LVCMOS33 [get_ports {pc_out[*]}]

# 7-segment display for instruction display (optional)
# Cathodes
set_property PACKAGE_PIN U7 [get_ports {instruction_out[0]}]
set_property PACKAGE_PIN V5 [get_ports {instruction_out[1]}]
set_property PACKAGE_PIN U5 [get_ports {instruction_out[2]}]
set_property PACKAGE_PIN V8 [get_ports {instruction_out[3]}]
set_property PACKAGE_PIN U8 [get_ports {instruction_out[4]}]
set_property PACKAGE_PIN W6 [get_ports {instruction_out[5]}]
set_property PACKAGE_PIN W7 [get_ports {instruction_out[6]}]

set_property IOSTANDARD LVCMOS33 [get_ports {instruction_out[*]}]

# Switches for manual control (optional)
set_property PACKAGE_PIN V17 [get_ports {alu_result_out[0]}]
set_property PACKAGE_PIN V16 [get_ports {alu_result_out[1]}]
set_property PACKAGE_PIN W16 [get_ports {alu_result_out[2]}]
set_property PACKAGE_PIN W17 [get_ports {alu_result_out[3]}]
set_property PACKAGE_PIN W15 [get_ports {alu_result_out[4]}]
set_property PACKAGE_PIN V15 [get_ports {alu_result_out[5]}]
set_property PACKAGE_PIN W14 [get_ports {alu_result_out[6]}]
set_property PACKAGE_PIN W13 [get_ports {alu_result_out[7]}]

set_property IOSTANDARD LVCMOS33 [get_ports {alu_result_out[*]}]

# Timing constraints
set_input_delay -clock [get_clocks sys_clk_pin] -min -add_delay 2.000 [get_ports reset]
set_input_delay -clock [get_clocks sys_clk_pin] -max -add_delay 4.000 [get_ports reset]
set_output_delay -clock [get_clocks sys_clk_pin] -min -add_delay 1.000 [get_ports {pc_out[*]}]
set_output_delay -clock [get_clocks sys_clk_pin] -max -add_delay 3.000 [get_ports {pc_out[*]}]

# Configuration options
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property CFGBVS VCCO [current_design]