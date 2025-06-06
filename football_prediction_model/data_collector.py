"""
足球数据收集器
收集历史比赛数据、球队统计、球员信息等
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import time
import json
import random

class FootballDataCollector:
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {
            'X-Auth-Token': 'YOUR_API_TOKEN'  # 需要注册获取免费API token
        }
        
    def generate_sample_data(self, num_matches=1000):
        """生成示例数据用于演示"""
        teams = [
            'Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Manchester United',
            'Newcastle', 'Tottenham', 'Brighton', 'Aston Villa', 'West Ham',
            'Crystal Palace', 'Fulham', 'Wolves', 'Everton', 'Brentford',
            'Nottingham Forest', 'Leeds United', 'Leicester City', 'Southampton', 'Bournemouth'
        ]
        
        data = []
        for i in range(num_matches):
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            # 生成基础统计数据
            home_strength = random.uniform(0.3, 0.9)
            away_strength = random.uniform(0.3, 0.9)
            
            # 主场优势
            home_advantage = 0.1
            
            # 预期进球数
            home_expected_goals = home_strength * (2 - away_strength) + home_advantage
            away_expected_goals = away_strength * (2 - home_strength)
            
            # 实际进球数（泊松分布）
            home_goals = np.random.poisson(max(0, home_expected_goals))
            away_goals = np.random.poisson(max(0, away_expected_goals))
            
            # 比赛结果
            if home_goals > away_goals:
                result = 'H'  # 主队胜
            elif away_goals > home_goals:
                result = 'A'  # 客队胜
            else:
                result = 'D'  # 平局
            
            # 生成其他统计数据
            match_data = {
                'date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
                'home_team': home_team,
                'away_team': away_team,
                'home_goals': home_goals,
                'away_goals': away_goals,
                'result': result,
                'home_shots': random.randint(8, 25),
                'away_shots': random.randint(8, 25),
                'home_shots_on_target': random.randint(3, 12),
                'away_shots_on_target': random.randint(3, 12),
                'home_possession': random.randint(35, 75),
                'away_possession': 100 - random.randint(35, 75),
                'home_corners': random.randint(2, 12),
                'away_corners': random.randint(2, 12),
                'home_fouls': random.randint(8, 20),
                'away_fouls': random.randint(8, 20),
                'home_yellow_cards': random.randint(0, 5),
                'away_yellow_cards': random.randint(0, 5),
                'home_red_cards': random.randint(0, 1) if random.random() < 0.1 else 0,
                'away_red_cards': random.randint(0, 1) if random.random() < 0.1 else 0,
                'home_team_strength': home_strength,
                'away_team_strength': away_strength,
            }
            
            data.append(match_data)
        
        return pd.DataFrame(data)
    
    def get_team_form(self, team_name, matches_df, num_games=5):
        """获取球队最近表现"""
        team_matches = matches_df[
            (matches_df['home_team'] == team_name) | 
            (matches_df['away_team'] == team_name)
        ].sort_values('date', ascending=False).head(num_games)
        
        points = 0
        goals_for = 0
        goals_against = 0
        
        for _, match in team_matches.iterrows():
            if match['home_team'] == team_name:
                goals_for += match['home_goals']
                goals_against += match['away_goals']
                if match['result'] == 'H':
                    points += 3
                elif match['result'] == 'D':
                    points += 1
            else:
                goals_for += match['away_goals']
                goals_against += match['home_goals']
                if match['result'] == 'A':
                    points += 3
                elif match['result'] == 'D':
                    points += 1
        
        return {
            'points': points,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_difference': goals_for - goals_against,
            'avg_points': points / len(team_matches) if len(team_matches) > 0 else 0
        }
    
    def save_data(self, df, filename):
        """保存数据到CSV文件"""
        df.to_csv(filename, index=False)
        print(f"数据已保存到 {filename}")

if __name__ == "__main__":
    collector = FootballDataCollector()
    
    # 生成示例数据
    print("正在生成示例数据...")
    matches_df = collector.generate_sample_data(1000)
    
    # 保存数据
    collector.save_data(matches_df, 'football_matches.csv')
    
    print(f"生成了 {len(matches_df)} 场比赛的数据")
    print(matches_df.head())