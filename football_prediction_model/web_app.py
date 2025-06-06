"""
足球预测Web应用
使用Streamlit创建交互式预测界面
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import joblib
import os

# 导入自定义模块
from data_collector import FootballDataCollector
from feature_engineering import FeatureEngineer
from model_trainer import FootballPredictor
from betting_strategy import BettingStrategy

class FootballPredictionApp:
    def __init__(self):
        self.predictor = None
        self.load_model()
    
    def load_model(self):
        """加载训练好的模型"""
        if os.path.exists('football_predictor.pkl'):
            self.predictor = FootballPredictor()
            self.predictor.load_model('football_predictor.pkl')
        else:
            st.warning("模型文件不存在，请先训练模型")
    
    def main(self):
        """主应用界面"""
        st.set_page_config(
            page_title="足球预测系统",
            page_icon="⚽",
            layout="wide"
        )
        
        st.title("⚽ 足球比赛预测系统")
        st.markdown("---")
        
        # 侧边栏导航
        page = st.sidebar.selectbox(
            "选择功能",
            ["比赛预测", "模型训练", "投注策略", "数据分析", "历史表现"]
        )
        
        if page == "比赛预测":
            self.prediction_page()
        elif page == "模型训练":
            self.training_page()
        elif page == "投注策略":
            self.betting_page()
        elif page == "数据分析":
            self.analysis_page()
        elif page == "历史表现":
            self.performance_page()
    
    def prediction_page(self):
        """比赛预测页面"""
        st.header("🔮 比赛预测")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("主队信息")
            home_team = st.text_input("主队名称", "Manchester City")
            home_win_rate = st.slider("主队胜率", 0.0, 1.0, 0.6, 0.01)
            home_ppg = st.slider("主队场均积分", 0.0, 3.0, 2.1, 0.1)
            home_goals_per_game = st.slider("主队场均进球", 0.0, 5.0, 2.2, 0.1)
            home_recent_form = st.slider("主队最近状态", 0.0, 1.0, 0.7, 0.01)
        
        with col2:
            st.subheader("客队信息")
            away_team = st.text_input("客队名称", "Arsenal")
            away_win_rate = st.slider("客队胜率", 0.0, 1.0, 0.55, 0.01)
            away_ppg = st.slider("客队场均积分", 0.0, 3.0, 1.9, 0.1)
            away_goals_per_game = st.slider("客队场均进球", 0.0, 5.0, 1.8, 0.1)
            away_recent_form = st.slider("客队最近状态", 0.0, 1.0, 0.6, 0.01)
        
        if st.button("预测比赛结果", type="primary"):
            if self.predictor is None:
                st.error("模型未加载，请先训练模型")
                return
            
            # 构建特征向量（简化版）
            features = [
                home_win_rate, home_ppg, 0, home_goals_per_game, 1.0,  # 主队特征
                away_win_rate, away_ppg, 0, away_goals_per_game, 1.0,  # 客队特征
                home_recent_form, 2, 1, away_recent_form, 1, 1,  # 最近表现
                0, 0, 0, 0, 0, 0,  # 历史交锋
                home_win_rate - away_win_rate,  # 实力差
                home_ppg - away_ppg,  # 积分差
                home_recent_form - away_recent_form,  # 状态差
                home_goals_per_game - 1.0,  # 攻防对比
                away_goals_per_game - 1.0,  # 攻防对比
                1  # 主场优势
            ]
            
            # 确保特征数量匹配
            while len(features) < len(self.predictor.feature_columns):
                features.append(0)
            features = features[:len(self.predictor.feature_columns)]
            
            try:
                # 进行预测
                features_array = np.array(features).reshape(1, -1)
                features_scaled = self.predictor.scaler.transform(features_array)
                
                prediction = self.predictor.best_model.predict(features_scaled)[0]
                probabilities = self.predictor.best_model.predict_proba(features_scaled)[0]
                
                result = self.predictor.label_encoder.inverse_transform([prediction])[0]
                
                # 显示预测结果
                st.success(f"预测结果: {self.get_result_text(result)}")
                
                # 显示概率分布
                prob_dict = {}
                for i, class_name in enumerate(self.predictor.label_encoder.classes_):
                    prob_dict[class_name] = probabilities[i]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("主队胜", f"{prob_dict.get('H', 0):.1%}")
                with col2:
                    st.metric("平局", f"{prob_dict.get('D', 0):.1%}")
                with col3:
                    st.metric("客队胜", f"{prob_dict.get('A', 0):.1%}")
                
                # 绘制概率图
                fig = go.Figure(data=[
                    go.Bar(x=['主队胜', '平局', '客队胜'], 
                          y=[prob_dict.get('H', 0), prob_dict.get('D', 0), prob_dict.get('A', 0)],
                          marker_color=['green', 'orange', 'red'])
                ])
                fig.update_layout(title="预测概率分布", yaxis_title="概率")
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"预测失败: {str(e)}")
    
    def training_page(self):
        """模型训练页面"""
        st.header("🤖 模型训练")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("训练设置")
            num_matches = st.slider("生成比赛数量", 100, 2000, 1000, 100)
            test_size = st.slider("测试集比例", 0.1, 0.4, 0.2, 0.05)
            
        with col2:
            st.subheader("模型选择")
            models = st.multiselect(
                "选择训练模型",
                ["Random Forest", "XGBoost", "LightGBM", "Logistic Regression"],
                default=["Random Forest", "XGBoost"]
            )
        
        if st.button("开始训练", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 生成数据
                status_text.text("正在生成训练数据...")
                progress_bar.progress(20)
                
                collector = FootballDataCollector()
                matches_df = collector.generate_sample_data(num_matches)
                
                # 特征工程
                status_text.text("正在进行特征工程...")
                progress_bar.progress(40)
                
                engineer = FeatureEngineer()
                features_df = engineer.create_features(matches_df)
                
                # 训练模型
                status_text.text("正在训练模型...")
                progress_bar.progress(60)
                
                self.predictor = FootballPredictor()
                X, y = self.predictor.prepare_data(features_df)
                results = self.predictor.train_models(X, y)
                
                progress_bar.progress(80)
                
                # 保存模型
                status_text.text("正在保存模型...")
                self.predictor.save_model()
                
                progress_bar.progress(100)
                status_text.text("训练完成！")
                
                # 显示结果
                st.success("模型训练完成！")
                
                # 显示模型性能
                st.subheader("模型性能")
                performance_data = []
                for name, result in results.items():
                    performance_data.append({
                        '模型': name,
                        '准确率': f"{result['accuracy']:.3f}",
                        'CV均值': f"{result['cv_mean']:.3f}",
                        'CV标准差': f"{result['cv_std']:.3f}"
                    })
                
                st.dataframe(pd.DataFrame(performance_data))
                
            except Exception as e:
                st.error(f"训练失败: {str(e)}")
    
    def betting_page(self):
        """投注策略页面"""
        st.header("💰 投注策略")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("策略设置")
            initial_bankroll = st.number_input("初始资金", 100, 10000, 1000, 100)
            strategy = st.selectbox("投注策略", ["kelly", "value", "fixed"])
            min_confidence = st.slider("最小置信度", 0.5, 0.9, 0.6, 0.05)
            
        with col2:
            st.subheader("风险控制")
            max_bet_ratio = st.slider("最大投注比例", 0.01, 0.25, 0.05, 0.01)
            min_edge = st.slider("最小优势", 0.01, 0.15, 0.05, 0.01)
            num_simulations = st.slider("模拟场次", 50, 500, 100, 50)
        
        if st.button("运行投注模拟", type="primary"):
            # 生成模拟数据
            betting = BettingStrategy(initial_bankroll)
            
            # 生成预测数据
            predictions_data = []
            for i in range(num_simulations):
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
                    'prob_H': 0.4 if predicted == 'H' else 0.3,
                    'prob_D': 0.4 if predicted == 'D' else 0.3,
                    'prob_A': 0.4 if predicted == 'A' else 0.3
                })
            
            predictions_df = pd.DataFrame(predictions_data)
            odds_df = betting.generate_sample_odds(num_simulations)
            
            # 运行模拟
            bet_history = betting.simulate_betting(
                predictions_df, odds_df, 
                strategy=strategy, 
                min_confidence=min_confidence
            )
            
            if bet_history:
                performance = betting.analyze_performance()
                
                # 显示结果
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总投注次数", performance['total_bets'])
                with col2:
                    st.metric("胜率", f"{performance['win_rate']:.1%}")
                with col3:
                    st.metric("总盈亏", f"${performance['total_profit']:.2f}")
                with col4:
                    st.metric("投资回报率", f"{performance['roi']:.1%}")
                
                # 绘制资金变化图
                df = pd.DataFrame(bet_history)
                fig = px.line(df, x=df.index, y='bankroll', title='资金变化')
                fig.add_hline(y=initial_bankroll, line_dash="dash", line_color="red")
                st.plotly_chart(fig, use_container_width=True)
                
                # 显示投注历史
                st.subheader("投注历史")
                st.dataframe(df[['home_team', 'away_team', 'predicted', 'actual', 
                               'confidence', 'odds', 'bet_amount', 'profit']].head(20))
            else:
                st.warning("没有符合条件的投注")
    
    def analysis_page(self):
        """数据分析页面"""
        st.header("📊 数据分析")
        
        # 生成示例数据进行分析
        if st.button("生成分析数据"):
            collector = FootballDataCollector()
            matches_df = collector.generate_sample_data(500)
            
            # 基本统计
            st.subheader("比赛结果分布")
            result_counts = matches_df['result'].value_counts()
            fig = px.pie(values=result_counts.values, names=['主队胜', '平局', '客队胜'])
            st.plotly_chart(fig, use_container_width=True)
            
            # 进球分布
            st.subheader("进球分布")
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.histogram(matches_df, x='home_goals', title='主队进球分布')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.histogram(matches_df, x='away_goals', title='客队进球分布')
                st.plotly_chart(fig, use_container_width=True)
            
            # 球队表现
            st.subheader("球队表现分析")
            team_stats = []
            teams = matches_df['home_team'].unique()
            
            for team in teams[:10]:  # 只显示前10支球队
                home_matches = matches_df[matches_df['home_team'] == team]
                away_matches = matches_df[matches_df['away_team'] == team]
                
                total_games = len(home_matches) + len(away_matches)
                wins = len(home_matches[home_matches['result'] == 'H']) + \
                       len(away_matches[away_matches['result'] == 'A'])
                
                team_stats.append({
                    '球队': team,
                    '比赛场次': total_games,
                    '胜场': wins,
                    '胜率': wins / total_games if total_games > 0 else 0
                })
            
            team_df = pd.DataFrame(team_stats)
            fig = px.bar(team_df, x='球队', y='胜率', title='球队胜率')
            st.plotly_chart(fig, use_container_width=True)
    
    def performance_page(self):
        """历史表现页面"""
        st.header("📈 历史表现")
        
        if os.path.exists('football_predictor.pkl') and self.predictor:
            st.success("模型已加载")
            
            # 显示模型信息
            st.subheader("模型信息")
            if hasattr(self.predictor, 'models') and self.predictor.models:
                model_info = []
                for name, result in self.predictor.models.items():
                    model_info.append({
                        '模型': name,
                        '准确率': f"{result['accuracy']:.3f}",
                        'CV分数': f"{result['cv_mean']:.3f} ± {result['cv_std']:.3f}"
                    })
                
                st.dataframe(pd.DataFrame(model_info))
            
            # 特征重要性
            if hasattr(self.predictor.best_model, 'feature_importances_'):
                st.subheader("特征重要性")
                importances = self.predictor.best_model.feature_importances_
                feature_df = pd.DataFrame({
                    '特征': self.predictor.feature_columns,
                    '重要性': importances
                }).sort_values('重要性', ascending=False).head(10)
                
                fig = px.bar(feature_df, x='重要性', y='特征', orientation='h')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("请先训练模型")
    
    def get_result_text(self, result):
        """获取结果文本"""
        if result == 'H':
            return "主队胜"
        elif result == 'D':
            return "平局"
        elif result == 'A':
            return "客队胜"
        else:
            return "未知"

def main():
    app = FootballPredictionApp()
    app.main()

if __name__ == "__main__":
    main()