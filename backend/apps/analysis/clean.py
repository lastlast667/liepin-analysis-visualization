"""
数据清洗
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from job_analysis.app_config import RAW_DATA_DIR, PROCESSED_DATA_DIR
import re

def clean_text(text: str) -> str:
    """
    对单条文本进行清洗，包括移除换行符、制表符、回车符等，以及合并多个空格
    :param text: 输入文本
    :return: 清洗后的文本
    """
    if pd.isna(text):
        return ""
    text = re.sub(r'[\n\t\r]+', ' ', str(text))
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_work_time(text: str) -> str:
    """
    对单条工作时间文本进行清洗，包括移除“·”符号
    :param text: 输入工作时间文本
    :return: 清洗后的工作时间文本
    """
    if pd.isna(text) or not isinstance(text, str):
        return ""
    text = text.strip().rstrip("·").strip()
    return text


def read_raw_data() -> pd.DataFrame:
    """
    读取原始数据文件，合并为一个DataFrame
    :return: 合并后的DataFrame
    """
    all_data = []
    json_files = list(RAW_DATA_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"在{RAW_DATA_DIR}中未找到JSON文件，请检查是否已下载JSON文件")

    for file in json_files:
        df = pd.read_json(file, encoding="utf-8")
        if df.empty:
            print(f"文件{file}为空，跳过")
            continue
        all_data.append(df)
        print(f"已读取: {file.name} ({len(df)} 条)")

    if not all_data:
        raise ValueError("未找到有效数据，无法合并JSON文件")

    raw_df = pd.concat(all_data, ignore_index=True)
    print(f"成功合并 {len(all_data)} 个JSON文件，共 {len(raw_df)} 条数据")
    return raw_df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    对DataFrame进行清洗，包括去重、清洗特殊字符、转换数据类型等
    :param df: 输入�洗的DataFrame
    :return: 清洗后的DataFrame
    """
    df = df.copy()
    df.drop_duplicates(subset=["job_url"], inplace=True)
    print(f"去重后，剩余{len(df)}条数据")

    text_cols = df.select_dtypes(include=["string", "object"]).columns
    for col in text_cols:
        is_all_string = df[col].apply(lambda x: isinstance(x, str)).all()
        if not is_all_string:
            print(f"列 {col} 包含非字符串类型数据，跳过清洗特殊字符")
            continue
        df[col] = df[col].apply(clean_text)

    df["work_time"] = df["work_time"].apply(clean_work_time)
    return df


def main():
    """
    主函数，用于清洗数据
    """
    try:
        raw_df = read_raw_data()
        cleaned_df = clean_dataframe(raw_df)
        cleaned_path = PROCESSED_DATA_DIR / "cleaned.csv"
        cleaned_df.to_csv(cleaned_path, index=False)
        print(f"已保存清洗后的数据到: {cleaned_path}")
    except Exception as e:
        print(f"数据清洗过程中出错: {e}")

if __name__ == "__main__":
    main()
