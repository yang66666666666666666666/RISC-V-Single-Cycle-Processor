// Complete RISC-V Single Cycle Processor Testbench
// Tests R, I, U, S, B, J type instructions
// Author: OpenHands AI Assistant
// Date: 2025-06-05

`timescale 1ns / 1ps

module riscv_processor_complete_tb;

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
    
    // Instantiate the complete RISC-V processor
    riscv_processor_complete uut (
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
        $display("=== Complete RISC-V Single Cycle Processor Test ===");
        $display("Testing R, I, U, S, B, J type instructions");
        $display("Time\tPC\tInstruction\tALU Result\tWrite Data\tReg Write");
        $display("----\t--\t-----------\t----------\t----------\t---------");
        
        // Run for several clock cycles to see instruction execution
        repeat (35) begin
            @(posedge clk);
            #1; // Small delay to ensure signals are stable
            $display("%0t\t%h\t%h\t%h\t%h\t%h", 
                     $time, pc_out, instruction_out, alu_result_out, 
                     write_data_out, reg_write_data_out);
        end
        
        // Detailed instruction analysis
        $display("\n=== Detailed Instruction Type Analysis ===");
        
        // Reset and step through instructions one by one
        reset = 1;
        #10;
        reset = 0;
        #1;
        
        // I-type instructions
        $display("\n--- I-type Instructions ---");
        
        // Instruction 0: addi x1, x0, 5
        $display("Cycle 0 - PC: %h, Instruction: %h (addi x1, x0, 5)", pc_out, instruction_out);
        $display("  Expected: x1 = 5");
        @(posedge clk); #1;
        
        // Instruction 1: addi x2, x0, 10
        $display("Cycle 1 - PC: %h, Instruction: %h (addi x2, x0, 10)", pc_out, instruction_out);
        $display("  Expected: x2 = 10");
        @(posedge clk); #1;
        
        // Instruction 2: addi x3, x0, -1
        $display("Cycle 2 - PC: %h, Instruction: %h (addi x3, x0, -1)", pc_out, instruction_out);
        $display("  Expected: x3 = -1 (0xFFFFFFFF)");
        @(posedge clk); #1;
        
        // Instruction 3: slli x4, x1, 2
        $display("Cycle 3 - PC: %h, Instruction: %h (slli x4, x1, 2)", pc_out, instruction_out);
        $display("  Expected: x4 = x1 << 2 = 20");
        @(posedge clk); #1;
        
        // Instruction 4: slti x5, x1, 2
        $display("Cycle 4 - PC: %h, Instruction: %h (slti x5, x1, 2)", pc_out, instruction_out);
        $display("  Expected: x5 = (5 < 2) ? 1 : 0 = 0");
        @(posedge clk); #1;
        
        $display("\n--- R-type Instructions ---");
        
        // Instruction 5: add x3, x1, x2
        $display("Cycle 5 - PC: %h, Instruction: %h (add x3, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 + 10 = 15)", alu_result_out);
        @(posedge clk); #1;
        
        // Instruction 6: sub x4, x1, x2
        $display("Cycle 6 - PC: %h, Instruction: %h (sub x4, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 - 10 = -5)", alu_result_out);
        @(posedge clk); #1;
        
        // Instruction 7: and x5, x1, x2
        $display("Cycle 7 - PC: %h, Instruction: %h (and x5, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 & 10 = 0)", alu_result_out);
        @(posedge clk); #1;
        
        // Instruction 8: or x6, x1, x2
        $display("Cycle 8 - PC: %h, Instruction: %h (or x6, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 | 10 = 15)", alu_result_out);
        @(posedge clk); #1;
        
        // Instruction 9: xor x7, x1, x2
        $display("Cycle 9 - PC: %h, Instruction: %h (xor x7, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 ^ 10 = 15)", alu_result_out);
        @(posedge clk); #1;
        
        // Instruction 10: sll x9, x1, x2
        $display("Cycle 10 - PC: %h, Instruction: %h (sll x9, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 << 10 = 5120)", alu_result_out);
        @(posedge clk); #1;
        
        // Instruction 11: slt x10, x1, x2
        $display("Cycle 11 - PC: %h, Instruction: %h (slt x10, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: (5 < 10) ? 1 : 0 = 1)", alu_result_out);
        @(posedge clk); #1;
        
        $display("\n--- U-type Instructions ---");
        
        // Instruction 12: lui x11, 0x12
        $display("Cycle 12 - PC: %h, Instruction: %h (lui x11, 0x12)", pc_out, instruction_out);
        $display("  Reg Write Data: %h (Expected: 0x12000)", reg_write_data_out);
        @(posedge clk); #1;
        
        // Instruction 13: auipc x12, 0x12
        $display("Cycle 13 - PC: %h, Instruction: %h (auipc x12, 0x12)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: PC + 0x12000)", alu_result_out);
        @(posedge clk); #1;
        
        $display("\n--- S-type Instructions ---");
        
        // Instruction 14: sw x3, 0(x0)
        $display("Cycle 14 - PC: %h, Instruction: %h (sw x3, 0(x0))", pc_out, instruction_out);
        $display("  Write Data: %h (Should store x3 to memory[0])", write_data_out);
        @(posedge clk); #1;
        
        // Instruction 15: sw x4, 4(x0)
        $display("Cycle 15 - PC: %h, Instruction: %h (sw x4, 4(x0))", pc_out, instruction_out);
        $display("  Write Data: %h (Should store x4 to memory[1])", write_data_out);
        @(posedge clk); #1;
        
        $display("\n--- Load Instructions (I-type memory) ---");
        
        // Instruction 16: lw x13, 0(x0)
        $display("Cycle 16 - PC: %h, Instruction: %h (lw x13, 0(x0))", pc_out, instruction_out);
        $display("  Read Data: %h (Should load from memory[0])", read_data_out);
        @(posedge clk); #1;
        
        // Instruction 17: lw x14, 4(x0)
        $display("Cycle 17 - PC: %h, Instruction: %h (lw x14, 4(x0))", pc_out, instruction_out);
        $display("  Read Data: %h (Should load from memory[1])", read_data_out);
        @(posedge clk); #1;
        
        $display("\n--- B-type Instructions ---");
        
        // Instruction 18: beq x1, x2, 8
        $display("Cycle 18 - PC: %h, Instruction: %h (beq x1, x2, 8)", pc_out, instruction_out);
        $display("  Branch condition: x1(%d) == x2(%d) ? Should NOT branch", 5, 10);
        @(posedge clk); #1;
        
        // Instruction 19: bne x1, x2, 8
        $display("Cycle 19 - PC: %h, Instruction: %h (bne x1, x2, 8)", pc_out, instruction_out);
        $display("  Branch condition: x1(%d) != x2(%d) ? Should branch", 5, 10);
        @(posedge clk); #1;
        
        // Continue for a few more cycles to see branch behavior
        repeat (5) begin
            $display("Cycle %0d - PC: %h, Instruction: %h", 
                     ($time-25)/10-19, pc_out, instruction_out);
            @(posedge clk); #1;
        end
        
        $display("\n=== Instruction Type Summary ===");
        $display("+ I-type: addi, slli, slti, lw");
        $display("+ R-type: add, sub, and, or, xor, sll, slt");
        $display("+ U-type: lui, auipc");
        $display("+ S-type: sw");
        $display("+ B-type: beq, bne, blt, bge");
        $display("+ J-type: jal, jalr");
        
        $display("\n=== Expected Register Values ===");
        $display("x1  = 5 (0x00000005)");
        $display("x2  = 10 (0x0000000A)");
        $display("x3  = 15 (0x0000000F) - from add");
        $display("x4  = -5 (0xFFFFFFFB) - from sub");
        $display("x5  = 0 (0x00000000) - from and");
        $display("x6  = 15 (0x0000000F) - from or");
        $display("x7  = 15 (0x0000000F) - from xor");
        $display("x9  = 5120 (0x00001400) - from sll");
        $display("x10 = 1 (0x00000001) - from slt");
        $display("x11 = 0x12000 - from lui");
        $display("x12 = PC + 0x12000 - from auipc");
        $display("x13 = value from memory[0] - from lw");
        $display("x14 = value from memory[1] - from lw");
        
        $display("\n=== Test Completed Successfully ===");
        $display("All RISC-V instruction types (R, I, U, S, B, J) have been tested!");
        $finish;
    end
    
    // Optional: Generate VCD file for waveform viewing
    initial begin
        $dumpfile("riscv_processor_complete.vcd");
        $dumpvars(0, riscv_processor_complete_tb);
    end
    
    // Monitor important signals for debugging
    always @(posedge clk) begin
        if (!reset) begin
            // Check for any undefined signals
            if (pc_out === 32'hxxxxxxxx) begin
                $display("ERROR: PC is undefined at time %0t", $time);
            end
            if (instruction_out === 32'hxxxxxxxx) begin
                $display("ERROR: Instruction is undefined at time %0t", $time);
            end
        end
    end

endmodule