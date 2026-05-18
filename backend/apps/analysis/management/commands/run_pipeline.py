"""
主函数，执行整个分析管道
支持 --resume 从任意 checkpoint 恢复

用法: python manage.py run_pipeline [--resume <step>]
"""

import time
import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import pandas as pd
import numpy as np

from job_analysis.app_config import RAW_DATA_DIR, PROCESSED_DATA_DIR, INTERMEDIATE_DATA_DIR, MODEL_DIR
from apps.analysis import clean
from apps.analysis import preprocess
from apps.analysis import label
from apps.analysis import tokenizer
from apps.analysis import vectorizer

logger = logging.getLogger("pipeline")

STEP_NAMES = ["raw", "clean", "preprocess", "label", "filter", "tokenize", "vectorize"]
CHECKPOINT_DIR = INTERMEDIATE_DATA_DIR


def checkpoint_path(step: str) -> Path:
    mapping = {
        "clean": PROCESSED_DATA_DIR / "cleaned.csv",
        "preprocess": PROCESSED_DATA_DIR / "preprocessed.csv",
        "label": INTERMEDIATE_DATA_DIR / "labeled.csv",
        "filter": INTERMEDIATE_DATA_DIR / "filtered.csv",
        "tokenize": INTERMEDIATE_DATA_DIR / "tokenized.csv",
    }
    return mapping.get(step)


def run_step(step_name: str, df: pd.DataFrame | None) -> pd.DataFrame | None:
    logger.info(f"{'='*60}")
    logger.info(f"开始步骤: {step_name}")
    logger.info(f"{'='*60}")
    start_time = time.time()

    try:
        if step_name == "raw":
            df = clean.read_raw_data()
            logger.info(f"读取完成: {len(df)} 条原始数据")

        elif step_name == "clean":
            df = clean.clean_dataframe(df)
            ckpt = checkpoint_path("clean")
            df.to_csv(ckpt, index=False)
            logger.info(f"数据清洗完成: {len(df)} 条 | 已保存到 {ckpt}")

        elif step_name == "preprocess":
            df = preprocess.preprocess_dataframe(df)
            ckpt = checkpoint_path("preprocess")
            df.to_csv(ckpt, index=False)
            logger.info(f"预处理完成: {len(df)} 条 | 已保存到 {ckpt}")

        elif step_name == "label":
            df = label.label_dataframe(df)
            ckpt = checkpoint_path("label")
            df.to_csv(ckpt, index=False)
            logger.info(f"标注完成: {len(df)} 条 | 已保存到 {ckpt}")

        elif step_name == "filter":
            before = len(df)
            df = df[df["category"] != "过滤"].copy()
            after = len(df)
            logger.info(f"过滤完成: {before} -> {after} 条 (移除 {before - after} 条过滤数据)")
            ckpt = checkpoint_path("filter")
            df.to_csv(ckpt, index=False)
            logger.info(f"已保存过滤结果到 {ckpt}")

        elif step_name == "tokenize":
            df = tokenizer.tokenize_dataframe(df)
            ckpt = checkpoint_path("tokenize")
            df.to_csv(ckpt, index=False)
            logger.info(f"分词完成: {len(df)} 条 | 已保存到 {ckpt}")

        elif step_name == "vectorize":
            X, y, vec, le = vectorizer.vectorize_dataframe(df)
            X_path = PROCESSED_DATA_DIR / "tfidf_X.npy"
            y_path = PROCESSED_DATA_DIR / "labels_y.npy"
            np.save(X_path, X.toarray())
            np.save(y_path, y)
            classes = le.classes_
            logger.info(f"向量化完成: X=({X.shape[0]}, {X.shape[1]}), y=({y.shape[0]}), 类别={len(classes)}")
            logger.info(f"类别映射: {dict(zip(range(len(classes)), classes))}")

        elapsed = time.time() - start_time
        logger.info(f"步骤 [{step_name}] 完成，耗时 {elapsed:.2f} 秒")
        return df

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"步骤 [{step_name}] 失败 (耗时 {elapsed:.2f} 秒): {e}", exc_info=True)
        raise


class Command(BaseCommand):
    help = "运行完整分析管道（原始读取 → 清洗 → 预处理 → 标注 → 过滤 → 分词 → TF-IDF向量化）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--resume",
            type=str,
            default=None,
            choices=STEP_NAMES,
            help=f"从指定步骤恢复 (可选: {', '.join(STEP_NAMES)})",
        )

    def handle(self, *args, **options):
        self._setup_logging()
        resume_step = options.get("resume")

        if resume_step:
            resume_idx = STEP_NAMES.index(resume_step)
            start_idx = resume_idx
            logger.info(f"从步骤 [{resume_step}] 恢复执行")
        else:
            start_idx = 0
            logger.info("从头开始执行管道")

        df = None

        for i in range(start_idx, len(STEP_NAMES)):
            step = STEP_NAMES[i]

            if df is None and step != "raw":
                prev_step = STEP_NAMES[i - 1]
                ckpt = checkpoint_path(prev_step)
                if ckpt and ckpt.exists():
                    logger.info(f"从 checkpoint 加载: {ckpt}")
                    df = pd.read_csv(ckpt)
                else:
                    logger.error(f"找不到上一个 checkpoint: {ckpt}")
                    raise CommandError(f"缺少 {prev_step} 的 checkpoint: {ckpt}")

            df = run_step(step, df)

        logger.info(f"{'='*60}")
        logger.info("管道全部完成!")
        logger.info(f"{'='*60}")

    def _setup_logging(self):
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        root_logger.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        log_dir = settings.BASE_DIR
        file_handler = logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
