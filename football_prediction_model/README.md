# 足球预测模型系统

一个基于机器学习的足球比赛结果预测系统，包含数据收集、特征工程、模型训练、投注策略和Web界面。

## 🚀 功能特点

### 核心功能
- **数据收集**: 自动收集足球比赛数据和统计信息
- **特征工程**: 提取和构建预测特征（球队实力、最近表现、历史交锋等）
- **机器学习**: 使用多种算法训练预测模型（随机森林、XGBoost、LightGBM等）
- **投注策略**: 实现多种投注策略（凯利公式、价值投注、固定投注）
- **Web界面**: 提供直观的预测和分析界面

### 预测特征
- 球队整体实力（胜率、场均积分、进球数等）
- 最近表现（最近5场比赛状态）
- 历史交锋记录
- 主客场优势
- 攻防能力对比

### 投注策略
- **凯利公式**: 基于概率和赔率计算最优投注比例
- **价值投注**: 寻找市场定价错误的投注机会
- **固定投注**: 固定金额或比例投注

## 📦 安装和使用

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 生成训练数据
```bash
python data_collector.py
```

### 3. 训练模型
```bash
python feature_engineering.py
python model_trainer.py
```

### 4. 测试投注策略
```bash
python betting_strategy.py
```

### 5. 启动Web应用
```bash
streamlit run web_app.py
```

## 🔧 模块说明

### data_collector.py
- 数据收集器，生成示例比赛数据
- 支持从API获取真实数据（需要API密钥）
- 包含球队统计、比赛结果、技术统计等

### feature_engineering.py
- 特征工程模块，从原始数据提取预测特征
- 计算球队实力指标
- 分析最近表现和历史交锋
- 构建机器学习特征矩阵

### model_trainer.py
- 机器学习模型训练器
- 支持多种算法：随机森林、XGBoost、LightGBM、逻辑回归、SVM
- 自动模型选择和超参数优化
- 模型评估和特征重要性分析

### betting_strategy.py
- 投注策略实现
- 凯利公式计算最优投注比例
- 价值投注识别
- 投注模拟和收益分析

### web_app.py
- Streamlit Web应用
- 交互式预测界面
- 模型训练和投注策略测试
- 数据可视化和分析

## 📊 使用示例

### 预测单场比赛
```python
from model_trainer import FootballPredictor

# 加载训练好的模型
predictor = FootballPredictor()
predictor.load_model('football_predictor.pkl')

# 预测比赛结果
features = [0.6, 2.1, 0, 2.2, 1.0, ...]  # 特征向量
result = predictor.predict_match(features)
print(f"预测结果: {result['prediction']}")
print(f"置信度: {result['confidence']:.2%}")
```

### 投注策略回测
```python
from betting_strategy import BettingStrategy

# 初始化投注策略
betting = BettingStrategy(initial_bankroll=1000)

# 运行投注模拟
bet_history = betting.simulate_betting(
    predictions_df, odds_df, 
    strategy='kelly', 
    min_confidence=0.6
)

# 分析投注表现
performance = betting.analyze_performance()
print(f"投资回报率: {performance['roi']:.2%}")
```

## 🎯 模型性能

基于示例数据的测试结果：
- **准确率**: 60-65%
- **最佳模型**: XGBoost/Random Forest
- **重要特征**: 球队实力差、最近表现、主场优势

## 💡 投注策略表现

不同策略的回测结果：
- **凯利公式**: 风险调整后收益最优
- **价值投注**: 长期稳定盈利
- **固定投注**: 风险最低但收益有限

## ⚠️ 风险提示

1. **模型局限性**: 足球比赛存在很多不可预测因素
2. **数据质量**: 预测准确性依赖于数据质量
3. **投注风险**: 任何投注都存在亏损风险
4. **资金管理**: 严格控制投注比例，避免过度投注

## 🔮 改进方向

### 数据增强
- 集成更多数据源（球员伤病、天气、裁判等）
- 实时数据更新
- 更长的历史数据

### 模型优化
- 深度学习模型（神经网络）
- 集成学习方法
- 在线学习和模型更新

### 策略改进
- 动态投注策略
- 多市场投注（让球、大小球等）
- 风险对冲策略

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 联系方式

如有问题或建议，请通过GitHub Issues联系。

---

**免责声明**: 本项目仅用于教育和研究目的。投注有风险，请谨慎决策。