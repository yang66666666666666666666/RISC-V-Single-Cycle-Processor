# RISC-V Single Cycle Processor - Windows Compatible

这是一个完整的RISC-V单周期处理器实现，专门为Windows环境优化，支持Vivado和其他仿真工具。

## 🚀 快速开始

### Windows用户（推荐）

1. **使用Vivado（最简单）**
   ```cmd
   # 双击运行或在命令行执行
   run_vivado.bat
   ```

2. **手动创建Vivado项目**
   - 打开Vivado
   - 运行TCL脚本：`source create_vivado_project.tcl`
   - 或按照 `WINDOWS_SETUP.md` 中的详细说明操作

### Linux/Unix用户

```bash
# 使用Icarus Verilog
make iverilog

# 或者直接编译运行
iverilog -o processor.vvp src/riscv_processor_fixed.v src/riscv_processor_tb_fixed.v
vvp processor.vvp
```

## 📁 项目结构

```
RISC-V-Single-Cycle-Processor/
├── src/
│   ├── riscv_processor_fixed.v      # 修复后的主处理器设计
│   ├── riscv_processor_tb_fixed.v   # 修复后的测试文件
│   ├── riscv_processor.v            # 原始处理器设计
│   └── riscv_processor_tb.v         # 原始测试文件
├── vivado_project/                  # Vivado项目文件（生成）
├── create_vivado_project.tcl        # Vivado项目创建脚本
├── run_vivado.bat                   # Windows一键运行脚本
├── Makefile                         # Linux/Unix构建文件
├── WINDOWS_SETUP.md                 # Windows详细设置指南
├── README_UPDATED.md                # 本文件
└── README.md                        # 原始项目说明
```

## 🔧 处理器特性

### 支持的指令集
- **I-type**: `addi` (立即数加法)
- **R-type**: `add`, `sub`, `and`, `or` (寄存器间运算)
- **Load/Store**: `lw`, `sw` (内存读写)
- **Branch**: `beq` (条件分支)

### 架构组件
- **32位数据路径**
- **32个通用寄存器** (x0-x31，x0恒为0)
- **64字指令内存**
- **64字数据内存**
- **完整的控制单元**
- **ALU支持多种运算**

## 🧪 测试程序

处理器预装了以下测试程序：

```assembly
addi x1, x0, 5      # x1 = 5
addi x2, x0, 10     # x2 = 10
add  x3, x1, x2     # x3 = 15 (5 + 10)
sub  x4, x1, x2     # x4 = -5 (5 - 10)
and  x5, x1, x2     # x5 = 0 (5 & 10)
or   x6, x1, x2     # x6 = 15 (5 | 10)
sw   x3, 0(x0)      # 存储15到内存地址0
lw   x7, 0(x0)      # 从内存地址0加载到x7
```

## 📊 仿真结果

成功的仿真应该显示：

```
=== RISC-V Single Cycle Processor Test ===
Cycle 0 - PC: 00000000, Instruction: 00500093 (addi x1, x0, 5)
Cycle 1 - PC: 00000004, Instruction: 00a00113 (addi x2, x0, 10)
Cycle 2 - PC: 00000008, Instruction: 002081b3 (add x3, x1, x2)
  ALU Result: 0000000f (Expected: 15 = 0x0000000F) ✓
Cycle 3 - PC: 0000000c, Instruction: 40208233 (sub x4, x1, x2)
  ALU Result: fffffffb (Expected: -5 = 0xFFFFFFFB) ✓
...
```

## 🛠️ 开发环境要求

### Windows
- **Xilinx Vivado 2024.1+** (推荐)
- 或 **ModelSim Intel FPGA Edition**
- 或 **WSL + Icarus Verilog**

### Linux/macOS
- **Icarus Verilog** (`sudo apt install iverilog`)
- **GTKWave** (波形查看器)
- **Make** (构建工具)

## 🔍 调试和验证

### 查看波形
1. 仿真会生成 `riscv_processor.vcd` 文件
2. 使用GTKWave打开：`gtkwave riscv_processor.vcd`
3. 在Vivado中直接查看仿真波形

### 验证要点
- ✅ PC正确递增（每周期+4）
- ✅ 指令正确解码
- ✅ ALU运算结果正确
- ✅ 寄存器写入正确
- ✅ 内存读写正常

## 🚀 扩展功能

### 添加新指令
1. 修改 `main_decoder` 模块添加新的opcode
2. 更新 `alu_decoder` 如需新的ALU操作
3. 在 `alu` 模块中实现新运算
4. 更新测试程序验证

### 性能优化
- 当前设计可在大多数FPGA上达到50-100MHz
- 资源使用量低，适合小型FPGA
- 功耗优化，适合电池供电应用

## 📚 学习资源

- [RISC-V规范](https://riscv.org/specifications/)
- [Vivado用户指南](https://docs.xilinx.com/v/u/en-US/ug910-vivado-getting-started)
- [数字设计与计算机体系结构](https://www.amazon.com/Digital-Design-Computer-Architecture-Harris/dp/0123944244)

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发指南
1. Fork本仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 基于原始RISC-V规范
- 参考了多个开源RISC-V实现
- 感谢所有贡献者和测试者

---

**注意**: 如果遇到任何问题，请查看 `WINDOWS_SETUP.md` 获取详细的故障排除指南。