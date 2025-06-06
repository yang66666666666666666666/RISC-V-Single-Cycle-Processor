# Complete RISC-V Processor Vivado Project Creation Script
# Supports R, I, U, S, B, J type instructions
# Author: OpenHands AI Assistant
# Date: 2025-06-05

# Set project name and directory
set project_name "riscv_processor_complete"
set project_dir "./vivado_complete_project"

# Create project directory if it doesn't exist
file mkdir $project_dir

# Create new project
create_project $project_name $project_dir -part xc7a35tcpg236-1 -force

# Set project properties
set_property target_language Verilog [current_project]
set_property simulator_language Verilog [current_project]

# Add source files
add_files -norecurse {
    src/riscv_processor_complete.v
}

# Add testbench files
add_files -fileset sim_1 -norecurse {
    src/riscv_processor_complete_tb.v
}

# Add constraints file if it exists
if {[file exists "constraints/basys3.xdc"]} {
    add_files -fileset constrs_1 -norecurse constraints/basys3.xdc
}

# Set top module for synthesis
set_property top riscv_processor_complete [current_fileset]

# Set top module for simulation
set_property top riscv_processor_complete_tb [get_filesets sim_1]

# Update compile order
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

# Create runs
if {[get_runs synth_1] == ""} {
    create_run synth_1 -part xc7a35tcpg236-1 -flow {Vivado Synthesis 2024}
}

if {[get_runs impl_1] == ""} {
    create_run impl_1 -parent_run synth_1 -flow {Vivado Implementation 2024}
}

# Set synthesis options for better optimization
set_property strategy "Vivado Synthesis Defaults" [get_runs synth_1]
set_property steps.synth_design.args.flatten_hierarchy rebuilt [get_runs synth_1]
set_property steps.synth_design.args.gated_clock_conversion off [get_runs synth_1]
set_property steps.synth_design.args.bufg 12 [get_runs synth_1]
set_property steps.synth_design.args.directive AreaOptimized_high [get_runs synth_1]

# Set implementation options
set_property strategy "Vivado Implementation Defaults" [get_runs impl_1]
set_property steps.opt_design.args.directive Explore [get_runs impl_1]
set_property steps.place_design.args.directive Explore [get_runs impl_1]
set_property steps.route_design.args.directive Explore [get_runs impl_1]

puts "=========================================="
puts "Complete RISC-V Processor Project Created"
puts "=========================================="
puts "Project: $project_name"
puts "Location: [file normalize $project_dir]"
puts ""
puts "Supported Instruction Types:"
puts "✓ R-type: add, sub, and, or, xor, sll, slt"
puts "✓ I-type: addi, slli, slti, lw, jalr"
puts "✓ U-type: lui, auipc"
puts "✓ S-type: sw"
puts "✓ B-type: beq, bne, blt, bge"
puts "✓ J-type: jal"
puts ""
puts "Files added:"
puts "- src/riscv_processor_complete.v (main design)"
puts "- src/riscv_processor_complete_tb.v (testbench)"
puts "- constraints/basys3.xdc (FPGA constraints)"
puts ""
puts "Next steps:"
puts "1. Run simulation: launch_simulation"
puts "2. Run synthesis: launch_runs synth_1 -jobs 4"
puts "3. Run implementation: launch_runs impl_1 -jobs 4"
puts "4. Generate bitstream: launch_runs impl_1 -to_step write_bitstream -jobs 4"
puts ""
puts "To run simulation immediately:"
puts "launch_simulation"
puts ""
puts "To run complete flow:"
puts "launch_runs synth_1 -jobs 4"
puts "wait_on_run synth_1"
puts "launch_runs impl_1 -to_step write_bitstream -jobs 4"
puts "wait_on_run impl_1"
puts "=========================================="

# Optional: Launch simulation automatically
# Uncomment the next line to run simulation immediately
# launch_simulation

# Optional: Run synthesis automatically
# Uncomment the next lines to run synthesis immediately
# launch_runs synth_1 -jobs 4
# wait_on_run synth_1

# Save project
save_project_as $project_name $project_dir -force