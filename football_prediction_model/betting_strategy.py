"""
投注策略模块
基于模型预测结果制定投注策略
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class BettingStrategy:
    def __init__(self, initial_bankroll=1000):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.bet_history = []
        self.roi_history = []
        
    def kelly_criterion(self, probability, odds):
        """凯利公式计算最优投注比例"""
        if probability <= 0 or odds <= 1:
            return 0
        
        # 凯利公式: f = (bp - q) / b
        # 其中 b = odds - 1, p = probability, q = 1 - p
        b = odds - 1
        p = probability
        q = 1 - p
        
        f = (b * p - q) / b
        return max(0, min(f, 0.25))  # 限制最大投注比例为25%
    
    def value_betting(self, model_prob, bookmaker_odds, min_edge=0.05):
        """价值投注策略"""
        implied_prob = 1 / bookmaker_odds
        edge = model_prob - implied_prob
        
        if edge > min_edge:
            return True, edge
        return False, edge
    
    def confidence_betting(self, prediction_confidence, min_confidence=0.6):
        """基于预测置信度的投注策略"""
        return prediction_confidence >= min_confidence
    
    def simulate_betting(self, predictions_df, odds_df, strategy='kelly', 
                        min_confidence=0.6, min_edge=0.05):
        """模拟投注过程"""
        self.current_bankroll = self.initial_bankroll
        self.bet_history = []
        self.roi_history = []
        
        for idx, row in predictions_df.iterrows():
            if idx >= len(odds_df):
                break
                
            odds_row = odds_df.iloc[idx]
            
            # 获取预测信息
            predicted_result = row['predicted_result']
            confidence = row['confidence']
            probabilities = {
                'H': row.get('prob_H', 0.33),
                'D': row.get('prob_D', 0.33),
                'A': row.get('prob_A', 0.33)
            }
            
            # 获取赔率
            odds = {
                'H': odds_row.get('home_odds', 2.5),
                'D': odds_row.get('draw_odds', 3.0),
                'A': odds_row.get('away_odds', 2.8)
            }
            
            actual_result = row['actual_result']
            
            # 决定是否投注
            should_bet = False
            bet_amount = 0
            bet_outcome = predicted_result
            
            if strategy == 'kelly':
                # 凯利公式策略
                kelly_fraction = self.kelly_criterion(
                    probabilities[predicted_result], 
                    odds[predicted_result]
                )
                if kelly_fraction > 0 and confidence >= min_confidence:
                    bet_amount = self.current_bankroll * kelly_fraction
                    should_bet = True
                    
            elif strategy == 'value':
                # 价值投注策略
                is_value, edge = self.value_betting(
                    probabilities[predicted_result], 
                    odds[predicted_result], 
                    min_edge
                )
                if is_value and confidence >= min_confidence:
                    bet_amount = self.current_bankroll * 0.02  # 固定2%投注
                    should_bet = True
                    
            elif strategy == 'fixed':
                # 固定金额策略
                if confidence >= min_confidence:
                    bet_amount = min(50, self.current_bankroll * 0.05)  # 固定50或5%
                    should_bet = True
            
            # 执行投注
            if should_bet and bet_amount > 0:
                self.current_bankroll -= bet_amount
                
                # 计算收益
                if actual_result == bet_outcome:
                    winnings = bet_amount * odds[bet_outcome]
                    self.current_bankroll += winnings
                    profit = winnings - bet_amount
                else:
                    profit = -bet_amount
                
                # 记录投注历史
                bet_record = {
                    'date': row.get('date', datetime.now()),
                    'home_team': row.get('home_team', ''),
                    'away_team': row.get('away_team', ''),
                    'predicted': predicted_result,
                    'actual': actual_result,
                    'confidence': confidence,
                    'odds': odds[bet_outcome],
                    'bet_amount': bet_amount,
                    'profit': profit,
                    'bankroll': self.current_bankroll,
                    'roi': (self.current_bankroll - self.initial_bankroll) / self.initial_bankroll
                }
                
                self.bet_history.append(bet_record)
                self.roi_history.append(bet_record['roi'])
        
        return self.bet_history
    
    def analyze_performance(self):
        """分析投注表现"""
        if not self.bet_history:
            print("没有投注记录")
            return
        
        df = pd.DataFrame(self.bet_history)
        
        # 基本统计
        total_bets = len(df)
        winning_bets = len(df[df['profit'] > 0])
        losing_bets = len(df[df['profit'] < 0])
        win_rate = winning_bets / total_bets if total_bets > 0 else 0
        
        total_profit = df['profit'].sum()
        total_staked = df['bet_amount'].sum()
        roi = total_profit / total_staked if total_staked > 0 else 0
        
        avg_odds = df['odds'].mean()
        avg_bet = df['bet_amount'].mean()
        
        print("=== 投注表现分析 ===")
        print(f"总投注次数: {total_bets}")
        print(f"获胜次数: {winning_bets}")
        print(f"失败次数: {losing_bets}")
        print(f"胜率: {win_rate:.2%}")
        print(f"总投注金额: ${total_staked:.2f}")
        print(f"总盈亏: ${total_profit:.2f}")
        print(f"投资回报率: {roi:.2%}")
        print(f"平均赔率: {avg_odds:.2f}")
        print(f"平均投注额: ${avg_bet:.2f}")
        print(f"最终资金: ${self.current_bankroll:.2f}")
        print(f"资金增长率: {(self.current_bankroll - self.initial_bankroll) / self.initial_bankroll:.2%}")
        
        return {
            'total_bets': total_bets,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'roi': roi,
            'final_bankroll': self.current_bankroll
        }
    
    def plot_performance(self):
        """绘制投注表现图表"""
        if not self.bet_history:
            print("没有投注记录")
            return
        
        df = pd.DataFrame(self.bet_history)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 资金变化
        axes[0, 0].plot(df.index, df['bankroll'])
        axes[0, 0].axhline(y=self.initial_bankroll, color='r', linestyle='--', alpha=0.7)
        axes[0, 0].set_title('资金变化')
        axes[0, 0].set_xlabel('投注次数')
        axes[0, 0].set_ylabel('资金 ($)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 累计盈亏
        cumulative_profit = df['profit'].cumsum()
        axes[0, 1].plot(df.index, cumulative_profit)
        axes[0, 1].axhline(y=0, color='r', linestyle='--', alpha=0.7)
        axes[0, 1].set_title('累计盈亏')
        axes[0, 1].set_xlabel('投注次数')
        axes[0, 1].set_ylabel('累计盈亏 ($)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 投注金额分布
        axes[1, 0].hist(df['bet_amount'], bins=20, alpha=0.7)
        axes[1, 0].set_title('投注金额分布')
        axes[1, 0].set_xlabel('投注金额 ($)')
        axes[1, 0].set_ylabel('频次')
        
        # 赔率vs盈亏
        colors = ['red' if x < 0 else 'green' for x in df['profit']]
        axes[1, 1].scatter(df['odds'], df['profit'], c=colors, alpha=0.6)
        axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
        axes[1, 1].set_title('赔率 vs 盈亏')
        axes[1, 1].set_xlabel('赔率')
        axes[1, 1].set_ylabel('盈亏 ($)')
        
        plt.tight_layout()
        plt.savefig('betting_performance.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_sample_odds(self, num_matches=100):
        """生成示例赔率数据"""
        odds_data = []
        
        for i in range(num_matches):
            # 生成随机但合理的赔率
            home_prob = np.random.uniform(0.25, 0.65)
            away_prob = np.random.uniform(0.15, 0.55)
            draw_prob = 1 - home_prob - away_prob
            
            if draw_prob < 0.1:
                draw_prob = 0.1
                total = home_prob + away_prob + draw_prob
                home_prob = home_prob / total
                away_prob = away_prob / total
                draw_prob = draw_prob / total
            
            # 转换为赔率（加入书商利润）
            margin = 0.05  # 5%利润率
            home_odds = (1 / home_prob) * (1 - margin)
            draw_odds = (1 / draw_prob) * (1 - margin)
            away_odds = (1 / away_prob) * (1 - margin)
            
            odds_data.append({
                'home_odds': round(home_odds, 2),
                'draw_odds': round(draw_odds, 2),
                'away_odds': round(away_odds, 2)
            })
        
        return pd.DataFrame(odds_data)

def compare_strategies(predictions_df, odds_df):
    """比较不同投注策略"""
    strategies = ['kelly', 'value', 'fixed']
    results = {}
    
    for strategy in strategies:
        print(f"\n=== 测试 {strategy.upper()} 策略 ===")
        betting = BettingStrategy(initial_bankroll=1000)
        betting.simulate_betting(predictions_df, odds_df, strategy=strategy)
        performance = betting.analyze_performance()
        results[strategy] = performance
    
    # 比较结果
    print("\n=== 策略比较 ===")
    comparison_df = pd.DataFrame(results).T
    print(comparison_df)
    
    return results

if __name__ == "__main__":
    # 生成示例预测数据
    np.random.seed(42)
    n_matches = 100
    
    predictions_data = []
    for i in range(n_matches):
        # 模拟预测结果
        actual = np.random.choice(['H', 'D', 'A'], p=[0.45, 0.25, 0.3])
        
        # 模型预测（有一定准确率）
        if np.random.random() < 0.6:  # 60%准确率
            predicted = actual
            confidence = np.random.uniform(0.6, 0.9)
        else:
            predicted = np.random.choice(['H', 'D', 'A'])
            confidence = np.random.uniform(0.4, 0.7)
        
        # 生成概率分布
        if predicted == 'H':
            prob_H = confidence
            prob_D = (1 - confidence) * 0.4
            prob_A = (1 - confidence) * 0.6
        elif predicted == 'D':
            prob_D = confidence
            prob_H = (1 - confidence) * 0.6
            prob_A = (1 - confidence) * 0.4
        else:
            prob_A = confidence
            prob_H = (1 - confidence) * 0.6
            prob_D = (1 - confidence) * 0.4
        
        predictions_data.append({
            'date': datetime.now() - timedelta(days=i),
            'home_team': f'Team{i%10}',
            'away_team': f'Team{(i+5)%10}',
            'predicted_result': predicted,
            'actual_result': actual,
            'confidence': confidence,
            'prob_H': prob_H,
            'prob_D': prob_D,
            'prob_A': prob_A
        })
    
    predictions_df = pd.DataFrame(predictions_data)
    
    # 生成赔率数据
    betting = BettingStrategy()
    odds_df = betting.generate_sample_odds(n_matches)
    
    # 比较不同策略
    strategy_results = compare_strategies(predictions_df, odds_df)
    
    # 详细分析最佳策略
    best_strategy = max(strategy_results.keys(), 
                       key=lambda x: strategy_results[x]['final_bankroll'])
    
    print(f"\n最佳策略: {best_strategy.upper()}")
    
    # 使用最佳策略进行详细分析
    betting = BettingStrategy(initial_bankroll=1000)
    betting.simulate_betting(predictions_df, odds_df, strategy=best_strategy)
    betting.analyze_performance()
    betting.plot_performance()