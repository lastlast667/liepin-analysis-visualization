# 分类器封装（加载 .pkl、predict）

from functools import lru_cache
import pickle

import pandas as pd

from apps.analysis.tokenizer import tokenize_dataframe

from job_analysis.app_config import MODEL_DIR

@lru_cache(maxsize=1)  # 缓存结果，只加载一次模型
def _load_assets():
    """
    懒加载所有模型资产，只加载一次
    """
    with open(MODEL_DIR / "tfidf_vectorizer.pkl", "rb") as f:   # 加载TF-IDF向量化器
        vectorizer = pickle.load(f)
    with open(MODEL_DIR / "label_encoder.pkl", "rb") as f:      # 加载标签编码器
        encoder = pickle.load(f)
    with open(MODEL_DIR / "best_model.pkl", "rb") as f:         # 加载最佳模型
        model = pickle.load(f)
    return vectorizer, encoder, model

def predict_category(text: str):
    """
    对文本进行分类预测
    """
    vectorizer, encoder, model = _load_assets()

    # 把字符串包装成DataFrame
    df = pd.DataFrame({"job_description": [text]})

    # 对文本进行分词
    df = tokenize_dataframe(df)
    text_vec = df.iloc[0]["tokenized_words"]    # 取第一行中列"tokenized_words"的值

    # 向量化
    X = vectorizer.transform([text_vec])

    # 预测并且解码标签
    y_pred = model.predict(X)   # 一维数组 / 一维列表
    category = encoder.inverse_transform(y_pred)[0]
    
    return category
   
