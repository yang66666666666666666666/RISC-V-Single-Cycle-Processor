#!/usr/bin/env python3
"""
Simple logic test for RISC-V processor without requiring Verilog simulator
"""

def test_instruction_decode():
    """Test instruction decoding logic"""
    print("=== Testing Instruction Decoding ===")
    
    # Test cases: (instruction_hex, expected_opcode, expected_funct3, expected_funct7, description)
    test_cases = [
        (0x00500093, 0b0010011, 0b000, 0, "addi x1, x0, 5"),
        (0x00A00113, 0b0010011, 0b000, 0, "addi x2, x0, 10"),
        (0x002081B3, 0b0110011, 0b000, 0, "add x3, x1, x2"),
        (0x40208233, 0b0110011, 0b000, 1, "sub x4, x1, x2"),
        (0x000125B7, 0b0110111, 0, 0, "lui x11, 0x12"),
        (0x00012617, 0b0010111, 0, 0, "auipc x12, 0x12"),
        (0x00302023, 0b0100011, 0b010, 0, "sw x3, 0(x0)"),
        (0x00002683, 0b0000011, 0b010, 0, "lw x13, 0(x0)"),
        (0x00208463, 0b1100011, 0b000, 0, "beq x1, x2, 8"),
        (0x008000EF, 0b1101111, 0, 0, "jal x1, 8"),
        (0x00108067, 0b1100111, 0b000, 0, "jalr x0, x1, 1"),
    ]
    
    all_passed = True
    
    for instr_hex, exp_opcode, exp_funct3, exp_funct7, desc in test_cases:
        # Extract fields
        opcode = instr_hex & 0x7F
        funct3 = (instr_hex >> 12) & 0x7
        funct7 = (instr_hex >> 25) & 0x7F
        funct7_bit = (instr_hex >> 30) & 0x1
        
        rd = (instr_hex >> 7) & 0x1F
        rs1 = (instr_hex >> 15) & 0x1F
        rs2 = (instr_hex >> 20) & 0x1F
        
        # Check opcode
        if opcode != exp_opcode:
            print(f"FAIL: {desc}")
            print(f"  Expected opcode: {exp_opcode:07b}, Got: {opcode:07b}")
            all_passed = False
            continue
        
        # Check funct3 for relevant instructions
        if exp_funct3 != 0 and funct3 != exp_funct3:
            print(f"FAIL: {desc}")
            print(f"  Expected funct3: {exp_funct3:03b}, Got: {funct3:03b}")
            all_passed = False
            continue
        
        # Check funct7 bit for sub instruction
        if desc.startswith("sub") and funct7_bit != exp_funct7:
            print(f"FAIL: {desc}")
            print(f"  Expected funct7[5]: {exp_funct7}, Got: {funct7_bit}")
            all_passed = False
            continue
        
        print(f"PASS: {desc}")
        print(f"  Opcode: {opcode:07b}, Funct3: {funct3:03b}, rd: {rd}, rs1: {rs1}, rs2: {rs2}")
    
    return all_passed

def test_immediate_extraction():
    """Test immediate value extraction"""
    print("\n=== Testing Immediate Extraction ===")
    
    test_cases = [
        # (instruction, imm_type, expected_immediate, description)
        (0x00500093, "I", 5, "addi x1, x0, 5"),
        (0xFFF00193, "I", -1, "addi x3, x0, -1"),
        (0x000125B7, "U", 0x12000, "lui x11, 0x12"),
        (0x00302023, "S", 0, "sw x3, 0(x0)"),
        (0x00208463, "B", 8, "beq x1, x2, 8"),
        (0x008000EF, "J", 8, "jal x1, 8"),
        (0x00108067, "I", 1, "jalr x0, x1, 1"),
    ]
    
    all_passed = True
    
    for instr, imm_type, expected, desc in test_cases:
        if imm_type == "I":
            # I-type: bits [31:20]
            imm = instr >> 20
            if imm & 0x800:  # Sign extend
                imm |= 0xFFFFF000
            imm = imm & 0xFFFFFFFF
            if imm >= 0x80000000:
                imm -= 0x100000000
        
        elif imm_type == "U":
            # U-type: bits [31:12] << 12
            imm = (instr & 0xFFFFF000)
        
        elif imm_type == "S":
            # S-type: bits [31:25] + [11:7]
            imm = ((instr >> 25) << 5) | ((instr >> 7) & 0x1F)
            if imm & 0x800:  # Sign extend
                imm |= 0xFFFFF000
            imm = imm & 0xFFFFFFFF
            if imm >= 0x80000000:
                imm -= 0x100000000
        
        elif imm_type == "B":
            # B-type: complex bit arrangement
            imm = (((instr >> 31) & 0x1) << 12) | \
                  (((instr >> 7) & 0x1) << 11) | \
                  (((instr >> 25) & 0x3F) << 5) | \
                  (((instr >> 8) & 0xF) << 1)
            if imm & 0x1000:  # Sign extend
                imm |= 0xFFFFE000
            imm = imm & 0xFFFFFFFF
            if imm >= 0x80000000:
                imm -= 0x100000000
        
        elif imm_type == "J":
            # J-type: complex bit arrangement
            imm = (((instr >> 31) & 0x1) << 20) | \
                  (((instr >> 12) & 0xFF) << 12) | \
                  (((instr >> 20) & 0x1) << 11) | \
                  (((instr >> 21) & 0x3FF) << 1)
            if imm & 0x100000:  # Sign extend
                imm |= 0xFFE00000
            imm = imm & 0xFFFFFFFF
            if imm >= 0x80000000:
                imm -= 0x100000000
        
        if imm == expected:
            print(f"PASS: {desc}")
            print(f"  Immediate: {imm} (0x{imm & 0xFFFFFFFF:08X})")
        else:
            print(f"FAIL: {desc}")
            print(f"  Expected: {expected}, Got: {imm}")
            all_passed = False
    
    return all_passed

def test_alu_operations():
    """Test ALU operations"""
    print("\n=== Testing ALU Operations ===")
    
    test_cases = [
        # (src_a, src_b, alu_control, expected_result, description)
        (5, 10, 0, 15, "ADD: 5 + 10 = 15"),
        (5, 10, 1, -5, "SUB: 5 - 10 = -5"),
        (5, 10, 2, 0, "AND: 5 & 10 = 0"),
        (5, 10, 3, 15, "OR: 5 | 10 = 15"),
        (5, 10, 7, 15, "XOR: 5 ^ 10 = 15"),
        (5, 2, 4, 20, "SLL: 5 << 2 = 20"),
        (5, 10, 5, 1, "SLT: 5 < 10 = 1"),
        (10, 5, 5, 0, "SLT: 10 < 5 = 0"),
    ]
    
    all_passed = True
    
    for src_a, src_b, alu_ctrl, expected, desc in test_cases:
        # Simulate ALU operation
        if alu_ctrl == 0:  # ADD
            result = (src_a + src_b) & 0xFFFFFFFF
        elif alu_ctrl == 1:  # SUB
            result = (src_a - src_b) & 0xFFFFFFFF
        elif alu_ctrl == 2:  # AND
            result = src_a & src_b
        elif alu_ctrl == 3:  # OR
            result = src_a | src_b
        elif alu_ctrl == 4:  # SLL
            result = (src_a << (src_b & 0x1F)) & 0xFFFFFFFF
        elif alu_ctrl == 5:  # SLT
            # Sign extend for comparison
            a_signed = src_a if src_a < 0x80000000 else src_a - 0x100000000
            b_signed = src_b if src_b < 0x80000000 else src_b - 0x100000000
            result = 1 if a_signed < b_signed else 0
        elif alu_ctrl == 7:  # XOR
            result = src_a ^ src_b
        else:
            result = 0
        
        # Convert expected to unsigned for comparison
        if expected < 0:
            expected = expected & 0xFFFFFFFF
        
        if result == expected:
            print(f"PASS: {desc}")
            print(f"  Result: {result} (0x{result:08X})")
        else:
            print(f"FAIL: {desc}")
            print(f"  Expected: {expected} (0x{expected:08X}), Got: {result} (0x{result:08X})")
            all_passed = False
    
    return all_passed

def main():
    """Main test function"""
    print("RISC-V Processor Logic Test")
    print("=" * 40)
    
    test1 = test_instruction_decode()
    test2 = test_immediate_extraction()
    test3 = test_alu_operations()
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"Instruction Decode: {'PASS' if test1 else 'FAIL'}")
    print(f"Immediate Extract:  {'PASS' if test2 else 'FAIL'}")
    print(f"ALU Operations:     {'PASS' if test3 else 'FAIL'}")
    
    if test1 and test2 and test3:
        print("\nAll tests PASSED! Logic appears correct.")
        return 0
    else:
        print("\nSome tests FAILED! Please check the logic.")
        return 1

if __name__ == "__main__":
    exit(main())