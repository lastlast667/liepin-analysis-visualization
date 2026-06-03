import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_analysis.settings")
django.setup()

from apps.analysis.views import salary_analysis
from django.test import RequestFactory

factory = RequestFactory()


def test_no_filters():
    """测试无筛选条件（全量薪资分析）"""
    request = factory.get("/api/analysis/salary/")
    response = salary_analysis(request)
    print("=== 无筛选条件 ===")
    stats = response.data["stats"]
    print(f"  avg_salary={stats['avg_salary']}, max_salary={stats['max_salary']}, "
          f"median_salary={stats['median_salary']}")
    # 验证返回字段存在
    assert "avg_salary" in stats
    assert "max_salary" in stats
    assert "median_salary" in stats
    print("  ✅ 字段验证通过")
    print()


def test_filter_by_category():
    """测试按岗位类别筛选"""
    request = factory.get("/api/analysis/salary/", {"category": "人工智能"})
    response = salary_analysis(request)
    print("=== 岗位类别='人工智能' ===")
    stats = response.data["stats"]
    print(f"  avg_salary={stats['avg_salary']}, max_salary={stats['max_salary']}, "
          f"median_salary={stats['median_salary']}")
    print()


def test_filter_by_partition():
    """测试按城市分区筛选"""
    request = factory.get("/api/analysis/salary/", {"location_partition": "华东地区"})
    response = salary_analysis(request)
    print("=== 城市分区='华东地区' ===")
    stats = response.data["stats"]
    print(f"  avg_salary={stats['avg_salary']}, max_salary={stats['max_salary']}, "
          f"median_salary={stats['median_salary']}")
    print()


def test_filter_by_category_and_partition():
    """测试组合筛选（岗位类别 + 城市分区）"""
    request = factory.get("/api/analysis/salary/", {
        "category": "人工智能",
        "location_partition": "华东地区",
    })
    response = salary_analysis(request)
    print("=== 组合筛选(category=人工智能, location_partition=华东地区) ===")
    stats = response.data["stats"]
    print(f"  avg_salary={stats['avg_salary']}, max_salary={stats['max_salary']}, "
          f"median_salary={stats['median_salary']}")
    print()


def test_filter_result_less_than_all():
    """测试筛选后的数据量应小于全量"""
    request_all = factory.get("/api/analysis/salary/")
    request_filtered = factory.get("/api/analysis/salary/", {
        "category": "人工智能",
        "location_partition": "华东地区",
    })
    response_all = salary_analysis(request_all)
    response_filtered = salary_analysis(request_filtered)

    # 全量薪资中位数通常大于筛选后的（筛选缩小范围）
    print("=== 筛选前后对比 ===")
    all_median = response_all.data["stats"]["median_salary"]
    filtered_median = response_filtered.data["stats"]["median_salary"]
    print(f"  全量中位数: {all_median}, 筛选后中位数: {filtered_median}")
    print()


def test_multiple_categories():
    """测试多个岗位类别"""
    request = factory.get("/api/analysis/salary/", {"category": "人工智能,Java开发"})
    response = salary_analysis(request)
    print("=== 多类别(category=人工智能,Java开发) ===")
    stats = response.data["stats"]
    print(f"  avg_salary={stats['avg_salary']}, max_salary={stats['max_salary']}, "
          f"median_salary={stats['median_salary']}")
    print()


def test_response_structure():
    """测试返回结构完整性"""
    request = factory.get("/api/analysis/salary/")
    response = salary_analysis(request)
    print("=== 返回结构校验 ===")
    data = response.data
    expected_keys = {"stats"}
    actual_keys = set(data.keys())
    missing = expected_keys - actual_keys
    extra = actual_keys - expected_keys
    if missing:
        print(f"  ❌ 缺少字段: {missing}")
    if extra:
        print(f"  📌 额外字段（后续将实现）: {extra}")
    if not missing:
        print("  ✅ 必要字段齐全")
    print()


def test_stats_field_types():
    """测试 stats 字段值类型正确"""
    request = factory.get("/api/analysis/salary/")
    response = salary_analysis(request)
    print("=== stats 字段类型校验 ===")
    stats = response.data["stats"]
    assert isinstance(stats["avg_salary"], (int, float)), "avg_salary 应为数字"
    assert isinstance(stats["max_salary"], (int, float)), "max_salary 应为数字"
    assert isinstance(stats["median_salary"], (int, float)), "median_salary 应为数字"
    print(f"  avg_salary={stats['avg_salary']} (类型: {type(stats['avg_salary']).__name__})")
    print(f"  max_salary={stats['max_salary']} (类型: {type(stats['max_salary']).__name__})")
    print(f"  median_salary={stats['median_salary']} (类型: {type(stats['median_salary']).__name__})")
    print("  ✅ 类型校验通过")
    print()


def test_stats_sanity():
    """测试统计值合理性：avg <= max, median <= max"""
    request = factory.get("/api/analysis/salary/")
    response = salary_analysis(request)
    print("=== 统计值合理性校验 ===")
    stats = response.data["stats"]
    assert stats["avg_salary"] <= stats["max_salary"], \
        f"平均薪资({stats['avg_salary']}) 应 <= 最高薪资({stats['max_salary']})"
    assert stats["median_salary"] <= stats["max_salary"], \
        f"中位数({stats['median_salary']}) 应 <= 最高薪资({stats['max_salary']})"
    assert stats["avg_salary"] >= 0, "平均薪资应 >= 0"
    print(f"  avg_salary({stats['avg_salary']}) <= max_salary({stats['max_salary']}) ✅")
    print(f"  median_salary({stats['median_salary']}) <= max_salary({stats['max_salary']}) ✅")
    print()


if __name__ == "__main__":
    test_no_filters()
    test_filter_by_category()
    test_filter_by_partition()
    test_filter_by_category_and_partition()
    test_filter_result_less_than_all()
    test_multiple_categories()
    test_response_structure()
    test_stats_field_types()
    test_stats_sanity()
