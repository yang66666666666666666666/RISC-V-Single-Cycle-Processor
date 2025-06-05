# RISC-V Complete Single Cycle Processor

## 🎯 概述

这是一个完整的RISC-V单周期处理器实现，支持所有主要的指令类型：**R型、I型、U型、S型、B型、J型**指令。

## ✨ 支持的指令类型

### 📋 指令类型对比

| 指令类型 | 描述 | 支持的指令 | 示例 |
|---------|------|-----------|------|
| **R型** | 寄存器-寄存器运算 | ADD, SUB, AND, OR, XOR, SLT | `add x3, x1, x2` |
| **I型** | 立即数运算和加载 | ADDI, ANDI, ORI, XORI, LW | `addi x1, x0, 5` |
| **U型** | 上位立即数 | LUI, AUIPC | `lui x8, 1` |
| **S型** | 存储指令 | SW | `sw x3, 0(x0)` |
| **B型** | 分支指令 | BEQ, BNE, BLT, BGE | `beq x1, x2, 8` |
| **J型** | 跳转指令 | JAL, JALR | `jal x1, 8` |

## 🔧 文件结构

### 核心文件
- **`src/riscv_processor_complete.v`** - 完整处理器实现
- **`src/riscv_processor_complete_tb.v`** - 完整测试程序
- **`src/riscv_processor_fixed.v`** - 基础版本（向后兼容）
- **`src/riscv_processor_tb_fixed.v`** - 基础版本测试

### 构建和运行
```bash
# 运行完整版本（推荐）
make complete

# 运行基础版本
make basic

# 查看所有选项
make help
```

## 🧪 测试程序详解

完整版本的测试程序包含以下指令序列：

### I型指令测试
```assembly
addi x1, x0, 5      # x1 = 5
addi x2, x0, 10     # x2 = 10
addi x3, x0, 12     # x3 = 12
```

### R型指令测试
```assembly
add  x3, x1, x2     # x3 = 5 + 10 = 15
sub  x4, x1, x2     # x4 = 5 - 10 = -5
and  x5, x1, x2     # x5 = 5 & 10 = 0
or   x6, x1, x2     # x6 = 5 | 10 = 15
xor  x7, x1, x2     # x7 = 5 ^ 10 = 15
```

### U型指令测试
```assembly
lui   x8, 1         # x8 = 1 << 12 = 4096
auipc x9, 1         # x9 = PC + (1 << 12)
```

### S型指令测试
```assembly
sw x3, 0(x0)        # 存储x3到地址0
sw x4, 4(x0)        # 存储x4到地址4
```

### I型加载指令测试
```assembly
lw x10, 0(x0)       # 从地址0加载到x10
lw x11, 4(x0)       # 从地址4加载到x11
```

### B型指令测试
```assembly
beq x1, x2, 8       # 如果x1==x2则跳转
bne x1, x2, 8       # 如果x1!=x2则跳转
blt x1, x2, 8       # 如果x1<x2则跳转
```

### J型指令测试
```assembly
jal  x1, 8          # 跳转并链接
jalr x0, x1, 0      # 寄存器跳转
```

## 🏗️ 架构特性

### 处理器组件
1. **程序计数器 (PC)** - 32位，支持顺序和跳转
2. **指令内存** - 64字×32位
3. **寄存器文件** - 32个32位寄存器
4. **ALU** - 支持算术、逻辑、比较运算
5. **数据内存** - 64字×32位
6. **控制单元** - 完整的指令解码和控制信号生成

### 数据路径
- **PC源选择** - 支持PC+4、分支目标、跳转目标
- **ALU源选择** - 寄存器或立即数
- **结果源选择** - ALU结果、内存数据、PC+4、立即数
- **立即数扩展** - 支持所有指令格式的立即数

### 控制逻辑
- **主解码器** - 根据操作码生成控制信号
- **ALU解码器** - 根据funct3/funct7生成ALU控制
- **分支单元** - 处理各种分支条件

## 📊 仿真结果

### 预期输出示例
```
=== Complete RISC-V Single Cycle Processor Test ===
Testing R, I, U, S, B, J type instructions

--- I-type Instructions ---
Cycle 0 - PC: 00000000, Instruction: 00500093 (addi x1, x0, 5)
  Expected: x1 = 5

--- R-type Instructions ---
Cycle 3 - PC: 0000000c, Instruction: 002081b3 (add x3, x1, x2)
  ALU Result: 0000000f (Expected: 5 + 10 = 15)

--- U-type Instructions ---
Cycle 8 - PC: 00000020, Instruction: 00001437 (lui x8, 1)
  Expected: x8 = 4096 (1 << 12)

--- S-type Instructions ---
Cycle 10 - PC: 00000028, Instruction: 00302023 (sw x3, 0(x0))
  Write Data: 0000000f (Should store x3 value)

--- B-type Instructions ---
INFO: Branch instruction detected at PC 00000048

--- J-type Instructions ---
INFO: JAL instruction detected at PC 00000058
```

## 🔍 调试和验证

### 信号监控
- `pc_out` - 当前程序计数器值
- `instruction_out` - 当前执行的指令
- `alu_result_out` - ALU运算结果
- `write_data_out` - 写入内存的数据
- `read_data_out` - 从内存读取的数据

### 验证点
1. **指令获取** - PC正确递增，指令正确读取
2. **寄存器操作** - 读写操作正确，x0始终为0
3. **ALU运算** - 各种运算结果正确
4. **内存操作** - 存储和加载操作正确
5. **控制流** - 分支和跳转逻辑正确

## 🚀 使用方法

### 快速开始
```bash
# 克隆或下载项目
cd RISC-V-Single-Cycle-Processor

# 运行完整版本测试
make complete

# 查看波形（如果支持）
gtkwave riscv_processor_complete.vcd
```

### Windows用户
```cmd
# 使用Vivado
run_vivado.bat

# 或使用替代方案
run_alternative.bat
```

### 在线仿真
参考 `ONLINE_SIMULATION_GUIDE.md` 使用在线仿真器。

## 📚 教育价值

### 学习目标
1. **RISC-V指令集架构** - 理解不同指令类型的编码和执行
2. **单周期处理器设计** - 掌握基本的处理器架构
3. **数字逻辑设计** - 学习组合逻辑和时序逻辑
4. **Verilog HDL** - 实践硬件描述语言

### 适用课程
- 计算机组成原理
- 数字逻辑设计
- 计算机体系结构
- FPGA设计

## 🔧 扩展和定制

### 可能的扩展
1. **流水线实现** - 将单周期改为多周期流水线
2. **缓存系统** - 添加指令和数据缓存
3. **异常处理** - 实现中断和异常机制
4. **更多指令** - 支持乘除法、浮点运算等

### 定制选项
- 修改内存大小
- 添加外设接口
- 实现不同的分支预测
- 优化关键路径时序

## 📈 性能特征

### 资源使用（典型FPGA）
- **LUT**: ~500-800个
- **寄存器**: ~200-300个
- **BRAM**: 2-4个块
- **最大频率**: 50-100MHz

### 指令吞吐量
- **CPI**: 1（单周期）
- **指令/秒**: 等于时钟频率
- **内存带宽**: 每周期1次访问

## 🤝 贡献和反馈

欢迎提交问题报告、功能请求或改进建议！

### 常见问题
1. **仿真不工作** - 检查工具安装和文件路径
2. **指令执行错误** - 验证指令编码和控制逻辑
3. **时序问题** - 检查时钟和复位信号

---

**注意**: 这是一个教育用途的处理器实现，专注于清晰性和可理解性，而非最优性能。