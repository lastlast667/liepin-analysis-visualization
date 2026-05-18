"""
文本分词器

jieba分词 + 停用词过滤
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import jieba
import pandas as pd
from job_analysis.app_config import DATA_DIR, MODEL_DIR, INTERMEDIATE_DATA_DIR
from utils.load_words_from import load_words_from


@load_words_from("stopwords.txt")
def load_stopwords(stopwords: list[str]) -> list[str]:
    """
    加载停用词表
    """
    return stopwords


@load_words_from("customwords.txt")
def load_customwords(customwords: list[str]) -> list[str]:
    """
    加载自定义词表
    """
    return customwords


def tokenize(text: str, stopwords: set[str]) -> list[str]:
    """
    对单条文本进行分词，并过滤停用词
    """
    words = jieba.lcut(text)
    return [w for w in words if w.strip() and w not in stopwords]


def tokenize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    对 DataFrame 中的 title 和 job_description 进行分词，生成 tokenized_words 列

    :param df: 包含 title 和 job_description 列的 DataFrame
    :return: 新增 tokenized_words 列的 DataFrame
    """
    stopwords = set(load_stopwords())
    customwords = load_customwords()

    for word in customwords:
        jieba.add_word(word)

    df = df.copy()
    print(f"已加载停用词 {len(stopwords)} 个，自定义词 {len(customwords)} 个")
    print(f"读取数据: {len(df)} 条")

    tokenized_list = []
    for _, row in df.iterrows():
        # 处理 title 和 job_description 列缺失值，避免 KeyErrors，合并为一个字符串
        title = str(row.get("title", "")) if pd.notna(row.get("title")) else ""
        job_description = str(row.get("job_description", "")) if pd.notna(row.get("job_description")) else ""
        combined_text = title + " " + job_description
        # 对合并后的文本进行分词
        tokens = tokenize(combined_text, stopwords)
        tokenized_list.append(" ".join(tokens))

    df["tokenized_words"] = tokenized_list
    return df


def tokenize_data(data_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(data_path)
    return tokenize_dataframe(df)


def main():
    """
    主函数，执行分词处理
    """
    labeled_path = INTERMEDIATE_DATA_DIR / "labeled.csv"
    df = tokenize_data(labeled_path)
    output_path = INTERMEDIATE_DATA_DIR / "tokenized.csv"
    df.to_csv(output_path, index=False)
    print(f"已保存分词结果到: {output_path}")


if __name__ == "__main__":
    main()