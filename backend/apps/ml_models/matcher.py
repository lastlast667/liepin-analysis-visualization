# 匹配引擎（加载全量数据、余弦相似度）
"""
匹配引擎（加载全量数据、余弦相似度）
"""
import pickle
import pandas as pd
from functools import lru_cache
from sklearn.metrics.pairwise import cosine_similarity

from apps.jobs.models import Job
from job_analysis.app_config import MODEL_DIR
from apps.ml_models.classifier import predict_category
from apps.analysis.tokenizer import tokenize, load_stopwords, load_customwords
import jieba

@lru_cache(maxsize=1)  # 缓存结果，只加载一次模型
def _load_vectorizer():
    """
    加载训练好的 TF-IDF 向量化器
    """
    with open(MODEL_DIR / "tfidf_vectorizer.pkl", "rb") as f:   # 加载TF-IDF向量化器
        vectorizer = pickle.load(f)
    return vectorizer
    
@lru_cache(maxsize=1)  # 缓存结果
def _load_all_jobs():
    """
    从数据库加载全量岗位数据到 DataFrame
    """
    df = Job.objects.exclude(tokenized_words__in=["", None]).values()
    df = pd.DataFrame(df)
    return df

def _filter_by_salary(category_pool:pd.DataFrame, salary_range:str) -> pd.DataFrame:
    """按薪资区间过滤，只保留有重叠的岗位"""
    if salary_range and salary_range != "不限":
        # 此时 category_pool 是 DataFrame，不是 QuerySet。DataFrame 不能用 filter(字段__gte=xxx) 这种 Django ORM 语法，要用 pandas 的方式过滤
        if salary_range == "10k以内":
            category_pool = category_pool[category_pool["month_salary_avg"] < 10000]  # 小于10k
        elif salary_range == "10-20k":
            category_pool = category_pool[(category_pool["month_salary_avg"] >= 10000) & (category_pool["month_salary_avg"] < 20000)]  # 大于等于10k，小于20k
        elif salary_range == "20-30k":
            category_pool = category_pool[(category_pool["month_salary_avg"] >= 20000) & (category_pool["month_salary_avg"] < 30000)]  # 大于等于20k，小于30k
        elif salary_range == "30-50k":
            category_pool = category_pool[(category_pool["month_salary_avg"] >= 30000) & (category_pool["month_salary_avg"] < 50000)]  # 大于等于30k，小于50k
        elif salary_range == "50k以上":
            category_pool = category_pool[category_pool["month_salary_avg"] >= 50000]  # 大于等于50k
        elif salary_range == "薪资面议":
            category_pool = category_pool[category_pool["month_salary_avg"].isnull()]  # 空值表示薪资面议
    return category_pool

def _filter_by_company_scale(category_pool:pd.DataFrame, company_scales:list) -> pd.DataFrame:
    """按公司规模过滤，只保留有重叠的岗位"""
    if company_scales:
        category_pool = category_pool[category_pool["company_scale"].isin(company_scales)]
    return category_pool

def _filter_by_company_industry(category_pool:pd.DataFrame, company_industries:list) -> pd.DataFrame:
    """按公司行业过滤，只保留有重叠的岗位"""
    if company_industries:
        category_pool = category_pool[category_pool["company_industry"].isin(company_industries)]
    return category_pool

def _filter_by_has_weekend_off(category_pool:pd.DataFrame, has_weekend_off:bool) -> pd.DataFrame:
    """按是否双休过滤，只保留有重叠的岗位"""
    if has_weekend_off is not None:
        category_pool = category_pool[category_pool["has_weekend_off"] == has_weekend_off]
    return category_pool

def _handle_remote_cities(category_pool:pd.DataFrame, cities:list, top_k:int) -> pd.DataFrame:
    """
    城市处理逻辑：
    - 选了城市：优先返回选中城市岗位，不够时从其他城市补（标异地）
    - 没选城市（不限）：全部不标异地
    """
    if not cities:
        # 不选城市：全部不标异地
        category_pool["is_remote"] = False
        return category_pool
    
    # 打标异地
    category_pool["is_remote"] = ~category_pool["location_city"].isin(cities)

    # 排序：本地优先（is_remote=False 排前面），相同优先级内按 match_score 降序，取前 tap_k 个
    category_pool.sort_values(
        by=["is_remote", "match_score"], 
        ascending=[True, False], 
        inplace=True
        )
    category_pool = category_pool.head(top_k)
    
    return category_pool

def match(resume_text: str, filters: dict):
    """
    简历匹配主流程

    :param resume_text: 简历文本
    :param filters: 筛选条件字典
        {
            "cities": ["北京", "上海"],              # 期望城市范围
            "salary_range": "10k-20k",              # 期望薪资范围
            "company_scales": ["100-499人"],        # 公司规模偏好
            "company_industries": ["IT", "金融"],   # 公司行业偏好
            "has_weekend_off": True,                # 是否双休
            "top_k": 20                             # 筛选结果数量
        }
    :return: 包含匹配结果的字典
    """

    # 加载数据
    vectorizer = _load_vectorizer()
    all_jobs = _load_all_jobs()

    # 预测简历类别
    resume_category = predict_category(resume_text)
    # print(f"[DEBUG] 预测的类别: {repr(resume_category)}")

    # 所有类别看一遍
    # print(f"[DEBUG] 数据库中的类别列表: {all_jobs['category'].unique()}")

    # 对简历文本分词后用于向量化
    stopwords = set(load_stopwords())
    for w in load_customwords():
        jieba.add_word(w)
    tokens = tokenize(resume_text, stopwords)
    tokenized_text = " ".join(tokens)

    # 筛选类别池
    category_pool = all_jobs[all_jobs["category"] == resume_category].copy()
    # print(f"[DEBUG] 类别池大小: {len(category_pool)}")
    if category_pool.empty:
        # print(f"[DEBUG] 类别池为空！数据总量: {len(all_jobs)}")
        return []

    # 简历向量化 + 计算余弦相似度
    resume_vec = vectorizer.transform([tokenized_text])
    category_vectors = vectorizer.transform(category_pool["tokenized_words"].tolist())
    # print(f"[DEBUG] resume_vec shape: {resume_vec.shape}")
    # print(f"[DEBUG] category_vectors shape: {category_vectors.shape}")
    similarities = cosine_similarity(resume_vec, category_vectors)[0]
    # print(f"[DEBUG] similarities length: {len(similarities)}")
    # print(f"[DEBUG] similarities[:3]: {similarities[:3]}")
    category_pool["match_score"] = similarities
    category_pool = category_pool.sort_values(by="match_score", ascending=False)
    # print(f"[DEBUG] 排序后最高分: {category_pool['match_score'].iloc[0]}")
    # print(f"[DEBUG] 排序后最低分: {category_pool['match_score'].iloc[-1]}")
    
    # 应用筛选条件 + 排序
    cities = filters.get("cities", [])
    salary_range = filters.get("salary_range", None)
    company_scales = filters.get("company_scales", [])
    company_industries = filters.get("company_industries", [])
    has_weekend_off = filters.get("has_weekend_off", False)
    top_k = filters.get("top_k", 20)

    # 薪资区间
    category_pool = _filter_by_salary(category_pool, salary_range)
        
    # 公司规模
    category_pool = _filter_by_company_scale(category_pool, company_scales)
    
    # 公司行业
    category_pool = _filter_by_company_industry(category_pool, company_industries)
    
    # 是否双休
    category_pool = _filter_by_has_weekend_off(category_pool, has_weekend_off)
    
    # 城市处理
    category_pool = _handle_remote_cities(category_pool, cities, top_k)
    return _format_results(category_pool)
def _format_results(category_pool: pd.DataFrame) -> list[dict]:
    """
    格式化匹配结果，返回字典列表
    """
    records = category_pool.to_dict(orient="records")
    for r in records:
        # 把每个字段检查一遍，所有 NaN / None / inf 都转成 null，否则 JSON 序列化会报错 ValueError: Out of range float values are not JSON compliant
        for k, v in r.items():
            if v is None or (isinstance(v, float) and (v != v or abs(v) == float("inf"))):
                r[k] = None
        # match_score 转成整数百分比
        if r["match_score"] is not None:
            r["match_score"] = round(r["match_score"] * 100)
        else:
            r["match_score"] = 0
    return records
    
    