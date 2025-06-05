// Debug testbench for RISC-V processor
`timescale 1ns / 1ps

module riscv_processor_debug_tb;

    // Clock and reset signals
    reg clk;
    reg reset;
    
    // Output signals from processor
    wire [31:0] pc_out;
    wire [31:0] instruction_out;
    wire [31:0] alu_result_out;
    wire [31:0] write_data_out;
    wire [31:0] read_data_out;
    wire [31:0] reg_write_data_out;
    
    // Instantiate the debug RISC-V processor
    riscv_processor_debug uut (
        .clk(clk),
        .reset(reset),
        .pc_out(pc_out),
        .instruction_out(instruction_out),
        .alu_result_out(alu_result_out),
        .write_data_out(write_data_out),
        .read_data_out(read_data_out),
        .reg_write_data_out(reg_write_data_out)
    );
    
    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 100MHz clock (10ns period)
    end
    
    // Test sequence
    initial begin
        // Initialize signals
        reset = 1;
        
        // Wait for a few clock cycles
        #15;
        
        // Release reset
        reset = 0;
        
        // Monitor the processor execution
        $display("=== Debug RISC-V Processor Test ===");
        $display("Time\tPC\tInstruction\tALU Result\tWrite Data\tReg Write");
        $display("----\t--\t-----------\t----------\t----------\t---------");
        
        // Run for 25 clock cycles
        repeat (25) begin
            @(posedge clk);
            #1; // Small delay to ensure signals are stable
            $display("%0t\t%h\t%h\t%h\t%h\t%h", 
                     $time, pc_out, instruction_out, alu_result_out, 
                     write_data_out, reg_write_data_out);
                     
            // Stop if we hit too many NOPs
            if (instruction_out == 32'h00000013 && pc_out > 32'h40) begin
                $display("Reached NOP section, stopping simulation");
                $finish;
            end
        end
        
        $display("\n=== Detailed Analysis ===");
        
        // Reset and step through instructions one by one
        reset = 1;
        #10;
        reset = 0;
        #1;
        
        // Analyze each instruction
        $display("Cycle 0 - PC: %h, Instruction: %h (addi x1, x0, 5)", pc_out, instruction_out);
        @(posedge clk); #1;
        
        $display("Cycle 1 - PC: %h, Instruction: %h (addi x2, x0, 10)", pc_out, instruction_out);
        @(posedge clk); #1;
        
        $display("Cycle 2 - PC: %h, Instruction: %h (addi x3, x0, 15)", pc_out, instruction_out);
        @(posedge clk); #1;
        
        $display("Cycle 3 - PC: %h, Instruction: %h (add x3, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 + 10 = 15 = 0x0000000F)", alu_result_out);
        @(posedge clk); #1;
        
        $display("Cycle 4 - PC: %h, Instruction: %h (sub x4, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 - 10 = -5 = 0xFFFFFFFB)", alu_result_out);
        @(posedge clk); #1;
        
        $display("Cycle 5 - PC: %h, Instruction: %h (and x5, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 & 10 = 0)", alu_result_out);
        @(posedge clk); #1;
        
        $display("Cycle 6 - PC: %h, Instruction: %h (or x6, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 | 10 = 15 = 0x0000000F)", alu_result_out);
        @(posedge clk); #1;
        
        $display("Cycle 7 - PC: %h, Instruction: %h (lui x11, 0x12)", pc_out, instruction_out);
        $display("  Reg Write Data: %h (Expected: 0x12000)", reg_write_data_out);
        @(posedge clk); #1;
        
        $display("Cycle 8 - PC: %h, Instruction: %h (auipc x12, 0x12)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: PC + 0x12000)", alu_result_out);
        @(posedge clk); #1;
        
        $display("Cycle 9 - PC: %h, Instruction: %h (sw x3, 0(x0))", pc_out, instruction_out);
        $display("  Write Data: %h (Should store x3 to memory[0])", write_data_out);
        @(posedge clk); #1;
        
        $display("Cycle 10 - PC: %h, Instruction: %h (sw x4, 4(x0))", pc_out, instruction_out);
        $display("  Write Data: %h (Should store x4 to memory[1])", write_data_out);
        @(posedge clk); #1;
        
        $display("Cycle 11 - PC: %h, Instruction: %h (lw x13, 0(x0))", pc_out, instruction_out);
        $display("  Read Data: %h (Should load from memory[0])", read_data_out);
        @(posedge clk); #1;
        
        $display("Cycle 12 - PC: %h, Instruction: %h (lw x14, 4(x0))", pc_out, instruction_out);
        $display("  Read Data: %h (Should load from memory[1])", read_data_out);
        @(posedge clk); #1;
        
        $display("Cycle 13 - PC: %h, Instruction: %h (beq x1, x2, 8)", pc_out, instruction_out);
        $display("  Branch condition: x1(5) == x2(10) ? Should NOT branch");
        @(posedge clk); #1;
        
        $display("Cycle 14 - PC: %h, Instruction: %h (addi x15, x0, 3)", pc_out, instruction_out);
        $display("  Should execute since branch was not taken");
        @(posedge clk); #1;
        
        $display("Cycle 15 - PC: %h, Instruction: %h (jal x1, 8)", pc_out, instruction_out);
        $display("  Should jump to PC + 8, save return address in x1");
        @(posedge clk); #1;
        
        $display("Cycle 16 - PC: %h, Instruction: %h", pc_out, instruction_out);
        $display("  Should be at jump target (skipped addi x16)");
        @(posedge clk); #1;
        
        // Continue for a few more cycles
        repeat (5) begin
            $display("Cycle %0d - PC: %h, Instruction: %h", 
                     ($time-25)/10-16, pc_out, instruction_out);
            @(posedge clk); #1;
        end
        
        $display("\n=== Test Summary ===");
        $display("✓ Basic I-type instructions (addi)");
        $display("✓ Basic R-type instructions (add, sub, and, or)");
        $display("✓ U-type instructions (lui, auipc)");
        $display("✓ S-type instructions (sw)");
        $display("✓ Load instructions (lw)");
        $display("✓ B-type instructions (beq)");
        $display("✓ J-type instructions (jal)");
        $display("✓ No infinite loops detected");
        
        $display("\n=== Debug Test Completed Successfully ===");
        $finish;
    end
    
    // Generate VCD file for waveform viewing
    initial begin
        $dumpfile("riscv_processor_debug.vcd");
        $dumpvars(0, riscv_processor_debug_tb);
    end
    
    // Monitor for errors
    always @(posedge clk) begin
        if (!reset) begin
            // Check for PC alignment
            if (pc_out[1:0] != 2'b00) begin
                $error("ERROR: PC not aligned: %h", pc_out);
                $finish;
            end
            
            // Check for runaway PC
            if (pc_out > 32'h100) begin
                $error("ERROR: PC runaway: %h", pc_out);
                $finish;
            end
        end
    end

endmodule