"""
导入岗位数据 tokenized.csv 到数据库 Job 表

用法：python manage.py import_jobs 
"""

import logging
import ast
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from pathlib import Path
import csv
from apps.jobs.models import Job



logger = logging.getLogger("import_jobs")

CSV_FIELD_MAP = [
    "key", "job_url", "title", "salary", "location",
    "experience", "education", "recruit_count", "update_time",
    "company_name", "company_link", "job_description",
    "language_requirement", "industry_requirement", "work_time",
    "company_tags", "crawl_time",
    "company_industry", "company_scale_min", "company_scale_max",
    "month_salary_min", "month_salary_max", "month_salary_avg",
    "location_city", "location_province", "location_partition", "category", "tokenized_words",
]

def parse_company_tags(raw: str):
    """
    解析公司标签字符串为列表
    """
    if not raw or raw.strip() == "[]":
        return []   # 空字符串或空列表字符串返回空列表
    try:
        return ast.literal_eval(raw)    # 安全解析为列表
    except (ValueError, SyntaxError):
        logger.error(f"无法解析公司标签字符串: {raw}")
        return []  # 解析失败时返回空列表

def parse_crawl_time(raw: str):
    """
    解析爬取时间字符串为 datetime 对象
    """
    if not raw or raw.strip() == "":
        return None   # 空字符串或空值返回 None
    try:
        return datetime.strptime(raw.strip(), "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        logger.error(f"无法解析爬取时间字符串: {raw}")
        return None  # 解析失败时返回 None
    

    
class Command(BaseCommand):
    help = "导入岗位数据 tokenized.csv 到数据库 Job 表"

    def add_arguments(self, parser):
        """
        添加命令行参数
        """
        parser.add_argument(
            "--csv", 
            type=str, 
            default="None",
            help="CSV 文件路径，默认使用 data/intermediate/tokenized.csv",
            )
    
    def _parse_float(self, val):
        """
        解析字符串为浮点数，返回 None 如果解析失败
        """
        if not val or val.strip() == "":
            return None   # 空字符串或空值返回 None
        try:
            return float(val.strip())
        except ValueError:
            logger.error(f"无法解析浮点数: {val}")
            return None  # 解析失败时返回 None

    def _parse_int(self, val):
        if not val or val.strip() == "":
            return None
        try:
            return int(float(val.strip()))
        except (ValueError, TypeError):
            logger.error(f"无法解析整数: {val}")
            return None

    def _parse_bool(self, val):
        if not val or val.strip() == "":
            return False
        return val.strip().lower() in ("true", "1", "yes")
        
    def handle(self, *args, **options):
        """
        处理命令逻辑
        """
        csv_path = options["csv"]
        if csv_path == "None":
            csv_path = str(Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "data" / "intermediate" / "tokenized.csv")
        
        csv_path = Path(csv_path)
        if not csv_path.exists():
            logger.error(f"文件 {csv_path} 不存在")
            return
        
        total = 0
        errors = 0
        batch = []
        
        logger.info(f"开始导入 {csv_path}")

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)  # 读取 CSV 文件，返回字典列表
            for row_num, row in enumerate(reader, start=2):  # 跳过标题行
                try:
                    job = Job(
                        key=row.get("key", ""),
                        job_url=row.get("job_url", ""),
                        title=row.get("title", ""),
                        salary=row.get("salary", ""),
                        location=row.get("location", ""),
                        experience=row.get("experience", ""),
                        education=row.get("education", ""),
                        recruit_count=row.get("recruit_count", ""),
                        update_time=row.get("update_time", ""),
                        company_name=row.get("company_name", ""),
                        company_link=row.get("company_link", ""),
                        company_industry=row.get("company_industry", ""),
                        company_scale=row.get("company_scale", ""),
                        company_scale_min=self._parse_int(row.get("company_scale_min")),
                        company_scale_max=self._parse_int(row.get("company_scale_max")),
                        job_description=row.get("job_description", ""),
                        language_requirement=row.get("language_requirement", ""),
                        industry_requirement=row.get("industry_requirement", ""),
                        work_time=row.get("work_time", ""),
                        company_tags=parse_company_tags(row.get("company_tags", "")),
                        crawl_time=parse_crawl_time(row.get("crawl_time", "")),
                        month_salary_min=self._parse_float(row.get("month_salary_min")),
                        month_salary_max=self._parse_float(row.get("month_salary_max")),
                        month_salary_avg=self._parse_float(row.get("month_salary_avg")),
                        location_city=row.get("location_city", ""),
                        location_province=row.get("location_province", ""),
                        location_partition=row.get("location_partition", ""),
                        category=row.get("category", ""),
                        tokenized_words=row.get("tokenized_words", ""),
                        recruit_count_parsed=self._parse_int(row.get("recruit_count_parsed")),
                        has_language_requirement=self._parse_bool(row.get("has_language_requirement")),
                        has_weekend_off=self._parse_bool(row.get("has_weekend_off")),
                    )
                    batch.append(job)
                    total += 1

                    if len(batch) >= 500:
                        Job.objects.bulk_create(batch, ignore_conflicts=True)   # 批量创建岗位，忽略冲突（key 重复）
                        logger.info(f"已导入 {total} 条岗位")
                        batch.clear()
            
                except Exception as e:
                    errors += 1
                    logger.error(f"导入第 {row_num} 行数据时出错: {e}")
        
            if batch:
                Job.objects.bulk_create(batch, ignore_conflicts=True)   # 批量创建岗位，忽略冲突（key 重复）
                logger.info(f"已导入 {total} 条岗位")
                batch.clear()

        logger.info(f"导入完成，共导入 {total} 条岗位，共 {errors} 条错误")
        logger.info(f"导入时间: {datetime.now()}")



