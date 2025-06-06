"""
足球预测系统演示
展示模型预测和投注策略功能
"""

import pandas as pd
import numpy as np
from model_trainer import FootballPredictor
from betting_strategy import BettingStrategy
import matplotlib.pyplot as plt

def demo_prediction():
    """演示预测功能"""
    print("=== 足球预测系统演示 ===\n")
    
    # 加载模型
    predictor = FootballPredictor()
    try:
        predictor.load_model('football_predictor.pkl')
        print("✅ 模型加载成功")
    except:
        print("❌ 模型文件不存在，请先运行 model_trainer.py")
        return
    
    # 演示比赛预测
    print("\n📊 比赛预测演示")
    print("-" * 50)
    
    # 示例比赛
    matches = [
        {
            'home_team': 'Manchester City',
            'away_team': 'Arsenal',
            'home_strength': 0.75,
            'away_strength': 0.68,
            'home_form': 0.8,
            'away_form': 0.7
        },
        {
            'home_team': 'Liverpool',
            'away_team': 'Chelsea',
            'home_strength': 0.72,
            'away_strength': 0.65,
            'home_form': 0.75,
            'away_form': 0.6
        },
        {
            'home_team': 'Tottenham',
            'away_team': 'Manchester United',
            'home_strength': 0.6,
            'away_strength': 0.62,
            'home_form': 0.5,
            'away_form': 0.65
        }
    ]
    
    predictions = []
    
    for i, match in enumerate(matches, 1):
        print(f"\n🏟️  比赛 {i}: {match['home_team']} vs {match['away_team']}")
        
        # 构建特征向量（简化版）
        features = [
            match['home_strength'], 2.1, 5, 1.8, 1.2,  # 主队特征
            match['away_strength'], 1.9, 2, 1.6, 1.3,  # 客队特征
            match['home_form'], 8, 2, match['away_form'], 6, 1,  # 最近表现
            3, 1, 1, 1, 4, 3,  # 历史交锋
            match['home_strength'] - match['away_strength'],  # 实力差
            0.2, match['home_form'] - match['away_form'],  # 状态差
            0.2, -0.1, 1  # 攻防对比和主场优势
        ]
        
        # 确保特征数量匹配
        while len(features) < len(predictor.feature_columns):
            features.append(0)
        features = features[:len(predictor.feature_columns)]
        
        try:
            # 进行预测
            features_array = np.array(features).reshape(1, -1)
            features_scaled = predictor.scaler.transform(features_array)
            
            prediction = predictor.best_model.predict(features_scaled)[0]
            probabilities = predictor.best_model.predict_proba(features_scaled)[0]
            
            result = predictor.label_encoder.inverse_transform([prediction])[0]
            
            # 获取概率分布
            prob_dict = {}
            for j, class_name in enumerate(predictor.label_encoder.classes_):
                prob_dict[class_name] = probabilities[j]
            
            # 显示预测结果
            result_text = {
                'H': f"🏆 {match['home_team']} 胜",
                'D': "🤝 平局",
                'A': f"🏆 {match['away_team']} 胜"
            }
            
            print(f"   预测结果: {result_text.get(result, '未知')}")
            print(f"   置信度: {max(probabilities):.1%}")
            print(f"   概率分布:")
            print(f"     主队胜: {prob_dict.get('H', 0):.1%}")
            print(f"     平局:   {prob_dict.get('D', 0):.1%}")
            print(f"     客队胜: {prob_dict.get('A', 0):.1%}")
            
            predictions.append({
                'match': f"{match['home_team']} vs {match['away_team']}",
                'prediction': result,
                'confidence': max(probabilities),
                'prob_H': prob_dict.get('H', 0),
                'prob_D': prob_dict.get('D', 0),
                'prob_A': prob_dict.get('A', 0)
            })
            
        except Exception as e:
            print(f"   ❌ 预测失败: {str(e)}")
    
    return predictions

def demo_betting_strategy():
    """演示投注策略"""
    print("\n\n💰 投注策略演示")
    print("-" * 50)
    
    # 生成模拟数据
    np.random.seed(42)
    n_matches = 50
    
    print(f"📈 模拟 {n_matches} 场比赛的投注策略...")
    
    # 生成预测数据
    predictions_data = []
    for i in range(n_matches):
        actual = np.random.choice(['H', 'D', 'A'], p=[0.45, 0.25, 0.3])
        
        # 模型预测（60%准确率）
        if np.random.random() < 0.6:
            predicted = actual
            confidence = np.random.uniform(0.6, 0.9)
        else:
            predicted = np.random.choice(['H', 'D', 'A'])
            confidence = np.random.uniform(0.4, 0.7)
        
        predictions_data.append({
            'predicted_result': predicted,
            'actual_result': actual,
            'confidence': confidence,
            'prob_H': 0.5 if predicted == 'H' else 0.25,
            'prob_D': 0.5 if predicted == 'D' else 0.25,
            'prob_A': 0.5 if predicted == 'A' else 0.25
        })
    
    predictions_df = pd.DataFrame(predictions_data)
    
    # 测试不同策略
    strategies = {
        'kelly': '凯利公式',
        'value': '价值投注',
        'fixed': '固定投注'
    }
    
    results = {}
    
    for strategy_key, strategy_name in strategies.items():
        print(f"\n🎯 测试 {strategy_name} 策略:")
        
        betting = BettingStrategy(initial_bankroll=1000)
        odds_df = betting.generate_sample_odds(n_matches)
        
        bet_history = betting.simulate_betting(
            predictions_df, odds_df, 
            strategy=strategy_key, 
            min_confidence=0.6
        )
        
        if bet_history:
            performance = betting.analyze_performance()
            results[strategy_name] = performance
            
            print(f"   投注次数: {performance['total_bets']}")
            print(f"   胜率: {performance['win_rate']:.1%}")
            print(f"   总盈亏: ${performance['total_profit']:.2f}")
            print(f"   投资回报率: {performance['roi']:.1%}")
            print(f"   最终资金: ${performance['final_bankroll']:.2f}")
        else:
            print("   没有符合条件的投注")
    
    # 策略比较
    if results:
        print(f"\n📊 策略比较总结:")
        print("-" * 30)
        best_strategy = max(results.keys(), key=lambda x: results[x]['final_bankroll'])
        
        for strategy_name, performance in results.items():
            status = "🏆 最佳" if strategy_name == best_strategy else "  "
            print(f"{status} {strategy_name}:")
            print(f"     最终资金: ${performance['final_bankroll']:.2f}")
            print(f"     投资回报率: {performance['roi']:.1%}")
            print(f"     胜率: {performance['win_rate']:.1%}")
    
    return results

def demo_risk_analysis():
    """风险分析演示"""
    print("\n\n⚠️  风险分析")
    print("-" * 50)
    
    print("📋 重要风险提示:")
    print("1. 🎲 足球比赛存在很多不可预测因素")
    print("2. 📊 模型准确率有限，不能保证盈利")
    print("3. 💸 任何投注都存在亏损风险")
    print("4. 🎯 建议严格控制投注比例（不超过总资金的5%）")
    print("5. 🧠 理性投注，避免情绪化决策")
    
    print("\n💡 使用建议:")
    print("1. 📈 将此系统作为辅助决策工具")
    print("2. 🔍 结合其他信息源进行综合分析")
    print("3. 📝 记录投注历史，持续优化策略")
    print("4. 🛡️  设置止损点，控制最大亏损")
    print("5. 📚 不断学习和改进预测模型")

def main():
    """主演示函数"""
    print("🚀 启动足球预测系统演示...\n")
    
    # 预测演示
    predictions = demo_prediction()
    
    # 投注策略演示
    betting_results = demo_betting_strategy()
    
    # 风险分析
    demo_risk_analysis()
    
    print("\n" + "="*60)
    print("🎉 演示完成！")
    print("📁 生成的文件:")
    print("   - football_matches.csv (比赛数据)")
    print("   - football_features.csv (特征数据)")
    print("   - football_predictor.pkl (训练好的模型)")
    print("   - confusion_matrices.png (混淆矩阵图)")
    print("   - feature_importance.png (特征重要性图)")
    print("   - betting_performance.png (投注表现图)")
    print("\n🌐 启动Web应用: streamlit run web_app.py")
    print("="*60)

if __name__ == "__main__":
    main()