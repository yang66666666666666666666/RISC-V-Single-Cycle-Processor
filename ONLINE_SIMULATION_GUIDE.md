# 在线仿真指南 - 无需安装Vivado

如果您遇到Vivado安装问题，可以使用在线仿真工具来测试RISC-V处理器。

## 🌐 推荐的在线仿真平台

### 1. EDA Playground（推荐）
- **网址**: https://www.edaplayground.com/
- **特点**: 免费、支持多种仿真器、无需注册
- **支持**: SystemVerilog, Verilog, VHDL

### 2. HDLBits
- **网址**: https://hdlbits.01xz.net/wiki/Iverilog
- **特点**: 教育导向、内置练习
- **支持**: Verilog

### 3. Verilog Online
- **网址**: https://verilogonline.com/
- **特点**: 简单易用、快速测试
- **支持**: Verilog

## 📋 使用步骤

### 在EDA Playground上运行

1. **打开EDA Playground**
   - 访问 https://www.edaplayground.com/

2. **设置仿真器**
   - 选择 "Icarus Verilog 0.9.7" 作为仿真器
   - 语言选择 "SystemVerilog/Verilog"

3. **复制设计文件**
   - 在左侧"design.sv"窗口中粘贴以下内容：

```verilog
// 复制 src/riscv_processor_fixed.v 的全部内容
// 文件内容从这里开始...
`timescale 1ns / 1ps

// [在这里粘贴 riscv_processor_fixed.v 的完整内容]
```

4. **复制测试文件**
   - 在右侧"testbench.sv"窗口中粘贴：

```verilog
// 复制 src/riscv_processor_tb_fixed.v 的全部内容
// 文件内容从这里开始...
`timescale 1ns / 1ps

// [在这里粘贴 riscv_processor_tb_fixed.v 的完整内容]
```

5. **运行仿真**
   - 点击 "Run" 按钮
   - 查看右下角的"Log"窗口获取结果

## 📁 文件内容快速复制

### 设计文件 (design.sv)
您需要复制 `src/riscv_processor_fixed.v` 的完整内容。

### 测试文件 (testbench.sv)
您需要复制 `src/riscv_processor_tb_fixed.v` 的完整内容。

## 🔍 预期结果

成功的仿真应该显示类似以下的输出：

```
=== RISC-V Single Cycle Processor Test ===
Cycle 0 - PC: 00000000, Instruction: 00500093 (addi x1, x0, 5)
Cycle 1 - PC: 00000004, Instruction: 00a00113 (addi x2, x0, 10)
Cycle 2 - PC: 00000008, Instruction: 002081b3 (add x3, x1, x2)
  ALU Result: 0000000f (Expected: 15 = 0x0000000F) ✓
Cycle 3 - PC: 0000000c, Instruction: 40208233 (sub x4, x1, x2)
  ALU Result: fffffffb (Expected: -5 = 0xFFFFFFFB) ✓
...
=== Test Completed Successfully ===
```

## 🛠️ 故障排除

### 常见问题

1. **编译错误**
   - 确保复制了完整的文件内容
   - 检查是否有语法错误

2. **仿真不运行**
   - 确认选择了正确的仿真器
   - 检查testbench模块名是否正确

3. **输出不正确**
   - 验证设计文件是否完整
   - 检查时钟和复位信号

### 调试技巧

1. **添加调试输出**
   ```verilog
   always @(posedge clk) begin
       $display("PC: %h, Instruction: %h", pc_out, instruction_out);
   end
   ```

2. **检查信号值**
   ```verilog
   initial begin
       $monitor("Time: %0t, PC: %h", $time, pc_out);
   end
   ```

## 🎯 替代方案

### 如果在线仿真不可用

1. **安装Icarus Verilog**
   - Windows: http://bleyer.org/icarus/
   - Linux: `sudo apt install iverilog`
   - macOS: `brew install icarus-verilog`

2. **使用WSL (Windows)**
   ```bash
   wsl --install
   sudo apt install iverilog gtkwave
   ```

3. **安装Vivado WebPACK**
   - 下载: https://www.xilinx.com/support/download.html
   - 免费版本，功能完整

## 📚 学习资源

- [Verilog教程](https://www.chipverify.com/verilog/verilog-tutorial)
- [RISC-V规范](https://riscv.org/specifications/)
- [数字设计基础](https://www.nandland.com/)

## 💡 提示

- 在线仿真适合学习和测试
- 对于大型项目，建议安装本地工具
- 保存您的代码到本地文件
- 定期备份重要的设计文件

---

如果您需要更多帮助，请查看 `WINDOWS_SETUP.md` 或运行 `run_alternative.bat`。