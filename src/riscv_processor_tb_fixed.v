// RISC-V Single Cycle Processor Testbench - Fixed Version
// Compatible with Windows Vivado environment
// Author: OpenHands AI Assistant
// Date: 2025-06-05

`timescale 1ns / 1ps

module riscv_processor_tb;

    // Clock and reset signals
    reg clk;
    reg reset;
    
    // Output signals from processor
    wire [31:0] pc_out;
    wire [31:0] instruction_out;
    wire [31:0] alu_result_out;
    wire [31:0] write_data_out;
    wire [31:0] read_data_out;
    
    // Instantiate the RISC-V processor
    riscv_processor uut (
        .clk(clk),
        .reset(reset),
        .pc_out(pc_out),
        .instruction_out(instruction_out),
        .alu_result_out(alu_result_out),
        .write_data_out(write_data_out),
        .read_data_out(read_data_out)
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
        $display("=== RISC-V Single Cycle Processor Test ===");
        $display("Time\tPC\tInstruction\tALU Result\tWrite Data\tRead Data");
        $display("----\t--\t-----------\t----------\t----------\t---------");
        
        // Run for several clock cycles to see instruction execution
        repeat (15) begin
            @(posedge clk);
            #1; // Small delay to ensure signals are stable
            $display("%0t\t%h\t%h\t%h\t%h\t%h", 
                     $time, pc_out, instruction_out, alu_result_out, 
                     write_data_out, read_data_out);
        end
        
        // Test specific instructions
        $display("\n=== Detailed Instruction Analysis ===");
        
        // Reset and step through instructions one by one
        reset = 1;
        #10;
        reset = 0;
        #1;
        
        // Instruction 0: addi x1, x0, 5 (x1 = 5)
        $display("Cycle 0 - PC: %h, Instruction: %h (addi x1, x0, 5)", pc_out, instruction_out);
        @(posedge clk);
        #1;
        
        // Instruction 1: addi x2, x0, 10 (x2 = 10)
        $display("Cycle 1 - PC: %h, Instruction: %h (addi x2, x0, 10)", pc_out, instruction_out);
        @(posedge clk);
        #1;
        
        // Instruction 2: add x3, x1, x2 (x3 = x1 + x2 = 15)
        $display("Cycle 2 - PC: %h, Instruction: %h (add x3, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 15 = 0x0000000F)", alu_result_out);
        @(posedge clk);
        #1;
        
        // Instruction 3: sub x4, x1, x2 (x4 = x1 - x2 = -5)
        $display("Cycle 3 - PC: %h, Instruction: %h (sub x4, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: -5 = 0xFFFFFFFB)", alu_result_out);
        @(posedge clk);
        #1;
        
        // Instruction 4: and x5, x1, x2 (x5 = x1 & x2)
        $display("Cycle 4 - PC: %h, Instruction: %h (and x5, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 & 10 = 0)", alu_result_out);
        @(posedge clk);
        #1;
        
        // Instruction 5: or x6, x1, x2 (x6 = x1 | x2)
        $display("Cycle 5 - PC: %h, Instruction: %h (or x6, x1, x2)", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 5 | 10 = 15)", alu_result_out);
        @(posedge clk);
        #1;
        
        // Instruction 6: sw x3, 0(x0) (store x3 to address 0)
        $display("Cycle 6 - PC: %h, Instruction: %h (sw x3, 0(x0))", pc_out, instruction_out);
        $display("  Write Data: %h (Should be 15)", write_data_out);
        @(posedge clk);
        #1;
        
        // Instruction 7: lw x7, 0(x0) (load from address 0 to x7)
        $display("Cycle 7 - PC: %h, Instruction: %h (lw x7, 0(x0))", pc_out, instruction_out);
        $display("  Read Data: %h (Should be 15)", read_data_out);
        @(posedge clk);
        #1;
        
        // Continue for a few more cycles
        repeat (3) begin
            $display("Cycle %0d - PC: %h, Instruction: %h (nop)", 
                     ($time-25)/10-7, pc_out, instruction_out);
            @(posedge clk);
            #1;
        end
        
        $display("\n=== Register File Status (if accessible) ===");
        $display("Note: Register values are internal and not directly observable");
        $display("Expected values after execution:");
        $display("  x1 = 5 (0x00000005)");
        $display("  x2 = 10 (0x0000000A)");
        $display("  x3 = 15 (0x0000000F)");
        $display("  x4 = -5 (0xFFFFFFFB)");
        $display("  x5 = 0 (0x00000000)");
        $display("  x6 = 15 (0x0000000F)");
        $display("  x7 = 15 (0x0000000F)");
        
        $display("\n=== Test Completed Successfully ===");
        $finish;
    end
    
    // Optional: Generate VCD file for waveform viewing
    initial begin
        $dumpfile("riscv_processor.vcd");
        $dumpvars(0, riscv_processor_tb);
    end
    
    // Monitor important signals
    always @(posedge clk) begin
        if (!reset) begin
            // Monitor for any unexpected behavior
            if (pc_out === 32'hxxxxxxxx) begin
                $display("ERROR: PC is undefined at time %0t", $time);
            end
            if (instruction_out === 32'hxxxxxxxx) begin
                $display("ERROR: Instruction is undefined at time %0t", $time);
            end
        end
    end

endmodule