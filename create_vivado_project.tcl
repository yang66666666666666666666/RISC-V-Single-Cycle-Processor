# Vivado TCL script to create RISC-V Single Cycle Processor project
# Compatible with Vivado 2024.1 and later versions
# For Windows environment

# Set project name and directory
set project_name "riscv_single_cycle"
set project_dir "./vivado_project"

# Create project directory if it doesn't exist
file mkdir $project_dir

# Create new project
create_project $project_name $project_dir -part xc7a35tcpg236-1 -force

# Add source files - Complete version with all instruction types
add_files -norecurse ./src/riscv_processor_complete.v

# Add testbench files
add_files -fileset sim_1 -norecurse ./src/riscv_processor_complete_tb.v

# Also add basic version for comparison
add_files -norecurse ./src/riscv_processor_fixed.v
add_files -fileset sim_1 -norecurse ./src/riscv_processor_tb_fixed.v

# Set top module to complete version
set_property top riscv_processor_complete [current_fileset]
set_property top riscv_processor_complete_tb [get_filesets sim_1]

# Update compile order
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

# Set simulation runtime
set_property -name {xsim.simulate.runtime} -value {1000ns} -objects [get_filesets sim_1]

puts "Project created successfully!"
puts "Project location: [file normalize $project_dir]"
puts ""
puts "To open the project in Vivado GUI:"
puts "1. Open Vivado"
puts "2. File -> Open Project"
puts "3. Navigate to $project_dir and select $project_name.xpr"
puts ""
puts "To run simulation:"
puts "1. Click 'Run Simulation' -> 'Run Behavioral Simulation'"
puts "2. Or use TCL command: launch_simulation"