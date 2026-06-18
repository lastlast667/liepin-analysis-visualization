"""
薪资预测模型
"""
"""
薪资预测模型
"""
import pickle
import pandas as pd
from apps.analysis.preprocess import parse_company_scale
from job_analysis.app_config import MODEL_DIR


def _load_assets():
    """加载模型和元数据"""

    with open(MODEL_DIR / "salary_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open(MODEL_DIR / "salary_predict_meta.pkl", "rb") as f:
        salary_meta = pickle.load(f)
        feature_cols = salary_meta["feature_cols"]
        exp_map = salary_meta["exp_numeric"]
        edu_map = salary_meta["edu_numeric"]

    return model, feature_cols, exp_map, edu_map


def predict(params: dict) -> dict:
    model, feature_cols, exp_map, edu_map = _load_assets()

    row = {
        "category": params.get("category", ""),
        "location_city": params.get("location_city", ""),
        "company_industry": params.get("company_industry", ""),
        "exp_numeric": exp_map.get(params.get("experience_level", ""), 0),
        "edu_numeric": edu_map.get(params.get("education", ""), 0),
        "company_scale_min": 0,
        "company_scale_max": 0,
        "has_weekend_off": False,
    }

    # 解析 company_scale 字符串，仅单个元组而非一列series所以不用apply
    company_scale = params.get("company_scale", "")
    if company_scale:
        scale_min, scale_max = parse_company_scale(company_scale)
        row["company_scale_min"] = scale_min or 0
        row["company_scale_max"] = scale_max or 0

    # 构造输入 DataFrame，列顺序和训练时一致
    input_df = pd.DataFrame([row], columns=feature_cols)

    # 预测薪资和置信区间
    pred = model.predict(input_df)[0]   # predict() 永远返回一维数组（ndarray）
    with open(MODEL_DIR / "salary_predict_meta.pkl", "rb") as f:
        salary_meta = pickle.load(f)
    mae = salary_meta.get("mae", 0)

    return {
        "predicted_salary": round(pred, -2),
        "predicted_min": round(pred - mae, -2) if mae else round(pred * 0.8, -2),
        "predicted_max": round(pred + mae, -2) if mae else round(pred * 1.2, -2),
        "model_used": model.__class__.__name__,
        "feature_importance": salary_meta.get("feature_importance", []),
    }
