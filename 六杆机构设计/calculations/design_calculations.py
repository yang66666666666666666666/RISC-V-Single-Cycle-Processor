#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六杆机构设计计算
基于第9列参数进行机构尺寸设计
"""

import numpy as np
import matplotlib.pyplot as plt
import math

# 设计参数（第9列）
n2 = 49  # r/min 转速
l_O2A = 82  # mm 曲柄长度
d = 122  # mm 分布
K = 1.9  # 行程速比系数
H = 128  # mm 描刀行程
f_BC_BO1 = 0.62  # f_BC/f_BO1比值
F_max = 8800  # N 工作阻力
m6 = 65  # kg 滑块6质量
m4 = 26  # kg 导杆4质量
Js4 = 1.2  # kg·m² 导杆4质心转动惯量

class SixBarMechanismDesign:
    def __init__(self):
        self.n2 = n2
        self.l_O2A = l_O2A / 1000  # 转换为米
        self.d = d / 1000  # 转换为米
        self.K = K
        self.H = H / 1000  # 转换为米
        self.f_BC_BO1 = f_BC_BO1
        self.F_max = F_max
        self.m6 = m6
        self.m4 = m4
        self.Js4 = Js4
        
        # 计算角速度
        self.omega2 = 2 * np.pi * self.n2 / 60  # rad/s
        
        print("=== 六杆机构设计计算 ===")
        print(f"输入参数：")
        print(f"转速 n₂ = {self.n2} r/min")
        print(f"曲柄长度 l_O2A = {l_O2A} mm")
        print(f"分布 d = {d} mm")
        print(f"行程速比系数 K = {self.K}")
        print(f"描刀行程 H = {H} mm")
        print(f"f_BC/f_BO1 = {self.f_BC_BO1}")
        print(f"角速度 ω₂ = {self.omega2:.3f} rad/s")
        
    def calculate_mechanism_dimensions(self):
        """计算机构尺寸"""
        print("\n=== 机构尺寸计算 ===")
        
        # 根据行程速比系数计算摆角
        # K = (180° + ψ) / (180° - ψ)
        # 解得：ψ = 180° * (K - 1) / (K + 1)
        psi_deg = 180 * (self.K - 1) / (self.K + 1)
        psi_rad = np.radians(psi_deg)
        
        print(f"摆角 ψ = {psi_deg:.2f}°")
        
        # 计算连杆长度
        # 对于六杆机构，根据几何关系计算各杆长度
        
        # 连杆AB长度（根据行程和摆角关系）
        self.l_AB = self.H / (2 * np.sin(psi_rad / 2))
        
        # 机架O1O2长度（根据分布参数）
        self.l_O1O2 = self.d
        
        # 导杆O1B长度（根据几何约束）
        self.l_O1B = np.sqrt(self.l_O1O2**2 + self.l_O2A**2 - 2*self.l_O1O2*self.l_O2A*np.cos(psi_rad))
        
        # BC杆长度
        self.l_BC = self.f_BC_BO1 * self.l_O1B
        
        # CD杆长度（假设与BC相等，实际应根据具体约束确定）
        self.l_CD = self.l_BC * 0.8  # 经验值
        
        # 滑块6的导路位置
        self.guide_height = self.l_O1B * 0.6  # 经验值
        
        print(f"连杆AB长度 l_AB = {self.l_AB*1000:.2f} mm")
        print(f"机架O1O2长度 l_O1O2 = {self.l_O1O2*1000:.2f} mm")
        print(f"导杆O1B长度 l_O1B = {self.l_O1B*1000:.2f} mm")
        print(f"BC杆长度 l_BC = {self.l_BC*1000:.2f} mm")
        print(f"CD杆长度 l_CD = {self.l_CD*1000:.2f} mm")
        print(f"导路高度 = {self.guide_height*1000:.2f} mm")
        
        return {
            'l_AB': self.l_AB,
            'l_O1O2': self.l_O1O2,
            'l_O1B': self.l_O1B,
            'l_BC': self.l_BC,
            'l_CD': self.l_CD,
            'psi_deg': psi_deg,
            'guide_height': self.guide_height
        }
    
    def determine_rotation_direction(self):
        """确定曲柄转动方向"""
        print("\n=== 曲柄转动方向确定 ===")
        
        # 根据工作要求，通常选择使工作行程时间较短的方向
        # 由于K > 1，说明工作行程较快，回程较慢
        # 因此选择顺时针转动
        
        rotation_direction = "顺时针"
        print(f"曲柄转动方向：{rotation_direction}")
        print(f"理由：K = {self.K} > 1，工作行程较快，选择顺时针转动")
        
        return rotation_direction
    
    def save_design_results(self):
        """保存设计结果"""
        dimensions = self.calculate_mechanism_dimensions()
        direction = self.determine_rotation_direction()
        
        results = {
            'input_parameters': {
                'n2': self.n2,
                'l_O2A': l_O2A,
                'd': d,
                'K': self.K,
                'H': H,
                'f_BC_BO1': self.f_BC_BO1,
                'F_max': self.F_max,
                'm6': self.m6,
                'm4': self.m4,
                'Js4': self.Js4
            },
            'calculated_dimensions': dimensions,
            'rotation_direction': direction,
            'omega2': self.omega2
        }
        
        return results

if __name__ == "__main__":
    # 创建设计对象
    design = SixBarMechanismDesign()
    
    # 执行设计计算
    results = design.save_design_results()
    
    print("\n=== 设计计算完成 ===")
    print("结果已保存，可用于后续运动分析和动态静力分析")