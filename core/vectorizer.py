"""
文本向量化器
TF-IDF向量化

输入：tokenized_words + category
输出：X, y, vectorizer
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import json
import pickle
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from config.settings import PROCESSED_DATA_DIR, MODEL_DIR, INTERMEDIATE_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vectorizer")


def vectorize_dataframe(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, TfidfVectorizer, LabelEncoder]:
    """
    对DataFrame进行TF-IDF向量化
    :param df: 包含 tokenized_words 和 category 列的DataFrame
    :return: TF-IDF特征矩阵 X, 类别标签向量 y, TF-IDF向量化器 vectorizer, 标签编码器 label_encoder
    """
    tokenized_list = df["tokenized_words"].tolist()
    category_list = df["category"].tolist()
    return vectorize_text(tokenized_list, category_list)


def vectorize_text(tokenized_words: list[list[str]] | list[str],category: list[str],) -> tuple[np.ndarray, np.ndarray, TfidfVectorizer, LabelEncoder]:
    """
    对文本进行TF-IDF向量化
    :param tokenized_words: 分词后的文本列表，每个元素为一个词列表或字符串
    :param category: 分类标签列表
    :return: TF-IDF特征矩阵 X, 类别标签向量 y, TF-IDF向量化器 vectorizer, 标签编码器 label_encoder
    """
    
    try:
        if isinstance(tokenized_words[0], list):
            documents = [" ".join(tokens) for tokens in tokenized_words]
        else:
            documents = list(tokenized_words)

        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(category)

        vectorizer = TfidfVectorizer(
            max_features=3000,  # 控制词汇表大小
            ngram_range=(1, 2), # 控制词组合
            min_df=2,           # 过滤低频词
            max_df=0.9          # 过滤高频词
        )
        X = vectorizer.fit_transform(documents)
        logger.info(f"TF-IDF向量化完成，共{X.shape[0]}条数据，{X.shape[1]}个特征，{len(label_encoder.classes_)}个类别")

        vectorizer_path = MODEL_DIR / "tfidf_vectorizer.pkl"
        with open(vectorizer_path, "wb") as f:
            pickle.dump(vectorizer, f)
        logger.info(f"已保存 TF-IDF向量化器 到 {vectorizer_path}")

        encoder_path = MODEL_DIR / "label_encoder.pkl"
        with open(encoder_path, "wb") as f:
            pickle.dump(label_encoder, f)
        logger.info(f"已保存 标签编码器 到 {encoder_path}")

        feature_names = vectorizer.get_feature_names_out().tolist()
        vocab_path = PROCESSED_DATA_DIR / "tfidf_vocab.json"
        with open(vocab_path, "w", encoding="utf-8") as f:
            json.dump(feature_names, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存 TF-IDF词汇表 到 {vocab_path}")

        return X, y, vectorizer, label_encoder
    except Exception as e:
        logger.error(f"向量化过程中出错: {e}")
        return None, None, None, None


def main():
    """
    主函数，读取分词后的数据，进行TF-IDF向量化，保存结果
    """
    data_path = INTERMEDIATE_DATA_DIR / "tokenized.csv"
    logger.info(f"读取分词后的数据: {data_path}")
    df = pd.read_csv(data_path)

    X, y, vectorizer, label_encoder = vectorize_dataframe(df)

    X_path = PROCESSED_DATA_DIR / "tfidf_X.npy"             # 保存 TF-IDF 特征矩阵
    y_path = PROCESSED_DATA_DIR / "labels_y.npy"            # 保存 数值编码后的标签数组
    vectorizer_path = MODEL_DIR / "tfidf_vectorizer.pkl"    # 保存 TF-IDF 向量化器
    encoder_path = MODEL_DIR / "label_encoder.pkl"          # 保存 标签编码器
    np.save(X_path, X.toarray())
    np.save(y_path, y)
    logger.info(f"已保存 X ({X.shape}) 到 {X_path}")
    logger.info(f"已保存 y ({y.shape}) 到 {y_path}")
    logger.info(f"已保存 vectorizer 到 {vectorizer_path}")
    logger.info(f"已保存 label_encoder 到 {encoder_path}")

    classes = label_encoder.classes_
    logger.info(f"类别映射: {dict(zip(range(len(classes)), classes))}")


if __name__ == "__main__":
    main()