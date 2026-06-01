import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_analysis.settings")
django.setup()

from apps.analysis.views import job_search
from django.test import RequestFactory

factory = RequestFactory()


def test_no_filters():
    """测试无筛选条件（全量查询第一页）"""
    request = factory.get("/api/analysis/jobs/")
    response = job_search(request)
    print("=== 无筛选条件 ===")
    print(f"  total={response.data['total']}, page={response.data['page']}, "
          f"page_size={response.data['page_size']}, total_pages={response.data['total_pages']}")
    print(f"  results 条数: {len(response.data['results'])}")
    if response.data['results']:
        print(f"  第一条: {response.data['results'][0]['title']}")
    print(f"  hot_jobs 条数: {len(response.data['hot_jobs'])}")
    print(f"  hot_cities 条数: {len(response.data['hot_cities'])}")
    print(f"  hot_companies 条数: {len(response.data['hot_companies'])}")
    print(f"  city_options 条数: {len(response.data['city_options'])}")
    print()


def test_keyword():
    """测试关键词筛选"""
    request = factory.get("/api/analysis/jobs/", {"keyword": "前端"})
    response = job_search(request)
    print("=== 关键词='前端' ===")
    print(f"  total={response.data['total']}")
    for r in response.data['results'][:3]:
        print(f"    - {r['title']} | {r['company_name']}")
    print()


def test_salary():
    """测试薪资范围筛选"""
    request = factory.get("/api/analysis/jobs/", {"salary": "10-20k"})
    response = job_search(request)
    print("=== 薪资=10-20k ===")
    print(f"  total={response.data['total']}")
    for r in response.data['results'][:3]:
        print(f"    - {r['title']} | {r['salary']} | avg={r['month_salary_avg']}")
    print()


def test_salary_bottom():
    """测试最低薪资范围"""
    request = factory.get("/api/analysis/jobs/", {"salary": "10k以内"})
    response = job_search(request)
    print("=== 薪资=10k以内 ===")
    print(f"  total={response.data['total']}")
    for r in response.data['results'][:3]:
        print(f"    - {r['title']} | {r['salary']} | avg={r['month_salary_avg']}")
    print()


def test_salary_top():
    """测试最高薪资范围"""
    request = factory.get("/api/analysis/jobs/", {"salary": "50k以上"})
    response = job_search(request)
    print("=== 薪资=50k以上 ===")
    print(f"  total={response.data['total']}")
    for r in response.data['results'][:3]:
        print(f"    - {r['title']} | {r['salary']} | avg={r['month_salary_avg']}")
    print()


def test_city():
    """测试城市筛选"""
    request = factory.get("/api/analysis/jobs/", {"location_city": "北京"})
    response = job_search(request)
    print("=== 城市=北京 ===")
    print(f"  total={response.data['total']}")
    for r in response.data['results'][:3]:
        print(f"    - {r['title']} | {r['location_city']} | {r['company_name']}")
    print()


def test_education():
    """测试学历筛选"""
    request = factory.get("/api/analysis/jobs/", {"education": "本科"})
    response = job_search(request)
    print("=== 学历=本科 ===")
    print(f"  total={response.data['total']}")
    for r in response.data['results'][:3]:
        print(f"    - {r['title']} | {r['education']} | {r['company_name']}")
    print()


def test_experience():
    """测试经验筛选"""
    request = factory.get("/api/analysis/jobs/", {"experience_level": "3-5年"})
    response = job_search(request)
    print("=== 经验=3-5年 ===")
    print(f"  total={response.data['total']}")
    for r in response.data['results'][:3]:
        print(f"    - {r['title']} | {r['experience_level']} | {r['company_name']}")
    print()


def test_sort_by_salary():
    """测试按薪资排序"""
    request = factory.get("/api/analysis/jobs/", {"sort_by": "salary"})
    response = job_search(request)
    print("=== 排序=薪资降序 ===")
    for r in response.data['results'][:3]:
        print(f"    - {r['title']} | avg={r['month_salary_avg']}")
    print()


def test_combined():
    """测试多个筛选条件组合"""
    request = factory.get("/api/analysis/jobs/", {
        "keyword": "java",
        "location_city": "北京",
        "salary": "20-30k",
        "education": "本科",
    })
    response = job_search(request)
    print("=== 组合筛选(keyword=java, city=北京, salary=20-30K, education=本科) ===")
    print(f"  total={response.data['total']}")
    for r in response.data['results'][:5]:
        print(f"    - {r['title']} | {r['location_city']} | {r['salary']} | {r['education']}")
    print()


def test_pagination():
    """测试翻页"""
    request_page1 = factory.get("/api/analysis/jobs/", {"page": 1, "page_size": 3})
    request_page2 = factory.get("/api/analysis/jobs/", {"page": 2, "page_size": 3})
    response1 = job_search(request_page1)
    response2 = job_search(request_page2)
    print("=== 翻页测试(page_size=3) ===")
    print(f"  第1页: total={response1.data['total']}, 返回{len(response1.data['results'])}条")
    print(f"  第2页: total={response2.data['total']}, 返回{len(response2.data['results'])}条")
    if response1.data['results'] and response2.data['results']:
        id1 = [r['id'] for r in response1.data['results']]
        id2 = [r['id'] for r in response2.data['results']]
        overlap = set(id1) & set(id2)
        print(f"  两页id重叠数: {len(overlap)}（应为0）")
    print()


if __name__ == "__main__":
    test_no_filters()
    test_keyword()
    test_salary()
    test_salary_bottom()
    test_salary_top()
    test_city()
    test_education()
    test_experience()
    test_sort_by_salary()
    test_combined()
    test_pagination()