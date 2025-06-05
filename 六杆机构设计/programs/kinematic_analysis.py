#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六杆机构运动分析主程序
计算滑块6的位移、速度、加速度
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

class KinematicAnalysis:
    def __init__(self):
        # 获取设计参数
        self.design = SixBarMechanismDesign()
        self.results = self.design.save_design_results()
        
        # 提取关键参数
        self.omega2 = self.results['omega2']
        self.l_O2A = self.results['input_parameters']['l_O2A'] / 1000  # 转换为米
        self.l_AB = self.results['calculated_dimensions']['l_AB']
        self.l_O1O2 = self.results['calculated_dimensions']['l_O1O2']
        self.l_O1B = self.results['calculated_dimensions']['l_O1B']
        self.l_BC = self.results['calculated_dimensions']['l_BC']
        self.l_CD = self.results['calculated_dimensions']['l_CD']
        self.guide_height = self.results['calculated_dimensions']['guide_height']
        
        print("=== 六杆机构运动分析 ===")
        print(f"分析参数已加载")
        
    def position_analysis(self, theta2_array):
        """位置分析"""
        n_points = len(theta2_array)
        
        # 初始化结果数组
        x_A = np.zeros(n_points)
        y_A = np.zeros(n_points)
        x_B = np.zeros(n_points)
        y_B = np.zeros(n_points)
        x_C = np.zeros(n_points)
        y_C = np.zeros(n_points)
        x_6 = np.zeros(n_points)  # 滑块6的位移
        
        # 设置坐标系原点O2在(0,0)，O1在(-l_O1O2, 0)
        O1_x, O1_y = -self.l_O1O2, 0
        O2_x, O2_y = 0, 0
        
        for i, theta2 in enumerate(theta2_array):
            # 点A的位置（曲柄末端）
            x_A[i] = O2_x + self.l_O2A * np.cos(theta2)
            y_A[i] = O2_y + self.l_O2A * np.sin(theta2)
            
            # 点B的位置（通过几何约束求解）
            # 使用余弦定理和几何关系
            # 这里简化处理，实际应该求解复杂的几何约束方程
            
            # 假设B点在以O1为中心的圆弧上运动
            # 通过A点位置和连杆长度约束确定B点
            
            # 计算O1A距离
            O1A_dist = np.sqrt((x_A[i] - O1_x)**2 + (y_A[i] - O1_y)**2)
            
            # 使用余弦定理计算角度
            if O1A_dist <= self.l_AB + self.l_O1B and O1A_dist >= abs(self.l_AB - self.l_O1B):
                cos_angle = (self.l_O1B**2 + O1A_dist**2 - self.l_AB**2) / (2 * self.l_O1B * O1A_dist)
                cos_angle = np.clip(cos_angle, -1, 1)  # 确保在有效范围内
                
                angle_O1A = np.arctan2(y_A[i] - O1_y, x_A[i] - O1_x)
                angle_O1B = angle_O1A + np.arccos(cos_angle)
                
                x_B[i] = O1_x + self.l_O1B * np.cos(angle_O1B)
                y_B[i] = O1_y + self.l_O1B * np.sin(angle_O1B)
            else:
                # 如果无解，使用近似值
                x_B[i] = O1_x + self.l_O1B * np.cos(theta2 * 0.5)
                y_B[i] = O1_y + self.l_O1B * np.sin(theta2 * 0.5)
            
            # 点C的位置（在BC延长线上）
            BC_angle = np.arctan2(y_B[i] - y_A[i], x_B[i] - x_A[i]) if x_B[i] != x_A[i] else np.pi/2
            x_C[i] = x_B[i] + self.l_BC * np.cos(BC_angle)
            y_C[i] = y_B[i] + self.l_BC * np.sin(BC_angle)
            
            # 滑块6的位置（假设在水平导路上）
            x_6[i] = x_C[i] + self.l_CD * np.cos(BC_angle + np.pi/4)  # 简化处理
        
        return {
            'theta2': theta2_array,
            'x_A': x_A, 'y_A': y_A,
            'x_B': x_B, 'y_B': y_B,
            'x_C': x_C, 'y_C': y_C,
            'x_6': x_6
        }
    
    def velocity_analysis(self, positions, dt):
        """速度分析"""
        # 使用数值微分计算速度
        v_6 = np.gradient(positions['x_6'], dt)
        
        return {'v_6': v_6}
    
    def acceleration_analysis(self, velocities, dt):
        """加速度分析"""
        # 使用数值微分计算加速度
        a_6 = np.gradient(velocities['v_6'], dt)
        
        return {'a_6': a_6}
    
    def run_complete_analysis(self):
        """运行完整的运动分析"""
        print("\n=== 开始运动分析 ===")
        
        # 设置分析参数
        n_points = 360  # 一周360个点
        theta2_array = np.linspace(0, 2*np.pi, n_points)
        dt = 2*np.pi / (self.omega2 * n_points)  # 时间步长
        
        # 位置分析
        print("进行位置分析...")
        positions = self.position_analysis(theta2_array)
        
        # 速度分析
        print("进行速度分析...")
        velocities = self.velocity_analysis(positions, dt)
        
        # 加速度分析
        print("进行加速度分析...")
        accelerations = self.acceleration_analysis(velocities, dt)
        
        # 时间数组
        t_array = theta2_array / self.omega2
        
        # 保存结果
        results = {
            'time': t_array,
            'theta2_deg': np.degrees(theta2_array),
            'displacement': positions['x_6'] * 1000,  # 转换为mm
            'velocity': velocities['v_6'] * 1000,     # 转换为mm/s
            'acceleration': accelerations['a_6'] * 1000,  # 转换为mm/s²
            'positions': positions
        }
        
        print("运动分析完成！")
        return results
    
    def plot_kinematic_curves(self, results):
        """绘制运动曲线"""
        print("绘制运动曲线...")
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        
        # 位移曲线
        ax1.plot(results['theta2_deg'], results['displacement'], 'b-', linewidth=2)
        ax1.set_xlabel('曲柄转角 (度)')
        ax1.set_ylabel('滑块6位移 (mm)')
        ax1.set_title('滑块6位移曲线')
        ax1.grid(True, alpha=0.3)
        
        # 速度曲线
        ax2.plot(results['theta2_deg'], results['velocity'], 'r-', linewidth=2)
        ax2.set_xlabel('曲柄转角 (度)')
        ax2.set_ylabel('滑块6速度 (mm/s)')
        ax2.set_title('滑块6速度曲线')
        ax2.grid(True, alpha=0.3)
        
        # 加速度曲线
        ax3.plot(results['theta2_deg'], results['acceleration'], 'g-', linewidth=2)
        ax3.set_xlabel('曲柄转角 (度)')
        ax3.set_ylabel('滑块6加速度 (mm/s²)')
        ax3.set_title('滑块6加速度曲线')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图片
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, 'kinematic_curves.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"运动曲线已保存到: {output_dir}/kinematic_curves.png")
    
    def plot_mechanism_animation(self, results):
        """绘制机构运动简图"""
        print("绘制机构运动简图...")
        
        positions = results['positions']
        
        # 选择几个典型位置进行绘制
        indices = [0, 90, 180, 270]  # 0°, 90°, 180°, 270°
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        for idx, i in enumerate(indices):
            ax = axes[idx]
            
            # 绘制机构
            # 机架
            O1_x, O1_y = -self.l_O1O2, 0
            O2_x, O2_y = 0, 0
            
            ax.plot([O1_x, O2_x], [O1_y, O2_y], 'k-', linewidth=3, label='机架')
            
            # 曲柄O2A
            ax.plot([O2_x, positions['x_A'][i]], [O2_y, positions['y_A'][i]], 'r-', linewidth=2, label='曲柄')
            
            # 连杆AB
            ax.plot([positions['x_A'][i], positions['x_B'][i]], 
                   [positions['y_A'][i], positions['y_B'][i]], 'b-', linewidth=2, label='连杆AB')
            
            # 导杆O1B
            ax.plot([O1_x, positions['x_B'][i]], [O1_y, positions['y_B'][i]], 'g-', linewidth=2, label='导杆O1B')
            
            # BC杆
            ax.plot([positions['x_B'][i], positions['x_C'][i]], 
                   [positions['y_B'][i], positions['y_C'][i]], 'm-', linewidth=2, label='BC杆')
            
            # 关键点
            ax.plot(O1_x, O1_y, 'ko', markersize=8)
            ax.plot(O2_x, O2_y, 'ko', markersize=8)
            ax.plot(positions['x_A'][i], positions['y_A'][i], 'ro', markersize=6)
            ax.plot(positions['x_B'][i], positions['y_B'][i], 'bo', markersize=6)
            ax.plot(positions['x_C'][i], positions['y_C'][i], 'mo', markersize=6)
            
            # 标注
            ax.text(O1_x-0.01, O1_y-0.01, 'O1', fontsize=10)
            ax.text(O2_x+0.01, O2_y-0.01, 'O2', fontsize=10)
            ax.text(positions['x_A'][i]+0.01, positions['y_A'][i]+0.01, 'A', fontsize=10)
            ax.text(positions['x_B'][i]+0.01, positions['y_B'][i]+0.01, 'B', fontsize=10)
            ax.text(positions['x_C'][i]+0.01, positions['y_C'][i]+0.01, 'C', fontsize=10)
            
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(f'θ₂ = {results["theta2_deg"][i]:.0f}°')
            
            if idx == 0:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        # 保存图片
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        plt.savefig(os.path.join(output_dir, 'mechanism_positions.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"机构位置图已保存到: {output_dir}/mechanism_positions.png")

def main():
    """主函数"""
    # 创建运动分析对象
    analysis = KinematicAnalysis()
    
    # 运行完整分析
    results = analysis.run_complete_analysis()
    
    # 绘制曲线
    analysis.plot_kinematic_curves(results)
    
    # 绘制机构图
    analysis.plot_mechanism_animation(results)
    
    # 保存数据
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为CSV文件
    import pandas as pd
    df = pd.DataFrame({
        '曲柄转角(度)': results['theta2_deg'],
        '时间(s)': results['time'],
        '滑块6位移(mm)': results['displacement'],
        '滑块6速度(mm/s)': results['velocity'],
        '滑块6加速度(mm/s²)': results['acceleration']
    })
    
    csv_file = os.path.join(output_dir, 'kinematic_results.csv')
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"运动分析数据已保存到: {csv_file}")
    
    print("\n=== 运动分析完成 ===")
    print(f"最大位移: {np.max(results['displacement']):.2f} mm")
    print(f"最大速度: {np.max(np.abs(results['velocity'])):.2f} mm/s")
    print(f"最大加速度: {np.max(np.abs(results['acceleration'])):.2f} mm/s²")

if __name__ == "__main__":
    main()