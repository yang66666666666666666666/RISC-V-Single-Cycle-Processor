"""
API使用示例
演示如何调用足球预测API
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_prediction():
    """测试比赛预测"""
    print("⚽ 测试比赛预测...")
    
    # 预测数据
    match_data = {
        "home_team": "Manchester City",
        "away_team": "Arsenal", 
        "home_strength": 0.75,
        "away_strength": 0.68,
        "home_form": 0.8,
        "away_form": 0.7
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=match_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"比赛: {result['home_team']} vs {result['away_team']}")
        print(f"预测结果: {result['prediction']}")
        print(f"置信度: {result['confidence']:.1%}")
        print("概率分布:")
        for outcome, prob in result['probabilities'].items():
            print(f"  {outcome}: {prob:.1%}")
    else:
        print(f"错误: {response.json()}")
    print()

def test_betting_advice():
    """测试投注建议"""
    print("💰 测试投注建议...")
    
    # 投注数据
    betting_data = {
        "prediction_confidence": 0.75,
        "odds": {
            "home": 2.5,
            "draw": 3.0,
            "away": 2.8
        },
        "bankroll": 1000,
        "strategy": "kelly",
        "min_confidence": 0.6,
        "min_edge": 0.05
    }
    
    response = requests.post(f"{BASE_URL}/betting", json=betting_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        advice = response.json()
        print(f"是否投注: {advice['should_bet']}")
        print(f"投注金额: ${advice['bet_amount']:.2f}")
        print(f"策略: {advice['strategy_used']}")
        print(f"原因: {advice['reason']}")
    else:
        print(f"错误: {response.json()}")
    print()

def test_simulation():
    """测试投注模拟"""
    print("📊 测试投注模拟...")
    
    # 模拟数据
    sim_data = {
        "num_matches": 30,
        "initial_bankroll": 1000,
        "strategy": "value",
        "min_confidence": 0.6
    }
    
    response = requests.post(f"{BASE_URL}/simulate", json=sim_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if 'performance' in result:
            perf = result['performance']
            print("模拟结果:")
            print(f"  总投注次数: {perf['total_bets']}")
            print(f"  胜率: {perf['win_rate']:.1%}")
            print(f"  总盈亏: ${perf['total_profit']:.2f}")
            print(f"  投资回报率: {perf['roi']:.1%}")
            print(f"  最终资金: ${perf['final_bankroll']:.2f}")
            
            print("\n前几次投注:")
            for i, bet in enumerate(result['bet_history'][:5], 1):
                print(f"  {i}. 预测:{bet['predicted']} 实际:{bet['actual']} "
                      f"赔率:{bet['odds']:.2f} 投注:${bet['bet_amount']:.2f} "
                      f"盈亏:${bet['profit']:.2f}")
        else:
            print(result['message'])
    else:
        print(f"错误: {response.json()}")
    print()

def main():
    """主函数"""
    print("🚀 足球预测API测试")
    print("=" * 50)
    
    try:
        # 测试各个API端点
        test_health()
        test_prediction()
        test_betting_advice()
        test_simulation()
        
        print("✅ 所有测试完成")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器")
        print("请确保API服务器正在运行: python api.py")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    main()