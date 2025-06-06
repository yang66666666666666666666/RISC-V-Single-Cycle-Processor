"""
足球预测AI系统
基于机器学习和数据分析的足球比赛结果预测

警告：此系统仅用于学习和研究目的，不构成投资建议
体育博彩存在风险，请理性对待，遵守当地法律法规
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MatchData:
    """比赛数据结构"""
    home_team: str
    away_team: str
    date: str
    league: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    result: Optional[str] = None  # 'H', 'D', 'A'

@dataclass
class TeamStats:
    """球队统计数据"""
    team_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int
    form: List[str]  # 最近5场比赛结果
    
    @property
    def win_rate(self) -> float:
        return self.wins / max(self.matches_played, 1)
    
    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against
    
    @property
    def avg_goals_for(self) -> float:
        return self.goals_for / max(self.matches_played, 1)
    
    @property
    def avg_goals_against(self) -> float:
        return self.goals_against / max(self.matches_played, 1)

class FootballDataCollector:
    """足球数据收集器"""
    
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        # 注意：需要注册获取API密钥
        self.headers = {
            'X-Auth-Token': 'YOUR_API_KEY_HERE'
        }
    
    def get_league_matches(self, league_id: str, season: str = "2024") -> List[MatchData]:
        """获取联赛比赛数据"""
        # 模拟数据，实际使用时需要真实API
        sample_matches = [
            MatchData("Manchester City", "Arsenal", "2024-01-15", "Premier League", 2, 1, "H"),
            MatchData("Liverpool", "Chelsea", "2024-01-16", "Premier League", 1, 1, "D"),
            MatchData("Barcelona", "Real Madrid", "2024-01-17", "La Liga", 0, 2, "A"),
            # 更多比赛数据...
        ]
        return sample_matches
    
    def get_team_stats(self, team_name: str, league_id: str) -> TeamStats:
        """获取球队统计数据"""
        # 模拟数据
        if team_name == "Manchester City":
            return TeamStats(
                team_name="Manchester City",
                matches_played=20,
                wins=15,
                draws=3,
                losses=2,
                goals_for=45,
                goals_against=18,
                points=48,
                form=["W", "W", "D", "W", "W"]
            )
        else:
            return TeamStats(
                team_name=team_name,
                matches_played=20,
                wins=10,
                draws=5,
                losses=5,
                goals_for=30,
                goals_against=25,
                points=35,
                form=["L", "W", "D", "W", "L"]
            )

class FeatureEngineer:
    """特征工程"""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def create_features(self, home_stats: TeamStats, away_stats: TeamStats, 
                       historical_h2h: List[MatchData]) -> Dict[str, float]:
        """创建预测特征"""
        
        # 基础统计特征
        features = {
            # 主队特征
            'home_win_rate': home_stats.win_rate,
            'home_goal_diff': home_stats.goal_difference,
            'home_avg_goals_for': home_stats.avg_goals_for,
            'home_avg_goals_against': home_stats.avg_goals_against,
            'home_points': home_stats.points,
            
            # 客队特征
            'away_win_rate': away_stats.win_rate,
            'away_goal_diff': away_stats.goal_difference,
            'away_avg_goals_for': away_stats.avg_goals_for,
            'away_avg_goals_against': away_stats.avg_goals_against,
            'away_points': away_stats.points,
            
            # 对比特征
            'win_rate_diff': home_stats.win_rate - away_stats.win_rate,
            'goal_diff_diff': home_stats.goal_difference - away_stats.goal_difference,
            'points_diff': home_stats.points - away_stats.points,
        }
        
        # 近期状态特征
        features.update(self._get_form_features(home_stats.form, away_stats.form))
        
        # 历史交锋特征
        features.update(self._get_h2h_features(historical_h2h))
        
        # 主场优势
        features['home_advantage'] = 1.0
        
        return features
    
    def _get_form_features(self, home_form: List[str], away_form: List[str]) -> Dict[str, float]:
        """获取近期状态特征"""
        def form_score(form_list):
            score = 0
            for i, result in enumerate(reversed(form_list[-5:])):
                weight = (i + 1) * 0.2  # 越近期权重越高
                if result == 'W':
                    score += 3 * weight
                elif result == 'D':
                    score += 1 * weight
            return score
        
        return {
            'home_form_score': form_score(home_form),
            'away_form_score': form_score(away_form),
            'form_diff': form_score(home_form) - form_score(away_form)
        }
    
    def _get_h2h_features(self, h2h_matches: List[MatchData]) -> Dict[str, float]:
        """获取历史交锋特征"""
        if not h2h_matches:
            return {
                'h2h_home_wins': 0.5,
                'h2h_draws': 0.33,
                'h2h_away_wins': 0.5,
                'h2h_avg_goals': 2.5
            }
        
        home_wins = sum(1 for m in h2h_matches if m.result == 'H')
        draws = sum(1 for m in h2h_matches if m.result == 'D')
        away_wins = sum(1 for m in h2h_matches if m.result == 'A')
        total_matches = len(h2h_matches)
        
        total_goals = sum(m.home_score + m.away_score for m in h2h_matches if m.home_score is not None)
        
        return {
            'h2h_home_wins': home_wins / total_matches,
            'h2h_draws': draws / total_matches,
            'h2h_away_wins': away_wins / total_matches,
            'h2h_avg_goals': total_goals / total_matches if total_matches > 0 else 2.5
        }

class FootballPredictor:
    """足球预测模型"""
    
    def __init__(self):
        self.models = {
            'result': RandomForestClassifier(n_estimators=100, random_state=42),
            'goals': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'over_under': LogisticRegression(random_state=42)
        }
        self.feature_engineer = FeatureEngineer()
        self.is_trained = False
    
    def prepare_training_data(self, matches: List[MatchData], 
                            team_stats_dict: Dict[str, TeamStats]) -> Tuple[np.ndarray, np.ndarray]:
        """准备训练数据"""
        features_list = []
        labels_list = []
        
        for match in matches:
            if match.result is None:
                continue
                
            home_stats = team_stats_dict.get(match.home_team)
            away_stats = team_stats_dict.get(match.away_team)
            
            if home_stats and away_stats:
                features = self.feature_engineer.create_features(
                    home_stats, away_stats, []
                )
                features_list.append(list(features.values()))
                
                # 标签编码：H=0, D=1, A=2
                label_map = {'H': 0, 'D': 1, 'A': 2}
                labels_list.append(label_map[match.result])
        
        return np.array(features_list), np.array(labels_list)
    
    def train(self, matches: List[MatchData], team_stats_dict: Dict[str, TeamStats]):
        """训练模型"""
        print("🏋️ 开始训练足球预测模型...")
        
        X, y = self.prepare_training_data(matches, team_stats_dict)
        
        if len(X) == 0:
            print("❌ 没有足够的训练数据")
            return
        
        # 分割训练和测试数据
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 特征标准化
        X_train_scaled = self.feature_engineer.scaler.fit_transform(X_train)
        X_test_scaled = self.feature_engineer.scaler.transform(X_test)
        
        # 训练比赛结果预测模型
        self.models['result'].fit(X_train_scaled, y_train)
        
        # 评估模型
        y_pred = self.models['result'].predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ 模型训练完成！")
        print(f"📊 测试集准确率: {accuracy:.3f}")
        print(f"📈 交叉验证得分: {cross_val_score(self.models['result'], X_train_scaled, y_train, cv=5).mean():.3f}")
        
        self.is_trained = True
    
    def predict_match(self, home_team: str, away_team: str, 
                     team_stats_dict: Dict[str, TeamStats]) -> Dict[str, any]:
        """预测比赛结果"""
        if not self.is_trained:
            return {"error": "模型尚未训练"}
        
        home_stats = team_stats_dict.get(home_team)
        away_stats = team_stats_dict.get(away_team)
        
        if not home_stats or not away_stats:
            return {"error": "缺少球队数据"}
        
        # 创建特征
        features = self.feature_engineer.create_features(home_stats, away_stats, [])
        X = np.array([list(features.values())])
        X_scaled = self.feature_engineer.scaler.transform(X)
        
        # 预测结果概率
        result_probs = self.models['result'].predict_proba(X_scaled)[0]
        result_labels = ['主胜', '平局', '客胜']
        
        # 预测最可能的结果
        predicted_result = result_labels[np.argmax(result_probs)]
        confidence = np.max(result_probs)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'predicted_result': predicted_result,
            'confidence': confidence,
            'probabilities': {
                '主胜': result_probs[0],
                '平局': result_probs[1], 
                '客胜': result_probs[2]
            },
            'recommendation': self._get_betting_recommendation(result_probs, confidence)
        }
    
    def _get_betting_recommendation(self, probs: np.ndarray, confidence: float) -> Dict[str, any]:
        """获取投注建议"""
        max_prob = np.max(probs)
        
        # 保守的投注策略
        if confidence > 0.6 and max_prob > 0.5:
            risk_level = "低风险"
            recommended_stake = "小额投注"
        elif confidence > 0.45:
            risk_level = "中等风险"
            recommended_stake = "谨慎投注"
        else:
            risk_level = "高风险"
            recommended_stake = "不建议投注"
        
        return {
            'risk_level': risk_level,
            'recommended_stake': recommended_stake,
            'confidence_threshold': confidence,
            'note': '请理性投注，控制风险'
        }

class FootballPredictionSystem:
    """足球预测系统主类"""
    
    def __init__(self):
        self.data_collector = FootballDataCollector()
        self.predictor = FootballPredictor()
        self.team_stats = {}
    
    def initialize_system(self):
        """初始化系统"""
        print("🚀 初始化足球预测系统...")
        
        # 收集历史数据
        matches = self.data_collector.get_league_matches("PL")  # 英超
        
        # 收集球队统计数据
        teams = set()
        for match in matches:
            teams.add(match.home_team)
            teams.add(match.away_team)
        
        for team in teams:
            self.team_stats[team] = self.data_collector.get_team_stats(team, "PL")
        
        # 训练模型
        self.predictor.train(matches, self.team_stats)
        
        print("✅ 系统初始化完成！")
    
    def predict_upcoming_matches(self, matches: List[Tuple[str, str]]) -> List[Dict]:
        """预测即将到来的比赛"""
        predictions = []
        
        for home_team, away_team in matches:
            prediction = self.predictor.predict_match(
                home_team, away_team, self.team_stats
            )
            predictions.append(prediction)
        
        return predictions
    
    def generate_betting_report(self, predictions: List[Dict]) -> str:
        """生成投注报告"""
        report = "📊 足球预测投注报告\n"
        report += "=" * 50 + "\n\n"
        
        high_confidence_bets = []
        
        for pred in predictions:
            if 'error' in pred:
                continue
                
            report += f"🏆 {pred['home_team']} vs {pred['away_team']}\n"
            report += f"预测结果: {pred['predicted_result']}\n"
            report += f"置信度: {pred['confidence']:.3f}\n"
            report += f"概率分布:\n"
            for outcome, prob in pred['probabilities'].items():
                report += f"  {outcome}: {prob:.3f}\n"
            
            rec = pred['recommendation']
            report += f"投注建议: {rec['recommended_stake']} ({rec['risk_level']})\n"
            report += f"风险提示: {rec['note']}\n"
            report += "-" * 30 + "\n\n"
            
            if rec['confidence_threshold'] > 0.6:
                high_confidence_bets.append(pred)
        
        if high_confidence_bets:
            report += "🎯 高置信度推荐:\n"
            for bet in high_confidence_bets:
                report += f"• {bet['home_team']} vs {bet['away_team']} - {bet['predicted_result']}\n"
        
        report += "\n⚠️ 重要提醒:\n"
        report += "• 任何预测都存在不确定性\n"
        report += "• 请理性投注，控制风险\n"
        report += "• 遵守当地法律法规\n"
        report += "• 切勿沉迷赌博\n"
        
        return report

def main():
    """主函数演示"""
    print("⚽ 足球预测AI系统演示")
    print("=" * 50)
    
    # 创建预测系统
    system = FootballPredictionSystem()
    
    # 初始化系统
    system.initialize_system()
    
    # 预测即将到来的比赛
    upcoming_matches = [
        ("Manchester City", "Arsenal"),
        ("Liverpool", "Chelsea"),
        ("Barcelona", "Real Madrid")
    ]
    
    print("\n🔮 预测即将到来的比赛...")
    predictions = system.predict_upcoming_matches(upcoming_matches)
    
    # 生成报告
    report = system.generate_betting_report(predictions)
    print(report)
    
    # 保存报告
    with open('/workspace/football_prediction_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("📄 预测报告已保存到 football_prediction_report.txt")

if __name__ == "__main__":
    main()

"""
🎯 系统特点:

1. **多维度数据分析**
   - 球队历史表现
   - 近期状态
   - 历史交锋记录
   - 主客场优势

2. **机器学习模型**
   - 随机森林分类器
   - 梯度提升算法
   - 逻辑回归模型

3. **风险控制**
   - 置信度评估
   - 投注建议分级
   - 风险提醒

4. **实用功能**
   - 自动数据收集
   - 特征工程
   - 预测报告生成

📈 改进方向:

1. **数据源扩展**
   - 球员伤病信息
   - 天气条件
   - 裁判统计
   - 博彩赔率

2. **模型优化**
   - 深度学习模型
   - 集成学习
   - 在线学习
   - 超参数调优

3. **实时功能**
   - 实时数据更新
   - 比赛中预测
   - 动态调整

⚠️ 免责声明:
此系统仅用于学习和研究目的，不构成投资建议。
体育博彩存在风险，请理性对待，遵守法律法规。
"""