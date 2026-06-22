# 离线训练，python manage.py
"""
训练薪资预测模型
"""
import pickle
import re

from catboost import CatBoostRegressor
import numpy as np
from sklearn.calibration import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
# 所有评分函数都在 sklearn.metrics 中，这里只导入了常用的几个
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from django.core.management.base import BaseCommand
import logging
import pandas as pd
from apps.jobs.models import Job
from job_analysis.app_config import MODEL_DIR


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_salary_model")

class Command(BaseCommand):
    """
    训练薪资预测模型
    """
    help = "训练薪资预测模型"

    def handle(self, *args, **options):
        """
        处理命令逻辑
        """
        logger.info("开始训练薪资预测模型")
        # 读数据库，取所有有 month_salary_avg 的岗位
        results = pd.DataFrame(Job.objects\
                .filter(month_salary_avg__isnull=False)\
                .values("category", "location_city", "experience_level", 
                        "education","company_scale_min","company_scale_max", "company_industry", 
                        "has_weekend_off", "month_salary_avg"))
        
        # 填充空值
        results["company_scale_min"] = results["company_scale_min"].fillna(0)
        results["company_scale_max"] = results["company_scale_max"].fillna(0)
        results["has_weekend_off"] = results["has_weekend_off"].fillna(False)

        # 经验等级和学历要求转为有序数值
        exp_map = {
            "经验不限": 0, "实习生": 1, "应届生": 2, 
            "1-3年": 3, "3-5年": 4, "5-10年": 5
        }
        edu_map = {
            "学历不限": 0, "大专": 1, "本科": 2, "统招本科": 3, "硕士": 4, "博士": 5
        }
        results["exp_numeric"] = results["experience_level"].map(exp_map)
        results["edu_numeric"] = results["education"].map(edu_map)

        # 特征列
        feature_cols = ["category", "location_city", "exp_numeric", "edu_numeric",
                "company_scale_min", "company_scale_max", "company_industry", "has_weekend_off"]

        # 类别特征（CatBoost 需要的）—— 只保留真正的无序类别
        cat_features_cols = ["category", "location_city", "company_industry"]
        
        # 目标列
        target_col = results["month_salary_avg"]
        
        # 原始字符串数据（给CatBoost用）
        X_raw = results[feature_cols].fillna(0)
        cat_feature_indices = [0, 1, 6]
        
        # 编码后的数值数据（给Random Forest用）
        X_encoded = X_raw.copy()
        encoders = {}
        for col in cat_features_cols:
            le = LabelEncoder()
            X_encoded[col] = le.fit_transform(X_encoded[col].fillna("未知"))
            encoders[col] = le
        
        # 划分数据集
        X_train, X_test, y_train, y_test = train_test_split(
                X_encoded, target_col, test_size=0.2, random_state=42)
        
        # 定义模型
        models = {
            "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
            "CatBoost": CatBoostRegressor(iterations=500, random_state=42, verbose=0),
        }

        # 训练模型
        for name, model in models.items():
            logger.info(f"开始训练模型 {name}")
            # 训练模型
            if name == "CatBoost":
                # 传原始字符串，用同样的索引划分
                X_train_raw = X_raw.iloc[X_train.index]
                model.fit(X_train_raw, y_train, cat_features=cat_feature_indices)   # 传类别特征的索引位置
                y_pred = model.predict(X_raw.iloc[X_test.index])
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))  # 排查模型是否出现严重离谱薪资预测
            r2 = r2_score(y_test, y_pred)
            logger.info(f"模型 {name} 的 MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")

        # 保存 CatBoost
        best_model = models["CatBoost"]
        with open(MODEL_DIR / "salary_model.pkl", "wb") as f:
            pickle.dump(best_model, f)
            logger.info("CatBoost 模型已保存")

        # 保存元数据
        salary_meta = {
            "feature_cols": feature_cols,
            "exp_numeric": exp_map,
            "edu_numeric": edu_map,
            "data_count": len(results),
            "r2": round(r2, 4),
            "mae": round(mae, 2),
            "feature_importance":[
                {"name": col, "weight": round(imp * 100, 1)}
                for col, imp in zip(feature_cols, best_model.   # 按顺序把多个序列的元素两两配对打包，生成一组元组
                feature_importances_)
            ], 
            "model_used": best_model.__class__.__name__,
        }
        with open(MODEL_DIR / "salary_predict_meta.pkl", "wb") as f:
            pickle.dump(salary_meta, f)
            logger.info("已保存薪资预测模型元数据（特征列、映射表、R2、MAE、特征重要性权重）")
        
        # 保存特征列名和编码器（推理用）
        with open(MODEL_DIR / "feature_cols.pkl", "wb") as f:
            pickle.dump(feature_cols, f)
            logger.info("特征列名已保存")
        with open(MODEL_DIR / "salary_predict_encoder.pkl", "wb") as f:
            pickle.dump(encoders, f)
            logger.info("薪资预测编码器已保存")

        



