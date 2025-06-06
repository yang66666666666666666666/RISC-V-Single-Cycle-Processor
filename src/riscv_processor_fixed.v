// RISC-V Single Cycle Processor - Fixed Version
// Compatible with Windows Vivado environment
// Author: OpenHands AI Assistant
// Date: 2025-06-05

`timescale 1ns / 1ps

//=============================================================================
// Top Level RISC-V Processor Module
//=============================================================================
module riscv_processor(
    input wire clk,
    input wire reset,
    output wire [31:0] pc_out,
    output wire [31:0] instruction_out,
    output wire [31:0] alu_result_out,
    output wire [31:0] write_data_out,
    output wire [31:0] read_data_out
);

    // Internal wires
    wire [31:0] pc_next, pc_plus4, pc_target;
    wire [31:0] instruction;
    wire [31:0] src_a, src_b, alu_result;
    wire [31:0] imm_ext;
    wire [31:0] write_data, read_data, result;
    wire zero;
    
    // Control signals
    wire pc_src, alu_src, reg_write, mem_write, branch;
    wire [1:0] result_src, imm_src, alu_op;
    wire [2:0] alu_control;

    // Program Counter
    program_counter pc_inst (
        .clk(clk),
        .reset(reset),
        .pc_next(pc_next),
        .pc_out(pc_out)
    );

    // PC Adders
    assign pc_plus4 = pc_out + 4;
    assign pc_target = pc_out + imm_ext;

    // PC Source Multiplexer
    assign pc_next = pc_src ? pc_target : pc_plus4;

    // Instruction Memory
    instruction_memory imem (
        .address(pc_out),
        .instruction(instruction)
    );

    // Control Unit
    control_unit ctrl (
        .opcode(instruction[6:0]),
        .funct3(instruction[14:12]),
        .funct7(instruction[30]),
        .zero(zero),
        .pc_src(pc_src),
        .result_src(result_src),
        .mem_write(mem_write),
        .alu_src(alu_src),
        .imm_src(imm_src),
        .reg_write(reg_write),
        .alu_control(alu_control)
    );

    // Register File
    register_file regfile (
        .clk(clk),
        .we3(reg_write),
        .a1(instruction[19:15]),
        .a2(instruction[24:20]),
        .a3(instruction[11:7]),
        .wd3(result),
        .rd1(src_a),
        .rd2(write_data)
    );

    // Sign Extend
    sign_extend ext (
        .instr(instruction[31:7]),
        .imm_src(imm_src),
        .imm_ext(imm_ext)
    );

    // ALU Source Multiplexer
    assign src_b = alu_src ? imm_ext : write_data;

    // ALU
    alu alu_inst (
        .src_a(src_a),
        .src_b(src_b),
        .alu_control(alu_control),
        .alu_result(alu_result),
        .zero(zero)
    );

    // Data Memory
    data_memory dmem (
        .clk(clk),
        .we(mem_write),
        .address(alu_result),
        .write_data(write_data),
        .read_data(read_data)
    );

    // Result Source Multiplexer
    result_mux res_mux (
        .alu_result(alu_result),
        .read_data(read_data),
        .pc_plus4(pc_plus4),
        .result_src(result_src),
        .result(result)
    );

    // Output assignments
    assign instruction_out = instruction;
    assign alu_result_out = alu_result;
    assign write_data_out = write_data;
    assign read_data_out = read_data;

endmodule

//=============================================================================
// Program Counter Module
//=============================================================================
module program_counter(
    input wire clk,
    input wire reset,
    input wire [31:0] pc_next,
    output reg [31:0] pc_out
);
    always @(posedge clk) begin
        if (reset)
            pc_out <= 32'h00000000;
        else
            pc_out <= pc_next;
    end
endmodule

//=============================================================================
// Instruction Memory Module
//=============================================================================
module instruction_memory(
    input wire [31:0] address,
    output reg [31:0] instruction
);
    reg [31:0] memory [0:63];
    
    // Initialize with sample RISC-V instructions
    initial begin
        // Test program: Simple arithmetic and memory operations
        memory[0] = 32'h00500093;  // addi x1, x0, 5      (x1 = 5)
        memory[1] = 32'h00A00113;  // addi x2, x0, 10     (x2 = 10)
        memory[2] = 32'h002081B3;  // add  x3, x1, x2     (x3 = x1 + x2 = 15)
        memory[3] = 32'h40208233;  // sub  x4, x1, x2     (x4 = x1 - x2 = -5)
        memory[4] = 32'h0020F2B3;  // and  x5, x1, x2     (x5 = x1 & x2)
        memory[5] = 32'h0020E333;  // or   x6, x1, x2     (x6 = x1 | x2)
        memory[6] = 32'h00302023;  // sw   x3, 0(x0)      (store x3 to address 0)
        memory[7] = 32'h00002383;  // lw   x7, 0(x0)      (load from address 0 to x7)
        memory[8] = 32'h00000013;  // nop (addi x0, x0, 0)
        memory[9] = 32'h00000013;  // nop (addi x0, x0, 0)
        memory[10] = 32'h00000013; // nop (addi x0, x0, 0)
        
        // Initialize remaining memory to NOPs
        for (integer i = 11; i < 64; i = i + 1) begin
            memory[i] = 32'h00000013; // nop
        end
    end
    
    always @(*) begin
        instruction = memory[address[31:2]]; // Word-aligned access
    end
endmodule

//=============================================================================
// Control Unit Module
//=============================================================================
module control_unit(
    input wire [6:0] opcode,
    input wire [2:0] funct3,
    input wire funct7,
    input wire zero,
    output wire pc_src,
    output wire [1:0] result_src,
    output wire mem_write,
    output wire alu_src,
    output wire [1:0] imm_src,
    output wire reg_write,
    output wire [2:0] alu_control
);
    wire branch;
    wire [1:0] alu_op;
    
    // Main Decoder
    main_decoder main_dec (
        .opcode(opcode),
        .result_src(result_src),
        .mem_write(mem_write),
        .branch(branch),
        .alu_src(alu_src),
        .reg_write(reg_write),
        .imm_src(imm_src),
        .alu_op(alu_op)
    );
    
    // ALU Decoder
    alu_decoder alu_dec (
        .opcode(opcode[5]),
        .funct3(funct3),
        .funct7(funct7),
        .alu_op(alu_op),
        .alu_control(alu_control)
    );
    
    assign pc_src = branch & zero;
endmodule

//=============================================================================
// Main Decoder Module
//=============================================================================
module main_decoder(
    input wire [6:0] opcode,
    output reg [1:0] result_src,
    output reg mem_write,
    output reg branch,
    output reg alu_src,
    output reg reg_write,
    output reg [1:0] imm_src,
    output reg [1:0] alu_op
);
    always @(*) begin
        case (opcode)
            7'b0000011: begin // lw (load word)
                result_src = 2'b01;
                mem_write = 1'b0;
                branch = 1'b0;
                alu_src = 1'b1;
                reg_write = 1'b1;
                imm_src = 2'b00;
                alu_op = 2'b00;
            end
            7'b0100011: begin // sw (store word)
                result_src = 2'b00; // don't care
                mem_write = 1'b1;
                branch = 1'b0;
                alu_src = 1'b1;
                reg_write = 1'b0;
                imm_src = 2'b01;
                alu_op = 2'b00;
            end
            7'b0110011: begin // R-type (add, sub, and, or)
                result_src = 2'b00;
                mem_write = 1'b0;
                branch = 1'b0;
                alu_src = 1'b0;
                reg_write = 1'b1;
                imm_src = 2'b00; // don't care
                alu_op = 2'b10;
            end
            7'b1100011: begin // beq (branch equal)
                result_src = 2'b00; // don't care
                mem_write = 1'b0;
                branch = 1'b1;
                alu_src = 1'b0;
                reg_write = 1'b0;
                imm_src = 2'b10;
                alu_op = 2'b01;
            end
            7'b0010011: begin // I-type ALU (addi)
                result_src = 2'b00;
                mem_write = 1'b0;
                branch = 1'b0;
                alu_src = 1'b1;
                reg_write = 1'b1;
                imm_src = 2'b00;
                alu_op = 2'b10;
            end
            default: begin
                result_src = 2'b00;
                mem_write = 1'b0;
                branch = 1'b0;
                alu_src = 1'b0;
                reg_write = 1'b0;
                imm_src = 2'b00;
                alu_op = 2'b00;
            end
        endcase
    end
endmodule

//=============================================================================
// ALU Decoder Module
//=============================================================================
module alu_decoder(
    input wire opcode,
    input wire [2:0] funct3,
    input wire funct7,
    input wire [1:0] alu_op,
    output reg [2:0] alu_control
);
    always @(*) begin
        case (alu_op)
            2'b00: alu_control = 3'b000; // add
            2'b01: alu_control = 3'b001; // subtract
            2'b10: begin
                case (funct3)
                    3'b000: begin
                        if (opcode & funct7)
                            alu_control = 3'b001; // sub
                        else
                            alu_control = 3'b000; // add
                    end
                    3'b010: alu_control = 3'b101; // slt
                    3'b110: alu_control = 3'b011; // or
                    3'b111: alu_control = 3'b010; // and
                    default: alu_control = 3'b000;
                endcase
            end
            default: alu_control = 3'b000;
        endcase
    end
endmodule

//=============================================================================
// Register File Module
//=============================================================================
module register_file(
    input wire clk,
    input wire we3,
    input wire [4:0] a1, a2, a3,
    input wire [31:0] wd3,
    output wire [31:0] rd1, rd2
);
    reg [31:0] registers [31:0];
    
    // Initialize registers
    initial begin
        for (integer i = 0; i < 32; i = i + 1) begin
            registers[i] = 32'h00000000;
        end
    end
    
    always @(posedge clk) begin
        if (we3 && a3 != 5'b00000) // Don't write to x0
            registers[a3] <= wd3;
    end
    
    assign rd1 = (a1 == 5'b00000) ? 32'h00000000 : registers[a1];
    assign rd2 = (a2 == 5'b00000) ? 32'h00000000 : registers[a2];
endmodule

//=============================================================================
// Sign Extend Module
//=============================================================================
module sign_extend(
    input wire [31:7] instr,
    input wire [1:0] imm_src,
    output reg [31:0] imm_ext
);
    always @(*) begin
        case (imm_src)
            2'b00: // I-type
                imm_ext = {{20{instr[31]}}, instr[31:20]};
            2'b01: // S-type
                imm_ext = {{20{instr[31]}}, instr[31:25], instr[11:7]};
            2'b10: // B-type
                imm_ext = {{20{instr[31]}}, instr[7], instr[30:25], instr[11:8], 1'b0};
            2'b11: // J-type
                imm_ext = {{12{instr[31]}}, instr[19:12], instr[20], instr[30:21], 1'b0};
            default:
                imm_ext = 32'h00000000;
        endcase
    end
endmodule

//=============================================================================
// ALU Module
//=============================================================================
module alu(
    input wire [31:0] src_a, src_b,
    input wire [2:0] alu_control,
    output reg [31:0] alu_result,
    output wire zero
);
    always @(*) begin
        case (alu_control)
            3'b000: alu_result = src_a + src_b;           // add
            3'b001: alu_result = src_a - src_b;           // subtract
            3'b010: alu_result = src_a & src_b;           // and
            3'b011: alu_result = src_a | src_b;           // or
            3'b101: alu_result = (src_a < src_b) ? 1 : 0; // slt
            default: alu_result = 32'h00000000;
        endcase
    end
    
    assign zero = (alu_result == 32'h00000000);
endmodule

//=============================================================================
// Data Memory Module
//=============================================================================
module data_memory(
    input wire clk,
    input wire we,
    input wire [31:0] address,
    input wire [31:0] write_data,
    output wire [31:0] read_data
);
    reg [31:0] memory [63:0];
    
    // Initialize memory
    initial begin
        for (integer i = 0; i < 64; i = i + 1) begin
            memory[i] = 32'h00000000;
        end
    end
    
    always @(posedge clk) begin
        if (we)
            memory[address[31:2]] <= write_data;
    end
    
    assign read_data = memory[address[31:2]];
endmodule

//=============================================================================
// Result Multiplexer Module
//=============================================================================
module result_mux(
    input wire [31:0] alu_result,
    input wire [31:0] read_data,
    input wire [31:0] pc_plus4,
    input wire [1:0] result_src,
    output reg [31:0] result
);
    always @(*) begin
        case (result_src)
            2'b00: result = alu_result;
            2'b01: result = read_data;
            2'b10: result = pc_plus4;
            default: result = alu_result;
        endcase
    end
endmodule