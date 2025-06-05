// Debug version of RISC-V processor with simplified test program
// This version fixes the JALR infinite loop issue
`timescale 1ns / 1ps

// Include the complete processor but with a different instruction memory
module riscv_processor_debug(
    input wire clk,
    input wire reset,
    output wire [31:0] pc_out,
    output wire [31:0] instruction_out,
    output wire [31:0] alu_result_out,
    output wire [31:0] write_data_out,
    output wire [31:0] read_data_out,
    output wire [31:0] reg_write_data_out
);

    // Internal wires
    wire [31:0] pc_next, pc_plus4, pc_target;
    wire [31:0] instruction;
    wire [31:0] src_a, src_b, alu_result;
    wire [31:0] imm_ext;
    wire [31:0] write_data, read_data, result;
    wire zero, alu_zero;
    
    // Control signals
    wire pc_src, alu_src, reg_write, mem_write, branch, jump;
    wire [1:0] result_src, imm_src;
    wire [3:0] alu_control;

    // Program Counter
    program_counter_complete pc_inst (
        .clk(clk),
        .reset(reset),
        .pc_next(pc_next),
        .pc_out(pc_out)
    );

    // PC Adders
    assign pc_plus4 = pc_out + 4;
    
    // PC Target calculation - fixed for JALR
    wire jalr_instruction = (instruction[6:0] == 7'b1100111); // JALR opcode
    assign pc_target = jalr_instruction ? (src_a + imm_ext) : (pc_out + imm_ext);

    // PC Source Multiplexer - supports both branch and jump
    assign pc_next = (pc_src | jump) ? pc_target : pc_plus4;

    // Debug Instruction Memory with simplified program
    instruction_memory_debug imem (
        .address(pc_out),
        .instruction(instruction)
    );

    // Control Unit
    control_unit_complete ctrl (
        .opcode(instruction[6:0]),
        .funct3(instruction[14:12]),
        .funct7(instruction[30]),
        .zero(alu_zero),
        .pc_src(pc_src),
        .result_src(result_src),
        .mem_write(mem_write),
        .alu_src(alu_src),
        .imm_src(imm_src),
        .reg_write(reg_write),
        .jump(jump),
        .branch(branch),
        .alu_control(alu_control)
    );

    // Register File
    register_file_complete regfile (
        .clk(clk),
        .we3(reg_write),
        .a1(instruction[19:15]),
        .a2(instruction[24:20]),
        .a3(instruction[11:7]),
        .wd3(result),
        .rd1(src_a),
        .rd2(write_data)
    );

    // Sign Extend - supports all instruction types
    sign_extend_complete ext (
        .instr(instruction),
        .imm_src(imm_src),
        .imm_ext(imm_ext)
    );

    // ALU Source Multiplexer
    assign src_b = alu_src ? imm_ext : write_data;

    // ALU - enhanced for all operations
    alu_complete alu_inst (
        .src_a(src_a),
        .src_b(src_b),
        .alu_control(alu_control),
        .alu_result(alu_result),
        .zero(alu_zero)
    );

    // Data Memory
    data_memory_complete dmem (
        .clk(clk),
        .we(mem_write),
        .address(alu_result),
        .write_data(write_data),
        .read_data(read_data)
    );

    // Result Source Multiplexer - supports PC+4 for JAL
    result_mux_complete res_mux (
        .alu_result(alu_result),
        .read_data(read_data),
        .pc_plus4(pc_plus4),
        .imm_ext(imm_ext),  // For LUI/AUIPC
        .result_src(result_src),
        .result(result)
    );

    // Output assignments
    assign instruction_out = instruction;
    assign alu_result_out = alu_result;
    assign write_data_out = write_data;
    assign read_data_out = read_data;
    assign reg_write_data_out = result;

endmodule

// Simplified instruction memory for debugging
module instruction_memory_debug(
    input wire [31:0] address,
    output reg [31:0] instruction
);
    reg [31:0] memory [0:63];
    
    // Simplified test program - no infinite loops
    initial begin
        // Basic I-type instructions
        memory[0]  = 32'h00500093;  // addi x1, x0, 5       (x1 = 5)
        memory[1]  = 32'h00A00113;  // addi x2, x0, 10      (x2 = 10)
        memory[2]  = 32'h00F00193;  // addi x3, x0, 15      (x3 = 15)
        
        // Basic R-type instructions  
        memory[3]  = 32'h002081B3;  // add  x3, x1, x2      (x3 = x1 + x2 = 15)
        memory[4]  = 32'h40208233;  // sub  x4, x1, x2      (x4 = x1 - x2 = -5)
        memory[5]  = 32'h0020F2B3;  // and  x5, x1, x2      (x5 = x1 & x2)
        memory[6]  = 32'h0020E333;  // or   x6, x1, x2      (x6 = x1 | x2)
        
        // U-type instructions
        memory[7]  = 32'h000125B7;  // lui  x11, 0x12       (x11 = 0x12000)
        memory[8]  = 32'h00012617;  // auipc x12, 0x12      (x12 = PC + 0x12000)
        
        // S-type instructions
        memory[9]  = 32'h00302023;  // sw   x3, 0(x0)       (store x3 to mem[0])
        memory[10] = 32'h00402223;  // sw   x4, 4(x0)       (store x4 to mem[1])
        
        // Load instructions
        memory[11] = 32'h00002683;  // lw   x13, 0(x0)      (load from mem[0])
        memory[12] = 32'h00402703;  // lw   x14, 4(x0)      (load from mem[1])
        
        // Simple branch test (should not branch since x1 != x2)
        memory[13] = 32'h00208463;  // beq  x1, x2, 8       (branch if x1 == x2)
        memory[14] = 32'h00300793;  // addi x15, x0, 3      (x15 = 3) - should execute
        
        // Simple jump test
        memory[15] = 32'h008000EF;  // jal  x1, 8           (jump to memory[17])
        memory[16] = 32'h00400813;  // addi x16, x0, 4      (should be skipped)
        memory[17] = 32'h00500893;  // addi x17, x0, 5      (jump target, x17 = 5)
        
        // End with infinite NOPs to prevent runaway
        for (integer i = 18; i < 64; i = i + 1) begin
            memory[i] = 32'h00000013; // nop (addi x0, x0, 0)
        end
    end
    
    always @(*) begin
        instruction = memory[address[31:2]]; // Word-aligned access
    end
endmodule