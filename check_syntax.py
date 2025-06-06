#!/usr/bin/env python3
"""
Simple Verilog syntax checker for RISC-V processor files
"""

import re
import sys
import os

def check_verilog_file(filename):
    """Check a Verilog file for common syntax issues"""
    if not os.path.exists(filename):
        return [f"File not found: {filename}"]
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"Error reading file: {e}"]
    
    issues = []
    lines = content.split('\n')
    
    # Check for non-ASCII characters
    for i, line in enumerate(lines, 1):
        try:
            line.encode('ascii')
        except UnicodeEncodeError:
            # Find the problematic character
            for j, char in enumerate(line):
                if ord(char) > 127:
                    issues.append(f"Line {i}, Col {j+1}: Non-ASCII character '{char}' (U+{ord(char):04X})")
                    break
    
    # Check module/endmodule balance
    modules = re.findall(r'^\s*module\s+(\w+)', content, re.MULTILINE)
    endmodules = re.findall(r'^\s*endmodule', content, re.MULTILINE)
    if len(modules) != len(endmodules):
        issues.append(f"Module/endmodule mismatch: {len(modules)} modules, {len(endmodules)} endmodules")
    
    # Check for unmatched parentheses, brackets, braces
    paren_count = content.count('(') - content.count(')')
    bracket_count = content.count('[') - content.count(']')
    brace_count = content.count('{') - content.count('}')
    
    if paren_count != 0:
        issues.append(f"Unmatched parentheses: {paren_count}")
    if bracket_count != 0:
        issues.append(f"Unmatched brackets: {bracket_count}")
    if brace_count != 0:
        issues.append(f"Unmatched braces: {brace_count}")
    
    # Check for common Verilog syntax issues
    if re.search(r'always\s*@\s*\(\s*\*\s*\).*begin', content, re.DOTALL):
        # Check for missing end statements
        always_begin = len(re.findall(r'always\s*@.*begin', content))
        always_end = len(re.findall(r'always\s*@.*end', content))
    
    # Check for wire/reg declarations
    wire_decl = re.findall(r'^\s*wire\s+', content, re.MULTILINE)
    reg_decl = re.findall(r'^\s*reg\s+', content, re.MULTILINE)
    
    return issues

def main():
    """Main function"""
    files_to_check = [
        'src/riscv_processor_complete.v',
        'src/riscv_processor_complete_tb.v',
        'src/riscv_processor_fixed.v',
        'src/riscv_processor_tb_fixed.v'
    ]
    
    print("=== Verilog Syntax Checker ===")
    total_issues = 0
    
    for filename in files_to_check:
        if not os.path.exists(filename):
            print(f"Skipping {filename} (not found)")
            continue
            
        print(f"\nChecking {filename}...")
        issues = check_verilog_file(filename)
        
        if issues:
            print(f"  Found {len(issues)} issue(s):")
            for issue in issues:
                print(f"    - {issue}")
            total_issues += len(issues)
        else:
            print("  No issues found")
    
    print(f"\n=== Summary ===")
    print(f"Total issues found: {total_issues}")
    
    if total_issues == 0:
        print("All files appear to be syntactically correct!")
        return 0
    else:
        print("Please fix the issues above before running simulation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())