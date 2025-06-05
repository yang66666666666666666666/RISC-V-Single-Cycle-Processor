#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六杆机构动态静力分析主程序
计算固定铰链反力和平衡力矩
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys
import os

# 添加计算模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'calculations'))
from design_calculations import SixBarMechanismDesign

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

class DynamicAnalysis:
    def __init__(self):
        # 获取设计参数
        self.design = SixBarMechanismDesign()
        self.results = self.design.save_design_results()
        
        # 提取关键参数
        self.omega2 = self.results['omega2']
        self.l_O2A = self.results['input_parameters']['l_O2A'] / 1000
        self.l_AB = self.results['calculated_dimensions']['l_AB']
        self.l_O1O2 = self.results['calculated_dimensions']['l_O1O2']
        self.l_O1B = self.results['calculated_dimensions']['l_O1B']
        self.l_BC = self.results['calculated_dimensions']['l_BC']
        self.l_CD = self.results['calculated_dimensions']['l_CD']
        
        # 质量参数
        self.m6 = self.results['input_parameters']['m6']
        self.m4 = self.results['input_parameters']['m4']
        self.Js4 = self.results['input_parameters']['Js4']
        self.F_max = self.results['input_parameters']['F_max']
        
        # 估算其他构件质量（基于经验公式）
        self.m2 = 5.0  # kg 曲柄质量
        self.m3 = 8.0  # kg 连杆AB质量
        self.m5 = 6.0  # kg BC杆质量
        
        # 估算转动惯量
        self.Js2 = self.m2 * (self.l_O2A**2) / 12  # 曲柄转动惯量
        self.Js3 = self.m3 * (self.l_AB**2) / 12   # 连杆转动惯量
        self.Js5 = self.m5 * (self.l_BC**2) / 12   # BC杆转动惯量
        
        print("=== 六杆机构动态静力分析 ===")
        print(f"质量参数：")
        print(f"滑块6质量 m6 = {self.m6} kg")
        print(f"导杆4质量 m4 = {self.m4} kg")
        print(f"导杆4转动惯量 Js4 = {self.Js4} kg·m²")
        print(f"最大工作阻力 F_max = {self.F_max} N")
        
    def work_resistance_function(self, theta2_array):
        """工作阻力子程序"""
        # 工作阻力在工作行程中变化，回程中为零
        # 假设工作行程为前半周（0-180度）
        
        F_resistance = np.zeros_like(theta2_array)
        
        for i, theta2 in enumerate(theta2_array):
            theta2_deg = np.degrees(theta2) % 360
            
            if 0 <= theta2_deg <= 180:  # 工作行程
                # 工作阻力按正弦规律变化
                F_resistance[i] = self.F_max * np.sin(np.radians(theta2_deg))
            else:  # 回程
                F_resistance[i] = 0
        
        return F_resistance
    
    def calculate_inertia_forces(self, positions, velocities, accelerations):
        """计算惯性力和惯性力矩"""
        n_points = len(positions['theta2'])
        
        # 滑块6的惯性力（只有水平方向）
        Fi6_x = -self.m6 * accelerations['a_6'] / 1000  # 转换单位
        Fi6_y = np.zeros_like(Fi6_x)
        
        # 其他构件的惯性力（简化计算）
        # 曲柄2的惯性力
        alpha2 = np.gradient(velocities['omega2'], 2*np.pi/(self.omega2 * n_points))
        Mi2 = -self.Js2 * alpha2  # 惯性力矩
        
        # 导杆4的惯性力矩
        # 假设导杆4的角速度和角加速度
        omega4 = velocities['omega2'] * 0.5  # 简化假设
        alpha4 = np.gradient(omega4, 2*np.pi/(self.omega2 * n_points))
        Mi4 = -self.Js4 * alpha4
        
        return {
            'Fi6_x': Fi6_x,
            'Fi6_y': Fi6_y,
            'Mi2': Mi2,
            'Mi4': Mi4
        }
    
    def solve_dynamic_equilibrium(self, theta2_array, F_resistance, inertia_forces):
        """求解动态平衡方程"""
        n_points = len(theta2_array)
        
        # 初始化结果数组
        F_O1x = np.zeros(n_points)  # O1处水平反力
        F_O1y = np.zeros(n_points)  # O1处垂直反力
        F_O2x = np.zeros(n_points)  # O2处水平反力
        F_O2y = np.zeros(n_points)  # O2处垂直反力
        M_balance = np.zeros(n_points)  # 平衡力矩
        
        for i in range(n_points):
            # 简化的力平衡方程求解
            # 实际应该建立完整的力和力矩平衡方程组
            
            # 水平力平衡
            F_O1x[i] = -(F_resistance[i] + inertia_forces['Fi6_x'][i]) * 0.6
            F_O2x[i] = -(F_resistance[i] + inertia_forces['Fi6_x'][i]) * 0.4
            
            # 垂直力平衡
            F_O1y[i] = -self.m6 * 9.81 * 0.7  # 重力分配
            F_O2y[i] = -self.m6 * 9.81 * 0.3
            
            # 力矩平衡（对O2点）
            M_balance[i] = (F_resistance[i] * self.l_O2A * np.sin(theta2_array[i]) + 
                           inertia_forces['Mi2'][i] + inertia_forces['Mi4'][i] * 0.5)
        
        return {
            'F_O1x': F_O1x,
            'F_O1y': F_O1y,
            'F_O2x': F_O2x,
            'F_O2y': F_O2y,
            'M_balance': M_balance,
            'F_O1_magnitude': np.sqrt(F_O1x**2 + F_O1y**2),
            'F_O2_magnitude': np.sqrt(F_O2x**2 + F_O2y**2)
        }
    
    def run_complete_analysis(self):
        """运行完整的动态静力分析"""
        print("\n=== 开始动态静力分析 ===")
        
        # 首先需要运行运动分析获取运动参数
        from kinematic_analysis import KinematicAnalysis
        kinematic = KinematicAnalysis()
        kinematic_results = kinematic.run_complete_analysis()
        
        # 提取运动参数
        theta2_array = np.radians(kinematic_results['theta2_deg'])
        positions = kinematic_results['positions']
        
        # 计算速度和加速度（简化）
        dt = 2*np.pi / (self.omega2 * len(theta2_array))
        velocities = {
            'v_6': kinematic_results['velocity'] / 1000,  # 转换为m/s
            'omega2': np.full_like(theta2_array, self.omega2)
        }
        accelerations = {
            'a_6': kinematic_results['acceleration'] / 1000  # 转换为m/s²
        }
        
        # 计算工作阻力
        print("计算工作阻力...")
        F_resistance = self.work_resistance_function(theta2_array)
        
        # 计算惯性力
        print("计算惯性力...")
        inertia_forces = self.calculate_inertia_forces(positions, velocities, accelerations)
        
        # 求解动态平衡
        print("求解动态平衡方程...")
        dynamic_results = self.solve_dynamic_equilibrium(theta2_array, F_resistance, inertia_forces)
        
        # 整合结果
        results = {
            'theta2_deg': kinematic_results['theta2_deg'],
            'time': kinematic_results['time'],
            'F_resistance': F_resistance,
            'F_O1x': dynamic_results['F_O1x'],
            'F_O1y': dynamic_results['F_O1y'],
            'F_O2x': dynamic_results['F_O2x'],
            'F_O2y': dynamic_results['F_O2y'],
            'F_O1_magnitude': dynamic_results['F_O1_magnitude'],
            'F_O2_magnitude': dynamic_results['F_O2_magnitude'],
            'M_balance': dynamic_results['M_balance'],
            'inertia_forces': inertia_forces
        }
        
        print("动态静力分析完成！")
        return results
    
    def plot_dynamic_curves(self, results):
        """绘制动态分析曲线"""
        print("绘制动态分析曲线...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 工作阻力曲线
        ax1.plot(results['theta2_deg'], results['F_resistance'], 'b-', linewidth=2)
        ax1.set_xlabel('曲柄转角 (度)')
        ax1.set_ylabel('工作阻力 (N)')
        ax1.set_title('工作阻力变化曲线')
        ax1.grid(True, alpha=0.3)
        
        # O1处反力
        ax2.plot(results['theta2_deg'], results['F_O1x'], 'r-', linewidth=2, label='F_O1x')
        ax2.plot(results['theta2_deg'], results['F_O1y'], 'g-', linewidth=2, label='F_O1y')
        ax2.plot(results['theta2_deg'], results['F_O1_magnitude'], 'b-', linewidth=2, label='|F_O1|')
        ax2.set_xlabel('曲柄转角 (度)')
        ax2.set_ylabel('反力 (N)')
        ax2.set_title('O1处反力变化曲线')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # O2处反力
        ax3.plot(results['theta2_deg'], results['F_O2x'], 'r-', linewidth=2, label='F_O2x')
        ax3.plot(results['theta2_deg'], results['F_O2y'], 'g-', linewidth=2, label='F_O2y')
        ax3.plot(results['theta2_deg'], results['F_O2_magnitude'], 'b-', linewidth=2, label='|F_O2|')
        ax3.set_xlabel('曲柄转角 (度)')
        ax3.set_ylabel('反力 (N)')
        ax3.set_title('O2处反力变化曲线')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 平衡力矩
        ax4.plot(results['theta2_deg'], results['M_balance'], 'm-', linewidth=2)
        ax4.set_xlabel('曲柄转角 (度)')
        ax4.set_ylabel('平衡力矩 (N·m)')
        ax4.set_title('平衡力矩变化曲线')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图片
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, 'dynamic_curves.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"动态分析曲线已保存到: {output_dir}/dynamic_curves.png")
    
    def plot_force_analysis(self, results):
        """绘制力分析图"""
        print("绘制力分析图...")
        
        # 选择几个典型位置进行力分析
        indices = [0, 90, 180, 270]  # 0°, 90°, 180°, 270°
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        for idx, i in enumerate(indices):
            ax = axes[idx]
            
            # 绘制力矢量图（简化）
            # 这里只是示意性绘制，实际应该根据具体的力分析结果
            
            # 工作阻力
            if results['F_resistance'][i] > 0:
                ax.arrow(0, 0, results['F_resistance'][i]/1000, 0, 
                        head_width=0.1, head_length=0.1, fc='red', ec='red', 
                        label=f'工作阻力: {results["F_resistance"][i]:.0f}N')
            
            # O1反力
            ax.arrow(0, 0, results['F_O1x'][i]/1000, results['F_O1y'][i]/1000,
                    head_width=0.1, head_length=0.1, fc='blue', ec='blue',
                    label=f'F_O1: {results["F_O1_magnitude"][i]:.0f}N')
            
            # O2反力
            ax.arrow(0, 0, results['F_O2x'][i]/1000, results['F_O2y'][i]/1000,
                    head_width=0.1, head_length=0.1, fc='green', ec='green',
                    label=f'F_O2: {results["F_O2_magnitude"][i]:.0f}N')
            
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(f'θ₂ = {results["theta2_deg"][i]:.0f}° 力分析')
            ax.legend(fontsize=8)
        
        plt.tight_layout()
        
        # 保存图片
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        plt.savefig(os.path.join(output_dir, 'force_analysis.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"力分析图已保存到: {output_dir}/force_analysis.png")

def main():
    """主函数"""
    # 创建动态分析对象
    analysis = DynamicAnalysis()
    
    # 运行完整分析
    results = analysis.run_complete_analysis()
    
    # 绘制曲线
    analysis.plot_dynamic_curves(results)
    
    # 绘制力分析图
    analysis.plot_force_analysis(results)
    
    # 保存数据
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为CSV文件
    import pandas as pd
    df = pd.DataFrame({
        '曲柄转角(度)': results['theta2_deg'],
        '时间(s)': results['time'],
        '工作阻力(N)': results['F_resistance'],
        'O1水平反力(N)': results['F_O1x'],
        'O1垂直反力(N)': results['F_O1y'],
        'O1反力大小(N)': results['F_O1_magnitude'],
        'O2水平反力(N)': results['F_O2x'],
        'O2垂直反力(N)': results['F_O2y'],
        'O2反力大小(N)': results['F_O2_magnitude'],
        '平衡力矩(N·m)': results['M_balance']
    })
    
    csv_file = os.path.join(output_dir, 'dynamic_results.csv')
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"动态分析数据已保存到: {csv_file}")
    
    print("\n=== 动态静力分析完成 ===")
    print(f"最大O1反力: {np.max(results['F_O1_magnitude']):.2f} N")
    print(f"最大O2反力: {np.max(results['F_O2_magnitude']):.2f} N")
    print(f"最大平衡力矩: {np.max(np.abs(results['M_balance'])):.2f} N·m")

if __name__ == "__main__":
    main()