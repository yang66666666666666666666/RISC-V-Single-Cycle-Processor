"""
特征工程模块
从原始数据中提取和构建预测特征
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FeatureEngineer:
    def __init__(self):
        self.team_stats = {}
        
    def calculate_team_stats(self, matches_df):
        """计算球队统计数据"""
        teams = set(matches_df['home_team'].unique()) | set(matches_df['away_team'].unique())
        
        for team in teams:
            home_matches = matches_df[matches_df['home_team'] == team]
            away_matches = matches_df[matches_df['away_team'] == team]
            
            # 主场统计
            home_stats = {
                'games': len(home_matches),
                'wins': len(home_matches[home_matches['result'] == 'H']),
                'draws': len(home_matches[home_matches['result'] == 'D']),
                'losses': len(home_matches[home_matches['result'] == 'A']),
                'goals_for': home_matches['home_goals'].sum(),
                'goals_against': home_matches['away_goals'].sum(),
                'avg_shots': home_matches['home_shots'].mean(),
                'avg_shots_on_target': home_matches['home_shots_on_target'].mean(),
                'avg_possession': home_matches['home_possession'].mean(),
                'avg_corners': home_matches['home_corners'].mean(),
            }
            
            # 客场统计
            away_stats = {
                'games': len(away_matches),
                'wins': len(away_matches[away_matches['result'] == 'A']),
                'draws': len(away_matches[away_matches['result'] == 'D']),
                'losses': len(away_matches[away_matches['result'] == 'H']),
                'goals_for': away_matches['away_goals'].sum(),
                'goals_against': away_matches['home_goals'].sum(),
                'avg_shots': away_matches['away_shots'].mean(),
                'avg_shots_on_target': away_matches['away_shots_on_target'].mean(),
                'avg_possession': away_matches['away_possession'].mean(),
                'avg_corners': away_matches['away_corners'].mean(),
            }
            
            # 总体统计
            total_games = home_stats['games'] + away_stats['games']
            total_wins = home_stats['wins'] + away_stats['wins']
            total_draws = home_stats['draws'] + away_stats['draws']
            total_losses = home_stats['losses'] + away_stats['losses']
            
            self.team_stats[team] = {
                'home': home_stats,
                'away': away_stats,
                'overall': {
                    'games': total_games,
                    'wins': total_wins,
                    'draws': total_draws,
                    'losses': total_losses,
                    'win_rate': total_wins / total_games if total_games > 0 else 0,
                    'points': total_wins * 3 + total_draws,
                    'ppg': (total_wins * 3 + total_draws) / total_games if total_games > 0 else 0,
                    'goals_for': home_stats['goals_for'] + away_stats['goals_for'],
                    'goals_against': home_stats['goals_against'] + away_stats['goals_against'],
                    'goal_difference': (home_stats['goals_for'] + away_stats['goals_for']) - 
                                     (home_stats['goals_against'] + away_stats['goals_against']),
                }
            }
    
    def get_recent_form(self, team, matches_df, num_games=5):
        """获取球队最近表现"""
        team_matches = matches_df[
            (matches_df['home_team'] == team) | 
            (matches_df['away_team'] == team)
        ].sort_values('date', ascending=False).head(num_games)
        
        points = 0
        goals_for = 0
        goals_against = 0
        wins = 0
        
        for _, match in team_matches.iterrows():
            if match['home_team'] == team:
                goals_for += match['home_goals']
                goals_against += match['away_goals']
                if match['result'] == 'H':
                    points += 3
                    wins += 1
                elif match['result'] == 'D':
                    points += 1
            else:
                goals_for += match['away_goals']
                goals_against += match['home_goals']
                if match['result'] == 'A':
                    points += 3
                    wins += 1
                elif match['result'] == 'D':
                    points += 1
        
        return {
            'recent_points': points,
            'recent_goals_for': goals_for,
            'recent_goals_against': goals_against,
            'recent_goal_diff': goals_for - goals_against,
            'recent_wins': wins,
            'recent_form': points / (num_games * 3) if num_games > 0 else 0
        }
    
    def head_to_head_stats(self, home_team, away_team, matches_df, num_games=10):
        """计算两队历史交锋记录"""
        h2h_matches = matches_df[
            ((matches_df['home_team'] == home_team) & (matches_df['away_team'] == away_team)) |
            ((matches_df['home_team'] == away_team) & (matches_df['away_team'] == home_team))
        ].sort_values('date', ascending=False).head(num_games)
        
        if len(h2h_matches) == 0:
            return {
                'h2h_games': 0,
                'h2h_home_wins': 0,
                'h2h_away_wins': 0,
                'h2h_draws': 0,
                'h2h_home_goals': 0,
                'h2h_away_goals': 0
            }
        
        home_wins = 0
        away_wins = 0
        draws = 0
        home_goals = 0
        away_goals = 0
        
        for _, match in h2h_matches.iterrows():
            if match['home_team'] == home_team:
                home_goals += match['home_goals']
                away_goals += match['away_goals']
                if match['result'] == 'H':
                    home_wins += 1
                elif match['result'] == 'A':
                    away_wins += 1
                else:
                    draws += 1
            else:
                home_goals += match['away_goals']
                away_goals += match['home_goals']
                if match['result'] == 'A':
                    home_wins += 1
                elif match['result'] == 'H':
                    away_wins += 1
                else:
                    draws += 1
        
        return {
            'h2h_games': len(h2h_matches),
            'h2h_home_wins': home_wins,
            'h2h_away_wins': away_wins,
            'h2h_draws': draws,
            'h2h_home_goals': home_goals,
            'h2h_away_goals': away_goals
        }
    
    def create_features(self, matches_df):
        """创建机器学习特征"""
        self.calculate_team_stats(matches_df)
        
        features = []
        
        for idx, match in matches_df.iterrows():
            home_team = match['home_team']
            away_team = match['away_team']
            
            # 基础特征
            feature_row = {
                'home_team': home_team,
                'away_team': away_team,
                'result': match['result']
            }
            
            # 球队整体实力特征
            if home_team in self.team_stats:
                home_stats = self.team_stats[home_team]['overall']
                feature_row.update({
                    'home_win_rate': home_stats['win_rate'],
                    'home_ppg': home_stats['ppg'],
                    'home_goal_diff': home_stats['goal_difference'],
                    'home_goals_per_game': home_stats['goals_for'] / max(1, home_stats['games']),
                    'home_goals_conceded_per_game': home_stats['goals_against'] / max(1, home_stats['games'])
                })
            else:
                feature_row.update({
                    'home_win_rate': 0.33,
                    'home_ppg': 1.0,
                    'home_goal_diff': 0,
                    'home_goals_per_game': 1.0,
                    'home_goals_conceded_per_game': 1.0
                })
            
            if away_team in self.team_stats:
                away_stats = self.team_stats[away_team]['overall']
                feature_row.update({
                    'away_win_rate': away_stats['win_rate'],
                    'away_ppg': away_stats['ppg'],
                    'away_goal_diff': away_stats['goal_difference'],
                    'away_goals_per_game': away_stats['goals_for'] / max(1, away_stats['games']),
                    'away_goals_conceded_per_game': away_stats['goals_against'] / max(1, away_stats['games'])
                })
            else:
                feature_row.update({
                    'away_win_rate': 0.33,
                    'away_ppg': 1.0,
                    'away_goal_diff': 0,
                    'away_goals_per_game': 1.0,
                    'away_goals_conceded_per_game': 1.0
                })
            
            # 最近表现特征
            home_form = self.get_recent_form(home_team, matches_df.iloc[:idx])
            away_form = self.get_recent_form(away_team, matches_df.iloc[:idx])
            
            feature_row.update({
                'home_recent_form': home_form['recent_form'],
                'home_recent_goals': home_form['recent_goals_for'],
                'home_recent_conceded': home_form['recent_goals_against'],
                'away_recent_form': away_form['recent_form'],
                'away_recent_goals': away_form['recent_goals_for'],
                'away_recent_conceded': away_form['recent_goals_against']
            })
            
            # 历史交锋特征
            h2h = self.head_to_head_stats(home_team, away_team, matches_df.iloc[:idx])
            feature_row.update(h2h)
            
            # 实力对比特征
            feature_row.update({
                'strength_diff': feature_row['home_win_rate'] - feature_row['away_win_rate'],
                'ppg_diff': feature_row['home_ppg'] - feature_row['away_ppg'],
                'form_diff': feature_row['home_recent_form'] - feature_row['away_recent_form'],
                'attack_vs_defense': feature_row['home_goals_per_game'] - feature_row['away_goals_conceded_per_game'],
                'defense_vs_attack': feature_row['away_goals_per_game'] - feature_row['home_goals_conceded_per_game']
            })
            
            # 主场优势
            feature_row['home_advantage'] = 1
            
            features.append(feature_row)
        
        return pd.DataFrame(features)

if __name__ == "__main__":
    # 测试特征工程
    matches_df = pd.read_csv('football_matches.csv')
    
    engineer = FeatureEngineer()
    features_df = engineer.create_features(matches_df)
    
    print("特征数据形状:", features_df.shape)
    print("\n特征列:")
    print(features_df.columns.tolist())
    print("\n前5行特征数据:")
    print(features_df.head())
    
    # 保存特征数据
    features_df.to_csv('football_features.csv', index=False)
    print("\n特征数据已保存到 football_features.csv")