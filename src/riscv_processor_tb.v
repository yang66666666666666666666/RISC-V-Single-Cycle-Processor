// RISC-V Single Cycle Processor Testbench
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
        #20;
        
        // Release reset
        reset = 0;
        
        // Monitor the processor execution
        $display("=== RISC-V Single Cycle Processor Test ===");
        $display("Time\tPC\tInstruction\tALU Result\tWrite Data\tRead Data");
        $display("----\t--\t-----------\t----------\t----------\t---------");
        
        // Run for several clock cycles to see instruction execution
        repeat (20) begin
            @(posedge clk);
            #1; // Small delay to ensure signals are stable
            $display("%0t\t%h\t%h\t%h\t%h\t%h", 
                     $time, pc_out, instruction_out, alu_result_out, 
                     write_data_out, read_data_out);
        end
        
        // Test specific instructions
        $display("\n=== Instruction Analysis ===");
        
        // Reset and step through instructions one by one
        reset = 1;
        #10;
        reset = 0;
        
        // Instruction 0: addi x1, x0, 5 (x1 = 5)
        @(posedge clk);
        #1;
        $display("Instruction 0 - addi x1, x0, 5:");
        $display("  PC: %h, Instruction: %h", pc_out, instruction_out);
        $display("  Expected: x1 = 5");
        
        // Instruction 1: addi x2, x0, 10 (x2 = 10)
        @(posedge clk);
        #1;
        $display("Instruction 1 - addi x2, x0, 10:");
        $display("  PC: %h, Instruction: %h", pc_out, instruction_out);
        $display("  Expected: x2 = 10");
        
        // Instruction 2: add x3, x1, x2 (x3 = x1 + x2 = 15)
        @(posedge clk);
        #1;
        $display("Instruction 2 - add x3, x1, x2:");
        $display("  PC: %h, Instruction: %h", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: 15)", alu_result_out);
        
        // Instruction 3: sub x4, x1, x2 (x4 = x1 - x2 = -5)
        @(posedge clk);
        #1;
        $display("Instruction 3 - sub x4, x1, x2:");
        $display("  PC: %h, Instruction: %h", pc_out, instruction_out);
        $display("  ALU Result: %h (Expected: -5)", alu_result_out);
        
        // Instruction 4: and x5, x1, x2 (x5 = x1 & x2)
        @(posedge clk);
        #1;
        $display("Instruction 4 - and x5, x1, x2:");
        $display("  PC: %h, Instruction: %h", pc_out, instruction_out);
        $display("  ALU Result: %h", alu_result_out);
        
        // Instruction 5: or x6, x1, x2 (x6 = x1 | x2)
        @(posedge clk);
        #1;
        $display("Instruction 5 - or x6, x1, x2:");
        $display("  PC: %h, Instruction: %h", pc_out, instruction_out);
        $display("  ALU Result: %h", alu_result_out);
        
        // Instruction 6: sw x3, 0(x0) (store x3 to address 0)
        @(posedge clk);
        #1;
        $display("Instruction 6 - sw x3, 0(x0):");
        $display("  PC: %h, Instruction: %h", pc_out, instruction_out);
        $display("  Write Data: %h (Should be 15)", write_data_out);
        
        // Instruction 7: lw x7, 0(x0) (load from address 0 to x7)
        @(posedge clk);
        #1;
        $display("Instruction 7 - lw x7, 0(x0):");
        $display("  PC: %h, Instruction: %h", pc_out, instruction_out);
        $display("  Read Data: %h (Should be 15)", read_data_out);
        
        // Continue for a few more cycles
        repeat (5) begin
            @(posedge clk);
            #1;
            $display("PC: %h, Instruction: %h", pc_out, instruction_out);
        end
        
        $display("\n=== Test Completed ===");
        $finish;
    end
    
    // Optional: Generate VCD file for waveform viewing
    initial begin
        $dumpfile("riscv_processor.vcd");
        $dumpvars(0, riscv_processor_tb);
    end
    
    // Monitor register file changes (for debugging)
    always @(posedge clk) begin
        if (!reset) begin
            // You can add register monitoring here if needed
            // This would require exposing register file signals
        end
    end

endmodule