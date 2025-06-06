"""
足球预测API
提供RESTful API接口进行比赛预测
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from model_trainer import FootballPredictor
from betting_strategy import BettingStrategy
import joblib
import os

app = Flask(__name__)

# 全局变量
predictor = None

def load_model():
    """加载预测模型"""
    global predictor
    if os.path.exists('football_predictor.pkl'):
        predictor = FootballPredictor()
        predictor.load_model('football_predictor.pkl')
        return True
    return False

@app.route('/')
def home():
    """API首页"""
    return jsonify({
        'message': '足球预测API',
        'version': '1.0',
        'endpoints': {
            '/predict': 'POST - 预测比赛结果',
            '/betting': 'POST - 投注策略建议',
            '/health': 'GET - 健康检查'
        }
    })

@app.route('/health')
def health():
    """健康检查"""
    model_loaded = predictor is not None
    return jsonify({
        'status': 'healthy' if model_loaded else 'model_not_loaded',
        'model_loaded': model_loaded
    })

@app.route('/predict', methods=['POST'])
def predict_match():
    """预测比赛结果"""
    if predictor is None:
        return jsonify({'error': '模型未加载'}), 500
    
    try:
        data = request.json
        
        # 验证输入数据
        required_fields = ['home_team', 'away_team', 'home_strength', 'away_strength']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        # 构建特征向量
        home_strength = float(data['home_strength'])
        away_strength = float(data['away_strength'])
        home_form = float(data.get('home_form', 0.5))
        away_form = float(data.get('away_form', 0.5))
        
        features = [
            home_strength, 2.0, 0, 1.5, 1.0,  # 主队特征
            away_strength, 1.8, 0, 1.3, 1.0,  # 客队特征
            home_form, 5, 2, away_form, 4, 1,  # 最近表现
            2, 1, 0, 1, 3, 2,  # 历史交锋
            home_strength - away_strength,  # 实力差
            0.2, home_form - away_form,  # 状态差
            0.1, -0.1, 1  # 攻防对比和主场优势
        ]
        
        # 确保特征数量匹配
        while len(features) < len(predictor.feature_columns):
            features.append(0)
        features = features[:len(predictor.feature_columns)]
        
        # 进行预测
        features_array = np.array(features).reshape(1, -1)
        features_scaled = predictor.scaler.transform(features_array)
        
        prediction = predictor.best_model.predict(features_scaled)[0]
        probabilities = predictor.best_model.predict_proba(features_scaled)[0]
        
        result = predictor.label_encoder.inverse_transform([prediction])[0]
        
        # 构建概率字典
        prob_dict = {}
        for i, class_name in enumerate(predictor.label_encoder.classes_):
            prob_dict[class_name] = float(probabilities[i])
        
        # 结果映射
        result_mapping = {
            'H': 'home_win',
            'D': 'draw',
            'A': 'away_win'
        }
        
        response = {
            'home_team': data['home_team'],
            'away_team': data['away_team'],
            'prediction': result_mapping.get(result, 'unknown'),
            'confidence': float(max(probabilities)),
            'probabilities': {
                'home_win': prob_dict.get('H', 0),
                'draw': prob_dict.get('D', 0),
                'away_win': prob_dict.get('A', 0)
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/betting', methods=['POST'])
def betting_advice():
    """投注策略建议"""
    try:
        data = request.json
        
        # 验证输入数据
        required_fields = ['prediction_confidence', 'odds']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        confidence = float(data['prediction_confidence'])
        odds = data['odds']  # {'home': 2.5, 'draw': 3.0, 'away': 2.8}
        bankroll = float(data.get('bankroll', 1000))
        strategy = data.get('strategy', 'kelly')
        min_confidence = float(data.get('min_confidence', 0.6))
        min_edge = float(data.get('min_edge', 0.05))
        
        betting = BettingStrategy(bankroll)
        
        advice = {
            'should_bet': False,
            'bet_amount': 0,
            'strategy_used': strategy,
            'reason': ''
        }
        
        # 检查置信度
        if confidence < min_confidence:
            advice['reason'] = f'置信度过低 ({confidence:.1%} < {min_confidence:.1%})'
            return jsonify(advice)
        
        # 根据策略计算投注建议
        if strategy == 'kelly':
            # 假设预测主队胜
            kelly_fraction = betting.kelly_criterion(confidence, odds.get('home', 2.0))
            if kelly_fraction > 0:
                advice['should_bet'] = True
                advice['bet_amount'] = bankroll * kelly_fraction
                advice['reason'] = f'凯利公式建议投注 {kelly_fraction:.1%} 的资金'
            else:
                advice['reason'] = '凯利公式不建议投注'
                
        elif strategy == 'value':
            home_odds = odds.get('home', 2.0)
            implied_prob = 1 / home_odds
            edge = confidence - implied_prob
            
            if edge > min_edge:
                advice['should_bet'] = True
                advice['bet_amount'] = bankroll * 0.02  # 固定2%
                advice['reason'] = f'发现价值投注机会，优势: {edge:.1%}'
            else:
                advice['reason'] = f'无价值投注机会，优势: {edge:.1%}'
                
        elif strategy == 'fixed':
            if confidence >= min_confidence:
                advice['should_bet'] = True
                advice['bet_amount'] = min(50, bankroll * 0.05)  # 固定50或5%
                advice['reason'] = '固定投注策略'
            else:
                advice['reason'] = '置信度不足'
        
        # 限制最大投注金额
        if advice['bet_amount'] > bankroll * 0.25:
            advice['bet_amount'] = bankroll * 0.25
            advice['reason'] += ' (限制最大投注比例25%)'
        
        return jsonify(advice)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/simulate', methods=['POST'])
def simulate_betting():
    """模拟投注策略"""
    try:
        data = request.json
        
        num_matches = int(data.get('num_matches', 50))
        initial_bankroll = float(data.get('initial_bankroll', 1000))
        strategy = data.get('strategy', 'kelly')
        min_confidence = float(data.get('min_confidence', 0.6))
        
        # 生成模拟数据
        np.random.seed(42)
        predictions_data = []
        
        for i in range(num_matches):
            actual = np.random.choice(['H', 'D', 'A'], p=[0.45, 0.25, 0.3])
            
            if np.random.random() < 0.6:  # 60%准确率
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
        
        # 运行投注模拟
        betting = BettingStrategy(initial_bankroll)
        odds_df = betting.generate_sample_odds(num_matches)
        
        bet_history = betting.simulate_betting(
            predictions_df, odds_df,
            strategy=strategy,
            min_confidence=min_confidence
        )
        
        if bet_history:
            performance = betting.analyze_performance()
            
            # 简化投注历史（只返回前10条）
            simplified_history = []
            for bet in bet_history[:10]:
                simplified_history.append({
                    'predicted': bet['predicted'],
                    'actual': bet['actual'],
                    'confidence': bet['confidence'],
                    'odds': bet['odds'],
                    'bet_amount': bet['bet_amount'],
                    'profit': bet['profit']
                })
            
            response = {
                'performance': {
                    'total_bets': performance['total_bets'],
                    'win_rate': performance['win_rate'],
                    'total_profit': performance['total_profit'],
                    'roi': performance['roi'],
                    'final_bankroll': performance['final_bankroll']
                },
                'bet_history': simplified_history
            }
            
            return jsonify(response)
        else:
            return jsonify({'message': '没有符合条件的投注'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 启动时加载模型
    if load_model():
        print("✅ 模型加载成功")
    else:
        print("❌ 模型加载失败，请先训练模型")
    
    # 启动API服务
    app.run(host='0.0.0.0', port=5000, debug=True)