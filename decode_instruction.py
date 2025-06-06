#!/usr/bin/env python3
"""
RISC-V指令解码器
输入32位十六进制指令编码，输出对应的汇编指令
"""

def decode_instruction(instr_hex):
    """解码RISC-V指令"""
    if isinstance(instr_hex, str):
        if instr_hex.startswith('0x'):
            instr = int(instr_hex, 16)
        else:
            instr = int(instr_hex, 16)
    else:
        instr = instr_hex
    
    # 提取基本字段
    opcode = instr & 0x7F
    rd = (instr >> 7) & 0x1F
    funct3 = (instr >> 12) & 0x7
    rs1 = (instr >> 15) & 0x1F
    rs2 = (instr >> 20) & 0x1F
    funct7 = (instr >> 25) & 0x7F
    
    # 寄存器名称映射
    reg_names = [
        'x0', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7',
        'x8', 'x9', 'x10', 'x11', 'x12', 'x13', 'x14', 'x15',
        'x16', 'x17', 'x18', 'x19', 'x20', 'x21', 'x22', 'x23',
        'x24', 'x25', 'x26', 'x27', 'x28', 'x29', 'x30', 'x31'
    ]
    
    def get_reg(reg_num):
        return reg_names[reg_num] if reg_num < 32 else f'x{reg_num}'
    
    def sign_extend(value, bits):
        """符号扩展"""
        if value & (1 << (bits - 1)):
            return value | (0xFFFFFFFF << bits)
        return value
    
    # 根据opcode解码
    if opcode == 0b0110111:  # LUI
        imm = (instr >> 12) & 0xFFFFF
        return f"lui {get_reg(rd)}, 0x{imm:x}", "U型", f"{get_reg(rd)} = 0x{imm << 12:08x}"
    
    elif opcode == 0b0010111:  # AUIPC
        imm = (instr >> 12) & 0xFFFFF
        return f"auipc {get_reg(rd)}, 0x{imm:x}", "U型", f"{get_reg(rd)} = PC + 0x{imm << 12:08x}"
    
    elif opcode == 0b1101111:  # JAL
        # J型立即数重组
        imm = ((instr >> 31) & 0x1) << 20 | \
              ((instr >> 12) & 0xFF) << 12 | \
              ((instr >> 20) & 0x1) << 11 | \
              ((instr >> 21) & 0x3FF) << 1
        imm = sign_extend(imm, 21)
        return f"jal {get_reg(rd)}, {imm}", "J型", f"{get_reg(rd)} = PC+4; PC = PC+{imm}"
    
    elif opcode == 0b1100111:  # JALR
        imm = sign_extend((instr >> 20) & 0xFFF, 12)
        return f"jalr {get_reg(rd)}, {get_reg(rs1)}, {imm}", "I型", f"{get_reg(rd)} = PC+4; PC = {get_reg(rs1)}+{imm}"
    
    elif opcode == 0b1100011:  # Branch
        # B型立即数重组
        imm = ((instr >> 31) & 0x1) << 12 | \
              ((instr >> 7) & 0x1) << 11 | \
              ((instr >> 25) & 0x3F) << 5 | \
              ((instr >> 8) & 0xF) << 1
        imm = sign_extend(imm, 13)
        
        branch_ops = {
            0b000: "beq", 0b001: "bne", 0b100: "blt", 
            0b101: "bge", 0b110: "bltu", 0b111: "bgeu"
        }
        op = branch_ops.get(funct3, f"b_unknown_{funct3}")
        return f"{op} {get_reg(rs1)}, {get_reg(rs2)}, {imm}", "B型", f"if ({get_reg(rs1)} {op[1:]} {get_reg(rs2)}) PC = PC+{imm}"
    
    elif opcode == 0b0000011:  # Load
        imm = sign_extend((instr >> 20) & 0xFFF, 12)
        load_ops = {
            0b000: "lb", 0b001: "lh", 0b010: "lw", 
            0b100: "lbu", 0b101: "lhu"
        }
        op = load_ops.get(funct3, f"l_unknown_{funct3}")
        return f"{op} {get_reg(rd)}, {imm}({get_reg(rs1)})", "I型", f"{get_reg(rd)} = memory[{get_reg(rs1)}+{imm}]"
    
    elif opcode == 0b0100011:  # Store
        imm = sign_extend(((instr >> 25) & 0x7F) << 5 | ((instr >> 7) & 0x1F), 12)
        store_ops = {
            0b000: "sb", 0b001: "sh", 0b010: "sw"
        }
        op = store_ops.get(funct3, f"s_unknown_{funct3}")
        return f"{op} {get_reg(rs2)}, {imm}({get_reg(rs1)})", "S型", f"memory[{get_reg(rs1)}+{imm}] = {get_reg(rs2)}"
    
    elif opcode == 0b0010011:  # I-type ALU
        imm = sign_extend((instr >> 20) & 0xFFF, 12)
        
        if funct3 == 0b000:  # ADDI
            return f"addi {get_reg(rd)}, {get_reg(rs1)}, {imm}", "I型", f"{get_reg(rd)} = {get_reg(rs1)} + {imm}"
        elif funct3 == 0b010:  # SLTI
            return f"slti {get_reg(rd)}, {get_reg(rs1)}, {imm}", "I型", f"{get_reg(rd)} = ({get_reg(rs1)} < {imm}) ? 1 : 0"
        elif funct3 == 0b011:  # SLTIU
            return f"sltiu {get_reg(rd)}, {get_reg(rs1)}, {imm}", "I型", f"{get_reg(rd)} = ({get_reg(rs1)} < {imm}u) ? 1 : 0"
        elif funct3 == 0b100:  # XORI
            return f"xori {get_reg(rd)}, {get_reg(rs1)}, {imm}", "I型", f"{get_reg(rd)} = {get_reg(rs1)} ^ {imm}"
        elif funct3 == 0b110:  # ORI
            return f"ori {get_reg(rd)}, {get_reg(rs1)}, {imm}", "I型", f"{get_reg(rd)} = {get_reg(rs1)} | {imm}"
        elif funct3 == 0b111:  # ANDI
            return f"andi {get_reg(rd)}, {get_reg(rs1)}, {imm}", "I型", f"{get_reg(rd)} = {get_reg(rs1)} & {imm}"
        elif funct3 == 0b001:  # SLLI
            shamt = rs2  # 对于移位指令，rs2字段是移位量
            return f"slli {get_reg(rd)}, {get_reg(rs1)}, {shamt}", "I型", f"{get_reg(rd)} = {get_reg(rs1)} << {shamt}"
        elif funct3 == 0b101:  # SRLI/SRAI
            shamt = rs2
            if funct7 & 0x20:  # SRAI
                return f"srai {get_reg(rd)}, {get_reg(rs1)}, {shamt}", "I型", f"{get_reg(rd)} = {get_reg(rs1)} >> {shamt} (算术)"
            else:  # SRLI
                return f"srli {get_reg(rd)}, {get_reg(rs1)}, {shamt}", "I型", f"{get_reg(rd)} = {get_reg(rs1)} >> {shamt} (逻辑)"
    
    elif opcode == 0b0110011:  # R-type ALU
        if funct3 == 0b000:  # ADD/SUB
            if funct7 & 0x20:  # SUB
                return f"sub {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = {get_reg(rs1)} - {get_reg(rs2)}"
            else:  # ADD
                return f"add {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = {get_reg(rs1)} + {get_reg(rs2)}"
        elif funct3 == 0b001:  # SLL
            return f"sll {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = {get_reg(rs1)} << {get_reg(rs2)}"
        elif funct3 == 0b010:  # SLT
            return f"slt {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = ({get_reg(rs1)} < {get_reg(rs2)}) ? 1 : 0"
        elif funct3 == 0b011:  # SLTU
            return f"sltu {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = ({get_reg(rs1)} < {get_reg(rs2)}u) ? 1 : 0"
        elif funct3 == 0b100:  # XOR
            return f"xor {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = {get_reg(rs1)} ^ {get_reg(rs2)}"
        elif funct3 == 0b101:  # SRL/SRA
            if funct7 & 0x20:  # SRA
                return f"sra {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = {get_reg(rs1)} >> {get_reg(rs2)} (算术)"
            else:  # SRL
                return f"srl {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = {get_reg(rs1)} >> {get_reg(rs2)} (逻辑)"
        elif funct3 == 0b110:  # OR
            return f"or {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = {get_reg(rs1)} | {get_reg(rs2)}"
        elif funct3 == 0b111:  # AND
            return f"and {get_reg(rd)}, {get_reg(rs1)}, {get_reg(rs2)}", "R型", f"{get_reg(rd)} = {get_reg(rs1)} & {get_reg(rs2)}"
    
    # 未知指令
    return f"unknown_0x{instr:08x}", "未知", "未知指令"

def print_instruction_details(instr_hex):
    """打印指令的详细信息"""
    if isinstance(instr_hex, str):
        if instr_hex.startswith('0x'):
            instr = int(instr_hex, 16)
        else:
            instr = int(instr_hex, 16)
    else:
        instr = instr_hex
    
    print(f"\n指令编码: 0x{instr:08x}")
    print(f"二进制:   {instr:032b}")
    
    # 字段分解
    opcode = instr & 0x7F
    rd = (instr >> 7) & 0x1F
    funct3 = (instr >> 12) & 0x7
    rs1 = (instr >> 15) & 0x1F
    rs2 = (instr >> 20) & 0x1F
    funct7 = (instr >> 25) & 0x7F
    
    print(f"字段分解:")
    print(f"  opcode:  {opcode:07b} (0x{opcode:02x})")
    print(f"  rd:      {rd:05b} (x{rd})")
    print(f"  funct3:  {funct3:03b} (0x{funct3:x})")
    print(f"  rs1:     {rs1:05b} (x{rs1})")
    print(f"  rs2:     {rs2:05b} (x{rs2})")
    print(f"  funct7:  {funct7:07b} (0x{funct7:02x})")
    
    # 解码指令
    asm, instr_type, description = decode_instruction(instr)
    print(f"\n汇编指令: {asm}")
    print(f"指令类型: {instr_type}")
    print(f"功能描述: {description}")

def main():
    """主函数 - 交互式指令解码器"""
    print("RISC-V指令解码器")
    print("=" * 50)
    print("输入指令编码（十六进制），例如: 00500093 或 0x00500093")
    print("输入 'q' 退出，输入 'test' 运行测试")
    print()
    
    # 测试用例
    test_cases = [
        "00500093",  # addi x1, x0, 5
        "00a00113",  # addi x2, x0, 10
        "fff00193",  # addi x3, x0, -1
        "002081b3",  # add x3, x1, x2
        "40208233",  # sub x4, x1, x2
        "0020f2b3",  # and x5, x1, x2
        "0020e333",  # or x6, x1, x2
        "000125b7",  # lui x11, 0x12
        "00012617",  # auipc x12, 0x12
        "00302023",  # sw x3, 0(x0)
        "00002683",  # lw x13, 0(x0)
        "00208463",  # beq x1, x2, 8
        "008000ef",  # jal x1, 8
        "00108067",  # jalr x0, x1, 1
    ]
    
    while True:
        try:
            user_input = input("请输入指令编码: ").strip()
            
            if user_input.lower() == 'q':
                print("再见！")
                break
            elif user_input.lower() == 'test':
                print("\n运行测试用例:")
                print("-" * 50)
                for i, test_instr in enumerate(test_cases):
                    print(f"\n测试 {i+1}: {test_instr}")
                    asm, instr_type, description = decode_instruction(test_instr)
                    print(f"  汇编: {asm}")
                    print(f"  类型: {instr_type}")
                    print(f"  功能: {description}")
                print("-" * 50)
                continue
            elif not user_input:
                continue
            
            # 解码指令
            print_instruction_details(user_input)
            
        except ValueError as e:
            print(f"错误: 无效的十六进制数 '{user_input}'")
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    main()