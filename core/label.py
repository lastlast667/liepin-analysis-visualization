"""
数据标注：三层证据融合标注
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import logging
from config.settings import PROCESSED_DATA_DIR, INTERMEDIATE_DATA_DIR

KEYWORDS = [
    "Java开发", "Python开发", "Go开发", "C++开发", "PHP开发",
    "爬虫工程师", "嵌入式开发", "前端", "数据分析师", "大数据开发",
    "算法", "软件测试", "运维", "全栈",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("label")

CATEGORY_KEYWORDS_DESC = {
    "前端": ["前端", "Vue", "React"],
    "数据分析师": ["数据分析师", "数据挖掘", "数据可视化", "数据仓库"],
    "大数据开发": ["大数据开发", "Hadoop", "Spark", "Hive", "Pig", "Kafka", "HBase", "Cassandra"],
    "算法": ["算法", "机器学习", "深度学习", "自然语言处理", "图像识别", "语音识别"],
    "全栈": ["全栈"],
    "爬虫工程师":   ["爬虫", "Scrapy", "反爬", "数据采集", "Selenium", "数据抓取",
               "JS逆向", "App逆向", "代理"],
    "嵌入式开发": ["嵌入式", "单片机", "ARM", "Linux驱动", "驱动开发", "RTOS", "DSP",
               "FPGA", "Linux内核", "BSP", "uboot", "I2C", "SPI", "CAN"],
    "软件测试":   ["测试", "测试用例", "自动化测试", "功能测试", "性能测试",
               "Selenium", "JUnit", "TestNG", "接口测试", "压力测试",
               "单元测试", "质量保证", "QA"],
    "运维":   ["运维", "DevOps", "Kubernetes", "Docker", "CI/CD", "Jenkins",
               "监控", "部署", "容器化", "K8s", "Ansible", "Prometheus", "SRE"],
    "Go开发":     ["Golang", "Go语言", "Go开发", "微服务", "并发", "golang", "Gin"],
    "PHP开发":    ["PHP", "Laravel", "ThinkPHP", "MySQL", "Redis", "Swoole", "Hyperf"],
    "Python开发": ["Python", "Django", "Flask", "TensorFlow", "PyTorch", "机器学习",
               "深度学习", "数据分析", "Pandas", "NumPy", "数据挖掘", "NLP", "自然语言处理"],
    "Java开发":   ["Java", "Spring", "Spring Boot", "Spring Cloud", "MyBatis", "JVM",
               "Hibernate", "Maven", "微服务", "Dubbo", "Netty", "Tomcat"],
    "C++开发":    ["C++", "C/C++", "Qt", "MFC", "多线程", "内存管理", "STL", "Boost",
               "Windows驱动", "Linux驱动", "串口"],
}

# title 匹配关键词（核心词 + 特征词）
# 用于解决 key 为 "C++开发" 但 title 是 "C++工程师" 等无法精确子串匹配的问题
CATEGORY_KEYWORDS_TITLE = {
    "Java开发":   ["java", "spring", "mybatis", "jvm", "maven", "dubbo", "netty", "hibernate"],
    "Python开发": ["python", "django", "flask", "tensorflow", "pytorch", "pandas", "numpy"],
    "Go开发":     ["Go", "golang", "go语言", "gin", "grpc", "go开发", "go工程师", "go后端", "go服务端"],
    "C++开发":    ["c++", "c/c++", "qt", "mfc", "stl", "boost", "多线程", "内存管理"],
    "PHP开发":    ["php", "laravel", "thinkphp", "swoole", "hyperf"],
    "爬虫工程师": ["爬虫", "scrapy", "反爬", "数据采集", "数据抓取", "js逆向", "app逆向"],
    "嵌入式开发": ["嵌入式", "单片机", "arm", "dsp", "fpga", "bsp", "rtos", "驱动开发", "linux驱动"],
    "前端":       ["前端", "vue", "react", "angular", "web前端", "h5", "javascript", "typescript"],
    "数据分析师": ["数据分析", "数据分析师", "数据挖掘", "数据可视化", "数据仓库"],
    "大数据开发": ["大数据", "hadoop", "spark", "hive", "flink", "kafka", "hbase"],
    "算法":       ["算法", "机器学习", "深度学习", "nlp", "图像识别", "语音识别", "自然语言处理"],
    "软件测试":   ["测试", "qa", "质量保证", "自动化测试", "性能测试", "接口测试", "压力测试"],
    "运维":       ["运维", "devops", "sre", "kubernetes", "docker", "k8s", "jenkins", "prometheus"],
    "全栈":       ["全栈"],
}


def label_row(key: str, title: str, job_description: str) -> str:
    """
    对单行数据进行分类标注

    标注策略：
    1. 优先根据当前key的核心词匹配title，若匹配则直接返回该key
    2. 若标题未匹配当前key，则遍历所有key的核心词匹配title，匹配到哪个key就返回哪个key
    3. 若标题中未匹配到任何key的核心词，则根据描述匹配CATEGORY_KEYWORDS_DESC中的关键词进行分类
    4. 如果描述中也没有匹配到任何关键词，将该条数据分类为"过滤"

    :param title: 职位标题
    :param job_description: 职位描述
    :return: 分类结果
    """

    try:
        # 处理title和job_description的缺失值
        if pd.isna(title):
            title = ""
        else:
            title = str(title)
        if pd.isna(job_description):
            job_description = ""
        else:
            job_description = str(job_description)

        title_lower = title.lower()
        # 第一层：根据当前key的核心词匹配title
        key_keywords = CATEGORY_KEYWORDS_TITLE.get(key, [key.lower()])
        if any(kw.lower() in title_lower for kw in key_keywords):
            return key

        # 第二层：根据所有key的核心词匹配title
        for category, keywords in CATEGORY_KEYWORDS_TITLE.items():
            if any(kw.lower() in title_lower for kw in keywords):
                return category

        desc_lower = job_description.lower()
        # 第三层：根据描述进行分类，描述中若有匹配CATEGORY_KEYWORDS_DESC的任一关键词，则根据key进行分类
        for category, keywords in CATEGORY_KEYWORDS_DESC.items():
            if any(kw.lower() in desc_lower for kw in keywords):
                return key

        # 如果描述中也没有匹配CATEGORY_KEYWORDS_DESC的关键词，将该条数据分类为"过滤"
        return "过滤"
    except Exception as e:
        logger.error(f"标注数据时出错: {e}")


def label_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    对DataFrame进行分类标注
    :param df: 输入的DataFrame
    :return: 标注后的DataFrame
    """
    df = df.copy()
    original_count = len(df)
    logger.info(f"原始数据量: {original_count} 条")

    df["category"] = df.apply(
        lambda row: label_row(row["key"], row.get("title", ""), row.get("job_description", "")),
        axis=1,
    )

    category_counts = df["category"].value_counts()
    logger.info(f"标注完成，各分类分布:")
    for category, count in category_counts.items():
        pct = count / original_count * 100
        logger.info(f"  {category}: {count} 条 ({pct:.1f}%)")

    layer1_count = (df["category"] != "过滤").sum()
    logger.info(f"第一层(title)覆盖: {layer1_count}/{original_count} 条")

    return df


def label_data(data_path: str | Path) -> pd.DataFrame:
    """
    读取预处理后的数据文件，进行分类标注
    :param data_path: 预处理后的数据文件路径
    :return: 标注后的DataFrame
    """
    logger.info(f"读取预处理后数据: {data_path}")
    df = pd.read_csv(data_path)
    return label_dataframe(df)


def main():
    """
    主函数，用于标注数据
    """
    preprocessed_path = PROCESSED_DATA_DIR / "preprocessed.csv"  # 预处理后的数据路径
    df = label_data(preprocessed_path)
    labeled_path = INTERMEDIATE_DATA_DIR / "labeled.csv"         # 标注结果保存路径
    df.to_csv(labeled_path, index=False)
    logger.info(f"标注结果已保存至: {labeled_path}")


if __name__ == "__main__":
    main()
