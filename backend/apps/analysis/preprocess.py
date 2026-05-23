"""
数据预处理：薪资解析 + 城市标准化
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import re
import logging
from job_analysis.app_config import PROCESSED_DATA_DIR
from utils.load_words_from import load_words_from

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")   # 配置日志记录
logger = logging.getLogger("preprocess")     # 获取日志记录器，用于记录预处理过程中的信息和错误


@load_words_from("city_province.txt")
def load_city_province_map(words: list[str]) -> dict[str, str]:
    """
    加载城市-省份映射词表，返回城市-省份映射字典。
    :param words: 城市-省份映射词表内容，每个元素为一个城市-省份对
    :return: 城市-省份映射字典
    """
    city_province = {}
    for line in words:
        if "," in line:
            city, province = line.split(",", 1)
            city_province[city.strip()] = province.strip()
    return city_province


def parse_salary(salary_str: str) -> tuple:
    """解析薪资字段，返回 (salary_min, salary_max, month_min, month_max)，单位：元。

    支持格式：
      - "15-30k"           → (15000, 30000)
      - "20-40k·14薪"      → (23333, 46667)
      - "薪资面议"          → (None, None)
      - "150元/天"         → (3263, 3263)      日薪 * 21.75 折算月薪
      - "100-150元/天"     → (2175, 3263)
      - 无法识别            → (None, None) 并记录日志
    """


    salary_str = salary_str.strip()

    # 薪资面议
    if "面议" in salary_str:
        return None, None, None

    # 日薪格式：X元/天 或 X-Y元/天
    daily_match = re.match(r"(\d+)(?:-(\d+))?元/天", salary_str)
    if daily_match:
        min_val = int(daily_match.group(1))
        max_val = int(daily_match.group(2)) if daily_match.group(2) else min_val
        month_min = round(min_val * 21.75)
        month_max = round(max_val * 21.75)
        month_avg = round((month_min + month_max) / 2)
        return month_min, month_max, month_avg

    # 月薪格式：X-Yk 或 X-Yk·N薪
    monthly_match = re.match(r"(\d+)-(\d+)k(?:·(\d+)薪)?", salary_str)
    if monthly_match:
        min_val = int(monthly_match.group(1)) * 1000
        max_val = int(monthly_match.group(2)) * 1000
        months = monthly_match.group(3)
        if months:
            months = int(months)
            min_val = round(min_val * months / 12)
            max_val = round(max_val * months / 12)
        avg_val = round((min_val + max_val) / 2)
        return min_val, max_val, avg_val

    logger.warning(f"无法识别的薪资格式: {salary_str}")
    return None, None, None


def standardize_city(location: str) -> str:
    """标准化城市名。

    规则：
      - 无"-"则直接返回
      - 有"-"则提取"-"前的字符串
    """
    if not isinstance(location, str) or not location.strip():
        return ""
    location = location.strip()
    if "-" in location:
        return location.split("-")[0].strip()
    return location


def parse_recruit_count(recruit_count_raw: str) -> int | None:
    """解析招聘人数字符串，返回整数值。

    支持格式：
      - "10人" → 10
      - "20人" → 20
      - "" → None
    """
    if not isinstance(recruit_count_raw, str) or not recruit_count_raw.strip():
        return None
    num = re.findall(r'\d+', recruit_count_raw.strip())
    return int(num[0]) if num else None


def parse_language_requirement(requirement: str) -> bool:
    """解析语言要求字符串，返回是否包含外文。

    支持格式：
      - "英语" → True
      - "日语" → True
      - "韩语" → True
      - "法语" → True
      - "德语" → True
      - "俄语" → True
      - "西班牙语" → True
      - "" → False
    """
    if not isinstance(requirement, str) or not requirement.strip():
        return False
    foreign_languages = {"英语", "日语", "韩语", "法语", "德语", "俄语", "西班牙语"}
    return any(lang in requirement for lang in foreign_languages)


def parse_work_time(work_time: str) -> bool:
    """解析工作时间字符串，返回是否为周末双休。

    支持格式：
      - "周末双休" → True
      - "" → False
    """
    if not isinstance(work_time, str) or not work_time.strip():
        return False
    return "周末双休" in work_time.strip()

def parse_experience(experience: str) -> int | None:
    """解析工作经验字符串，返回整数值。

    支持格式：
      - "1-3年" → 1
      - "3-5年" → 4
      - "5-7年" → 6
      - "7-9年" → 8
      - "9-11年" → 10
      - "11-13年" → 12
      - ""13年以上" → 14
      - "" → None
    """

    if not isinstance(experience, str) or not experience.strip():
        return None
    num = re.findall(r'\d+', experience.strip())
    return int(num[0]) if num else None


def handle_company_scale(scale_value: str) -> str:
    """处理公司规模字段的占位函数，当前原值返回。
    后续可在此函数中补充公司规模的标准化逻辑。
    """
    return scale_value


def parse_company_scale(scale_str: str) -> tuple:
    """解析公司规模字符串，返回 (scale_min, scale_max) 整数值。

    支持格式：
      - "1000-2000人" → (1000, 2000)
      - "10000人以上" → (10000, 99999)
      - "1-49人"     → (1, 49)
      - ""           → (None, None)
    """
    if not isinstance(scale_str, str) or not scale_str.strip():
        return None, None

    scale_str = scale_str.strip()

    range_match = re.match(r"(\d+)-(\d+)人", scale_str)
    if range_match:
        return int(range_match.group(1)), int(range_match.group(2))

    above_match = re.match(r"(\d+)人以上", scale_str)
    if above_match:
        return int(above_match.group(1)), 99999

    return None, None


def supplement_company_info(df: pd.DataFrame) -> pd.DataFrame:
    """补充公司信息：
    - 当 company_link 为空时，将 industry_requirement 赋值给 company_industry
    - company_scale 调用占位函数处理
    """
    df = df.copy()

    no_link_mask = df["company_link"].isna() | (df["company_link"] == "")

    for idx in df[no_link_mask].index:
        if pd.isna(df.loc[idx, "company_industry"]) or df.loc[idx, "company_industry"] == "":
            industry_val = df.loc[idx, "industry_requirement"]
            if isinstance(industry_val, str) and industry_val.strip():
                industry_val = industry_val.split(",")[0].strip()   # 提取第一个行业
                df.loc[idx, "company_industry"] = industry_val

    df["company_scale"] = df["company_scale"].apply(handle_company_scale)

    return df


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    original_count = len(df)
    logger.info(f"原始数据量: {original_count} 条")

    salary_results = df["salary"].apply(parse_salary)
    df["month_salary_min"] = salary_results.apply(lambda x: x[0])
    df["month_salary_max"] = salary_results.apply(lambda x: x[1])
    df["month_salary_avg"] = salary_results.apply(lambda x: x[2])

    parsed = df["month_salary_min"].notna().sum()
    logger.info(f"薪资解析完成: {parsed}/{original_count} 条成功")

    df["location_city"] = df["location"].apply(standardize_city)
    logger.info(f"城市标准化完成")

    CITY_PROVINCE_MAP = load_city_province_map()
    logger.info(f"已加载城市-省份映射: {len(CITY_PROVINCE_MAP)} 个城市")

    df["location_province"] = df["location_city"].map(CITY_PROVINCE_MAP).fillna("")
    province_count = (df["location_province"] != "").sum()
    logger.info(f"省份映射完成，已识别 {province_count}/{original_count} 条")

    before = (df["company_industry"] != "").sum()
    df = supplement_company_info(df)
    after = (df["company_industry"] != "").sum()
    filled = after - before
    if filled > 0:
        logger.info(f"公司行业补充完成，通过 industry_requirement 补充了 {filled} 条数据")
    else:
        logger.info(f"公司行业补充完成，无需额外补充")

    scale_results = df["company_scale"].apply(parse_company_scale)
    df["company_scale_min"] = scale_results.apply(lambda x: x[0])
    df["company_scale_max"] = scale_results.apply(lambda x: x[1])
    scale_parsed = df["company_scale_min"].notna().sum()
    logger.info(f"公司规模解析完成: {scale_parsed}/{original_count} 条成功")

    df["recruit_count_parsed"] = df["recruit_count"].apply(parse_recruit_count)
    rc_parsed = df["recruit_count_parsed"].notna().sum()
    logger.info(f"招聘人数解析完成: {rc_parsed}/{original_count} 条成功")

    df["has_language_requirement"] = df["language_requirement"].apply(parse_language_requirement)
    lang_count = df["has_language_requirement"].sum()
    logger.info(f"语言要求解析完成: {int(lang_count)} 条有外语要求")

    df["has_weekend_off"] = df["work_time"].apply(parse_work_time)
    weekend_count = df["has_weekend_off"].sum()
    logger.info(f"工作时间解析完成: {int(weekend_count)} 条周末双休")

    logger.info(f"月薪范围: {df['month_salary_min'].min():,} ~ {df['month_salary_max'].max():,} 元/月")
    return df


def preprocess(data_path: str | Path) -> pd.DataFrame:
    """
    对清洗后的数据进行预处理，包括解析薪资、标准化城市、映射省份等
    :param data_path: 清洗后的数据文件路径
    :return: 预处理后的DataFrame
    """
    try:
        logger.info(f"读取清洗后数据: {data_path}")
        df = pd.read_csv(data_path)
        return preprocess_dataframe(df)
    except Exception as e:
        logger.error(f"数据预处理过程中出错: {e}")
        return None


def main():
    """
    主函数，用于预处理数据
    """
    cleaned_path = PROCESSED_DATA_DIR / "cleaned.csv"
    logger.info(f"读取清洗后数据: {cleaned_path}")
    df = preprocess(cleaned_path)
    preprocessed_path = PROCESSED_DATA_DIR / "preprocessed.csv"
    df.to_csv(preprocessed_path, index=False)
    logger.info(f"预处理结果已保存至: {preprocessed_path}")

if __name__ == "__main__":
    main()
