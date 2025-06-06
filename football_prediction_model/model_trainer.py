"""
机器学习模型训练器
训练多种模型来预测足球比赛结果
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
import lightgbm as lgb
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

class FootballPredictor:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        self.best_model = None
        self.best_score = 0
        
    def prepare_data(self, features_df):
        """准备训练数据"""
        # 移除非数值特征
        exclude_cols = ['home_team', 'away_team', 'result']
        self.feature_columns = [col for col in features_df.columns if col not in exclude_cols]
        
        X = features_df[self.feature_columns].fillna(0)
        y = features_df['result']
        
        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=self.feature_columns)
        
        # 编码标签
        y_encoded = self.label_encoder.fit_transform(y)
        
        return X_scaled, y_encoded
    
    def train_models(self, X, y):
        """训练多种机器学习模型"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 定义模型
        models_config = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'SVM': SVC(random_state=42, probability=True),
            'XGBoost': xgb.XGBClassifier(random_state=42),
            'LightGBM': lgb.LGBMClassifier(random_state=42, verbose=-1)
        }
        
        results = {}
        
        for name, model in models_config.items():
            print(f"训练 {name}...")
            
            # 训练模型
            model.fit(X_train, y_train)
            
            # 预测
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)
            
            # 评估
            accuracy = accuracy_score(y_test, y_pred)
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'predictions': y_pred,
                'probabilities': y_pred_proba
            }
            
            print(f"{name} - 准确率: {accuracy:.4f}, CV均值: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
            # 更新最佳模型
            if cv_scores.mean() > self.best_score:
                self.best_score = cv_scores.mean()
                self.best_model = model
        
        self.models = results
        self.X_test = X_test
        self.y_test = y_test
        
        return results
    
    def optimize_best_model(self, X, y):
        """优化最佳模型的超参数"""
        if self.best_model is None:
            print("请先训练模型")
            return
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 根据最佳模型类型定义参数网格
        if isinstance(self.best_model, RandomForestClassifier):
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        elif isinstance(self.best_model, xgb.XGBClassifier):
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 6, 10],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0]
            }
        else:
            print("当前最佳模型不支持超参数优化")
            return
        
        print("正在进行超参数优化...")
        grid_search = GridSearchCV(
            self.best_model, param_grid, cv=5, scoring='accuracy', n_jobs=-1
        )
        grid_search.fit(X_train, y_train)
        
        self.best_model = grid_search.best_estimator_
        print(f"最佳参数: {grid_search.best_params_}")
        print(f"最佳CV分数: {grid_search.best_score_:.4f}")
        
        # 在测试集上评估优化后的模型
        y_pred = self.best_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"测试集准确率: {accuracy:.4f}")
    
    def evaluate_models(self):
        """评估所有模型"""
        print("\n=== 模型评估结果 ===")
        
        for name, result in self.models.items():
            print(f"\n{name}:")
            print(f"准确率: {result['accuracy']:.4f}")
            print(f"交叉验证: {result['cv_mean']:.4f} (+/- {result['cv_std'] * 2:.4f})")
            
            # 分类报告
            print("\n分类报告:")
            print(classification_report(
                self.y_test, 
                result['predictions'],
                target_names=self.label_encoder.classes_
            ))
    
    def plot_confusion_matrices(self):
        """绘制混淆矩阵"""
        n_models = len(self.models)
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.ravel()
        
        for i, (name, result) in enumerate(self.models.items()):
            if i < len(axes):
                cm = confusion_matrix(self.y_test, result['predictions'])
                sns.heatmap(cm, annot=True, fmt='d', ax=axes[i], 
                           xticklabels=self.label_encoder.classes_,
                           yticklabels=self.label_encoder.classes_)
                axes[i].set_title(f'{name}\n准确率: {result["accuracy"]:.3f}')
                axes[i].set_xlabel('预测')
                axes[i].set_ylabel('实际')
        
        # 隐藏多余的子图
        for i in range(len(self.models), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig('confusion_matrices.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def feature_importance(self):
        """分析特征重要性"""
        if self.best_model is None:
            print("请先训练模型")
            return
        
        # 获取特征重要性
        if hasattr(self.best_model, 'feature_importances_'):
            importances = self.best_model.feature_importances_
            feature_importance_df = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            print("\n=== 特征重要性 ===")
            print(feature_importance_df.head(10))
            
            # 绘制特征重要性图
            plt.figure(figsize=(10, 8))
            sns.barplot(data=feature_importance_df.head(15), 
                       x='importance', y='feature')
            plt.title('前15个最重要特征')
            plt.xlabel('重要性')
            plt.tight_layout()
            plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            return feature_importance_df
    
    def predict_match(self, home_team_features, away_team_features):
        """预测单场比赛"""
        if self.best_model is None:
            print("请先训练模型")
            return None
        
        # 构建特征向量
        features = np.array([home_team_features + away_team_features]).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        
        # 预测
        prediction = self.best_model.predict(features_scaled)[0]
        probabilities = self.best_model.predict_proba(features_scaled)[0]
        
        result = self.label_encoder.inverse_transform([prediction])[0]
        
        prob_dict = {}
        for i, class_name in enumerate(self.label_encoder.classes_):
            prob_dict[class_name] = probabilities[i]
        
        return {
            'prediction': result,
            'probabilities': prob_dict,
            'confidence': max(probabilities)
        }
    
    def save_model(self, filename='football_predictor.pkl'):
        """保存训练好的模型"""
        model_data = {
            'best_model': self.best_model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'models': self.models
        }
        joblib.dump(model_data, filename)
        print(f"模型已保存到 {filename}")
    
    def load_model(self, filename='football_predictor.pkl'):
        """加载训练好的模型"""
        model_data = joblib.load(filename)
        self.best_model = model_data['best_model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_columns = model_data['feature_columns']
        self.models = model_data['models']
        print(f"模型已从 {filename} 加载")

if __name__ == "__main__":
    # 加载特征数据
    print("加载特征数据...")
    features_df = pd.read_csv('football_features.csv')
    
    # 初始化预测器
    predictor = FootballPredictor()
    
    # 准备数据
    print("准备训练数据...")
    X, y = predictor.prepare_data(features_df)
    
    # 训练模型
    print("开始训练模型...")
    results = predictor.train_models(X, y)
    
    # 评估模型
    predictor.evaluate_models()
    
    # 优化最佳模型
    print("\n优化最佳模型...")
    predictor.optimize_best_model(X, y)
    
    # 分析特征重要性
    predictor.feature_importance()
    
    # 绘制混淆矩阵
    predictor.plot_confusion_matrices()
    
    # 保存模型
    predictor.save_model()
    
    print("\n模型训练完成！")