# 离线训练，python manage.py
"""
训练简历匹配分类器
"""
import pickle
from django.core.management.base import BaseCommand
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.naive_bayes import MultinomialNB
from apps.analysis.vectorizer import vectorize_text
from apps.jobs.models import Job
from job_analysis.app_config import MODEL_DIR
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_classifier")

class Command(BaseCommand):
    """
    训练分类器
    """
    help = "训练分类器"

    def handle(self, *args, **options):
        """
        处理命令逻辑
        """
        # 筛选出有tokenized_words和category的岗位
        results = Job.objects.all().exclude(tokenized_words__in=["", None]).exclude(category__in=["", None]).values_list("tokenized_words", "category")

        # 提取tokenized_words和category
        words_list  = []
        categories_list = []
        for words, category in results:
            words_list.append(words)
            categories_list.append(category)
        
        # 对文本进行TF-IDF向量化
        X, y, vectorizer, encoder = vectorize_text(words_list, categories_list)

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # 定义模型
        models = {
            "MultinomialNB": MultinomialNB(),           # 多项式贝叶斯分类器
            "LogisticRegression": LogisticRegression(), # 逻辑回归分类器
        }

        # 交叉验证对比
        for name, clf in models.items():
            scores = cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")
            print(f"=== {name} ===")
            print(f"  交叉验证折准确率: {scores.mean():.4f}")
            print()

        # 选最好的模型，全量训练
        best_model = models["LogisticRegression"]
        best_model.fit(X, y)
        print(f"最佳模型准确率: {best_model.score(X, y):.4f}")

        # 测试集评估
        y_pred = best_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"测试集准确率: {accuracy:.4f}")
        print(classification_report(
            y_test, y_pred, 
            target_names=encoder.classes_,
            labels=list(range(len(encoder.classes_)))   # 确保标签顺序与 encoder.classes_ 一致
            ))

        # 保存模型
        best_model_path = MODEL_DIR / "best_model.pkl"
        with open(best_model_path, "wb") as f:
            pickle.dump(best_model, f)
        logger.info(f"已保存 最佳模型 LogisticRegression 到 {best_model_path}")







    
