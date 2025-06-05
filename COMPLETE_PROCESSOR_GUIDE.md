# 完整RISC-V单周期处理器指南

## 🎯 概述

本项目现在包含一个**完整的RISC-V单周期处理器**，支持所有主要指令类型：

- ✅ **R型指令** (Register-Register)
- ✅ **I型指令** (Immediate)  
- ✅ **U型指令** (Upper Immediate)
- ✅ **S型指令** (Store)
- ✅ **B型指令** (Branch)
- ✅ **J型指令** (Jump)

## 📁 文件结构

### 🔧 核心设计文件
- **`src/riscv_processor_complete.v`** - 完整处理器实现（推荐使用）
- **`src/riscv_processor_complete_tb.v`** - 完整测试程序
- **`src/riscv_processor_fixed.v`** - 基础版本（向后兼容）
- **`src/riscv_processor_tb_fixed.v`** - 基础测试程序

### 🖥️ Windows支持
- **`run_vivado_complete.bat`** - 完整版本Vivado项目创建
- **`create_vivado_project_complete.tcl`** - 完整版本TCL脚本
- **`run_vivado.bat`** - 基础版本（向后兼容）

### 🔨 构建系统
- **`Makefile`** - 支持完整版本和基础版本
- **`constraints/basys3.xdc`** - FPGA约束文件

## 🚀 快速开始

### Windows用户（推荐）

#### 方法1：使用Vivado（最佳体验）
```cmd
# 创建完整版本项目
run_vivado_complete.bat

# 或创建基础版本项目
run_vivado.bat
```

#### 方法2：在线仿真（无需安装）
1. 访问 https://www.edaplayground.com/
2. 复制 `src/riscv_processor_complete.v` 到设计窗口
3. 复制 `src/riscv_processor_complete_tb.v` 到测试窗口
4. 选择 "Icarus Verilog" 仿真器
5. 点击 "Run" 查看结果

### Linux/Unix/macOS用户

```bash
# 测试完整版本（默认）
make complete

# 测试基础版本
make basic

# 查看所有选项
make help

# 清理生成文件
make clean
```

## 📋 支持的指令详细说明

### R型指令 (Register-Register)
| 指令 | 功能 | 示例 | 说明 |
|------|------|------|------|
| `add` | 加法 | `add x3, x1, x2` | x3 = x1 + x2 |
| `sub` | 减法 | `sub x4, x1, x2` | x4 = x1 - x2 |
| `and` | 按位与 | `and x5, x1, x2` | x5 = x1 & x2 |
| `or` | 按位或 | `or x6, x1, x2` | x6 = x1 \| x2 |
| `xor` | 按位异或 | `xor x7, x1, x2` | x7 = x1 ^ x2 |
| `sll` | 逻辑左移 | `sll x9, x1, x2` | x9 = x1 << x2 |
| `slt` | 有符号比较 | `slt x10, x1, x2` | x10 = (x1 < x2) ? 1 : 0 |

### I型指令 (Immediate)
| 指令 | 功能 | 示例 | 说明 |
|------|------|------|------|
| `addi` | 立即数加法 | `addi x1, x0, 5` | x1 = x0 + 5 |
| `slli` | 立即数逻辑左移 | `slli x4, x1, 2` | x4 = x1 << 2 |
| `slti` | 立即数有符号比较 | `slti x5, x1, 2` | x5 = (x1 < 2) ? 1 : 0 |
| `lw` | 加载字 | `lw x13, 0(x0)` | x13 = memory[x0+0] |
| `jalr` | 跳转并链接寄存器 | `jalr x0, x1, 1` | PC = x1 + 1, x0 = PC+4 |

### U型指令 (Upper Immediate)
| 指令 | 功能 | 示例 | 说明 |
|------|------|------|------|
| `lui` | 加载高位立即数 | `lui x11, 0x12` | x11 = 0x12000 |
| `auipc` | PC加高位立即数 | `auipc x12, 0x12` | x12 = PC + 0x12000 |

### S型指令 (Store)
| 指令 | 功能 | 示例 | 说明 |
|------|------|------|------|
| `sw` | 存储字 | `sw x3, 0(x0)` | memory[x0+0] = x3 |

### B型指令 (Branch)
| 指令 | 功能 | 示例 | 说明 |
|------|------|------|------|
| `beq` | 相等分支 | `beq x1, x2, 8` | if (x1 == x2) PC += 8 |
| `bne` | 不等分支 | `bne x1, x2, 8` | if (x1 != x2) PC += 8 |
| `blt` | 小于分支 | `blt x1, x2, 8` | if (x1 < x2) PC += 8 |
| `bge` | 大于等于分支 | `bge x1, x2, 8` | if (x1 >= x2) PC += 8 |

### J型指令 (Jump)
| 指令 | 功能 | 示例 | 说明 |
|------|------|------|------|
| `jal` | 跳转并链接 | `jal x1, 8` | x1 = PC+4, PC += 8 |

## 🧪 测试程序示例

完整版本包含以下测试程序：

```assembly
# I型指令测试
addi x1, x0, 5      # x1 = 5
addi x2, x0, 10     # x2 = 10
addi x3, x0, -1     # x3 = -1
slli x4, x1, 2      # x4 = x1 << 2 = 20
slti x5, x1, 2      # x5 = (5 < 2) ? 1 : 0 = 0

# R型指令测试
add  x3, x1, x2     # x3 = 5 + 10 = 15
sub  x4, x1, x2     # x4 = 5 - 10 = -5
and  x5, x1, x2     # x5 = 5 & 10 = 0
or   x6, x1, x2     # x6 = 5 | 10 = 15
xor  x7, x1, x2     # x7 = 5 ^ 10 = 15
sll  x9, x1, x2     # x9 = 5 << 10 = 5120
slt  x10, x1, x2    # x10 = (5 < 10) ? 1 : 0 = 1

# U型指令测试
lui  x11, 0x12      # x11 = 0x12000
auipc x12, 0x12     # x12 = PC + 0x12000

# S型指令测试
sw   x3, 0(x0)      # memory[0] = x3
sw   x4, 4(x0)      # memory[1] = x4

# 加载指令测试
lw   x13, 0(x0)     # x13 = memory[0]
lw   x14, 4(x0)     # x14 = memory[1]

# B型指令测试
beq  x1, x2, 8      # 不跳转（5 != 10）
bne  x1, x2, 8      # 跳转（5 != 10）
blt  x1, x2, 8      # 跳转（5 < 10）
bge  x1, x2, 8      # 不跳转（5 < 10）

# J型指令测试
jal  x1, 8          # 跳转并保存返回地址
jalr x0, x1, 1      # 跳转到x1+1地址
```

## 📊 预期结果

运行测试后，您应该看到：

```
=== Complete RISC-V Single Cycle Processor Test ===
Testing R, I, U, S, B, J type instructions

--- I-type Instructions ---
Cycle 0 - PC: 00000000, Instruction: 00500093 (addi x1, x0, 5)
  Expected: x1 = 5
Cycle 1 - PC: 00000004, Instruction: 00a00113 (addi x2, x0, 10)
  Expected: x2 = 10

--- R-type Instructions ---
Cycle 5 - PC: 00000014, Instruction: 002081b3 (add x3, x1, x2)
  ALU Result: 0000000f (Expected: 5 + 10 = 15)

--- U-type Instructions ---
Cycle 12 - PC: 00000030, Instruction: 000125b7 (lui x11, 0x12)
  Reg Write Data: 00012000 (Expected: 0x12000)

=== Test Completed Successfully ===
All RISC-V instruction types (R, I, U, S, B, J) have been tested!
```

## 🔧 技术规格

### 处理器特性
- **架构**: 32位RISC-V单周期
- **指令集**: RV32I基础指令集
- **寄存器**: 32个通用寄存器（x0-x31）
- **内存**: 64字指令内存 + 64字数据内存
- **时钟频率**: 50-100 MHz（典型FPGA）

### 模块组成
- **程序计数器（PC）**: 指令地址生成
- **指令内存**: 存储程序指令
- **控制单元**: 指令解码和控制信号生成
- **寄存器文件**: 32个通用寄存器
- **ALU**: 算术逻辑单元
- **数据内存**: 数据存储
- **立即数扩展**: 支持所有立即数格式

### 控制信号
- **PC源选择**: 支持顺序执行、分支、跳转
- **ALU源选择**: 寄存器或立即数
- **结果源选择**: ALU、内存、PC+4、立即数
- **内存写使能**: 存储指令控制
- **寄存器写使能**: 寄存器更新控制

## 🎓 教育价值

这个完整的RISC-V处理器非常适合：

1. **计算机体系结构课程**
   - 理解处理器设计原理
   - 学习指令集架构
   - 掌握数据通路设计

2. **数字逻辑设计**
   - Verilog HDL编程
   - 组合逻辑和时序逻辑
   - 模块化设计方法

3. **FPGA开发**
   - 硬件描述语言实践
   - 综合和实现流程
   - 时序约束和优化

4. **RISC-V学习**
   - 指令格式理解
   - 汇编语言编程
   - 处理器微架构

## 🔍 故障排除

### 常见问题

1. **Vivado未找到**
   ```
   ERROR: Vivado not found in PATH
   ```
   **解决方案**: 
   - 安装Vivado WebPACK
   - 添加到系统PATH: `C:\Xilinx\Vivado\2024.1\bin`
   - 或使用 `run_alternative.bat`

2. **仿真错误**
   ```
   ERROR: Module not found
   ```
   **解决方案**:
   - 确保所有源文件存在
   - 检查模块名称拼写
   - 验证文件路径

3. **时序错误**
   ```
   WARNING: Setup time violation
   ```
   **解决方案**:
   - 降低时钟频率
   - 检查时序约束
   - 优化关键路径

### 调试技巧

1. **使用VCD波形文件**
   ```bash
   make complete
   gtkwave riscv_processor_complete.vcd
   ```

2. **添加调试输出**
   ```verilog
   always @(posedge clk) begin
       $display("PC: %h, Instr: %h", pc_out, instruction_out);
   end
   ```

3. **检查寄存器值**
   - 在测试程序中添加寄存器监控
   - 使用Vivado仿真器查看内部信号

## 📚 参考资料

- [RISC-V指令集手册](https://riscv.org/specifications/)
- [Verilog HDL教程](https://www.chipverify.com/verilog/verilog-tutorial)
- [Vivado设计套件用户指南](https://www.xilinx.com/support/documentation/)
- [数字设计与计算机体系结构](https://www.amazon.com/Digital-Design-Computer-Architecture-Harris/dp/0123944244)

## 🤝 贡献

欢迎提交问题报告和改进建议！

---

**恭喜！您现在拥有一个完整功能的RISC-V单周期处理器，支持所有主要指令类型！** 🎉