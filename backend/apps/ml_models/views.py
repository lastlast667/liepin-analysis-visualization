from datetime import datetime
import os

from altair import param
import json
import tempfile
from pathlib import Path
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.analysis.views import get_distinct_options
from apps.ml_models import matcher
from apps.ml_models.salary_predict import predict
from apps.users.serializers import JobBriefSerializer
from utils.extract_text import extract_pdf_text, extract_docx_text, extract_doc_text
from apps.jobs.models import Job
import pickle
from job_analysis.app_config import MODEL_DIR
from apps.ml_models.recommenders.hybrid_recommender import HybridRecommender
from apps.ml_models.recommenders.svd_recommender import SVDRecommender
from apps.ml_models.recommenders.content_recommender import ContentRecommender
from apps.ml_models.models import MLModel, RecommendationLog, ResumeMatchResult, SalaryPrediction
from django.utils import timezone
from django.db.models import Avg



def extract_text_from_file(uploaded_file):
    """
    从上传的文件中提取文本
    uploaded_file 是 request.FILES 中的 UploadedFile 对象（无磁盘路径）
    """
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp_path = Path(tmp.name)

    try:
        if suffix == '.pdf':
            return extract_pdf_text(tmp_path)
        elif suffix == '.docx':
            return extract_docx_text(tmp_path)
        elif suffix == '.doc':
            return extract_doc_text(tmp_path)
        else:
            raise ValueError(f"不支持的文件类型：{uploaded_file.name}")
    finally:
        # 无论成功还是失败，都清理临时文件
        tmp_path.unlink(missing_ok=True)

@api_view(["GET"])
@permission_classes([AllowAny])
def match_options(request):
    """
    简历匹配选项 API
    获取匹配选项，返回所有有岗位的城市列表、岗位列表、company_scale唯一值、company_industry唯一值
    """
    base_request = Job.objects.all()

    return Response({
        'cities': get_distinct_options(base_request, 'location_city'),
        'categories': get_distinct_options(base_request, 'category'),
        'company_scales': get_distinct_options(base_request, 'company_scale'),
        'company_industries': get_distinct_options(base_request, 'company_industry'),
    })

@api_view(["POST"])
@permission_classes([AllowAny])
def match_resume(request):
    """
    简历匹配 API
    匹配简历，返回匹配结果
    
    参数：
    - resume_file：简历文件
    - filters：筛选条件，格式为JSON字符串

    """
    # 1. 从请求中获取文件和筛选条件
    file = request.FILES.get('file')
    filters_raw = request.data.get('filters')

    # 解析filters
    if not filters_raw:
        return Response({'error': 'Filters are required'}, status=400)
    filters = json.loads(filters_raw)

    if not file:
        return Response({'error': 'No file uploaded'}, status=400)
    if not filters:
        return Response({'error': 'Filters are required'}, status=400)
    
    # 2. 提取简历文本
    resume_text = extract_text_from_file(file)

    # 3. 匹配简历
    results = matcher.match(resume_text, filters)

    # 4. 保存匹配结果
    if request.user.is_authenticated:
        result_dict = {}
        for result in results:
            result_dict[result.get('id')] = result.get('match_score', 0)
        total_count = len(results)
        ResumeMatchResult.objects.create(
            user=request.user,
            results=result_dict,
            total_count=total_count,
        )

    return Response({
        'results': results,
    })

@api_view(["GET"])
@permission_classes([AllowAny])
def salary_predict_options(request):
    """
    预测薪资选项 API
    """
    base_request = Job.objects.all()

    # 从训练模型的元数据中获取数据集大小
    try:
        with open(MODEL_DIR / "salary_predict_meta.pkl", "rb") as f:
            salary_meta = pickle.load(f)
        model_info = {
            "data_count": salary_meta.get("data_count", "--"),
            "r2": salary_meta.get('r2', '--'),
            "mae": salary_meta.get('mae', '--'),
            "model_used": salary_meta.get('model_used', 'CatBoostRegressor'),
        }
    except FileNotFoundError:
        model_info = {"data_count": '--', "r2": '--', "mae": '--'}

    return Response({
        'cities': get_distinct_options(base_request, 'location_city'),
        'categories': get_distinct_options(base_request, 'category'),
        'experience_levels': get_distinct_options(base_request, 'experience_level'),
        'educations': get_distinct_options(base_request, 'education'),
        'company_scales': get_distinct_options(base_request, 'company_scale'),
        'company_industries': get_distinct_options(base_request, 'company_industry'),
        'model_info': model_info,
    })

@api_view(["POST"])
@permission_classes([AllowAny])
def salary_predict(request):
    """
    预测薪资 API
    """
    # 1. 从请求中获取参数
    params = request.data
    
    # 2. 调用函数预测薪资
    result = predict(params)

    # 3. 保存预测记录
    if request.user.is_authenticated:
        SalaryPrediction.objects.create(
            user=request.user,
            city=params.get('location_city', ''),
            category=params.get('category', ''),
            experience_level=params.get('experience_level', ''),
            education=params.get('education', ''),
            company_scale=params.get('company_scale', ''),
            company_industry=params.get('company_industry', ''),
            predicted_salary=result.get('predicted_salary'),
            predicted_min=result.get('predicted_min'),
            predicted_max=result.get('predicted_max'),
            model_used=result.get('model_used', ''),
            feature_importance=result.get('feature_importance', []),
        )

    return Response(result)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_recommend(request):
    """
    岗位推荐 API
    """
    strategy_param = request.query_params.get('strategy','hybrid')
    top_k = int(request.query_params.get('top_k', 20))
    user = request.user

    # 1. 根据策略选择推荐器
    if strategy_param == 'hybrid':
        recommender = HybridRecommender()
    elif strategy_param == 'svd':
        recommender = SVDRecommender()
    elif strategy_param == 'content':
        recommender = ContentRecommender()
    else:
        return Response({'error': 'strategy strategy is not supported'}, status=400)
    
    # 2. 调用推荐器获取推荐结果
    results = recommender.recommend(user.id, top_k=top_k)  # [{"job_id": 1, "score": 0.8}, ...]

    # 归一化到 0-100
    if results:
        scores = [item["score"] for item in results]
        min_score, max_score = min(scores), max(scores)
        range_score = max_score - min_score
        if range_score > 0.001:
            for item in results:
                # 映射到 60-100，保留区分度
                item["score"] = round((item["score"] - min_score) / range_score * 40 + 60, 2)
        else:
            for item in results:
                item["score"] = 100

    # 3. 查岗位
    job_ids = [item["job_id"] for item in results]
    jobs_qs = Job.objects.filter(id__in=job_ids)
    job_map = {job.id: job for job in jobs_qs}  # 岗位ID到岗位的映射
    ordered_jobs = [job_map.get(item["job_id"]) for item in results if item["job_id"] in job_map]  # 按推荐结果排序，过滤不存在的岗位

    # 4. 保存推荐记录
    log_entries = []    # 推荐岗位列表
    for item in results:
        log_entries.append(
            RecommendationLog(
                user=user,
                job_id=item["job_id"],  # django自动识别 job_id 为 FK 的列名
                score=item["score"],
                strategy=strategy_param,
            )
        )
    RecommendationLog.objects.bulk_create(log_entries, ignore_conflicts=True)   # 批量创建推荐记录
    
    # 5. 序列化岗位，传入 score_map 给 context
    score_map = {item["job_id"]: item["score"] for item in results}
    serializer = JobBriefSerializer(ordered_jobs, many=True, context={"score_map": score_map})
    
    return Response({
        "strategy": strategy_param,
        "top_k": top_k,
        "recommendations": serializer.data,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def model_status(request):
    """
    模型状态 API
    返回薪资预测、简历匹配、岗位推荐三个模型的实时运行状态
    """
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. 薪资预测模型
    salary_model = MLModel.objects.filter(
        model_type='salary_predictor', is_active=True
    ).first()

    # 最新训练时间：读取模型文件的修改时间
    last_train_time = None
    model_path = MODEL_DIR / "salary_model.pkl"
    if model_path.exists():
        mtime = os.path.getmtime(model_path)
        last_train_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')

    # 准确率
    accuracy = None
    if salary_model and salary_model.accuracy is not None:
        accuracy = round(salary_model.accuracy, 3)
    else:
        try:
            with open(MODEL_DIR / "salary_predict_meta.pkl", "rb") as f:
                meta = pickle.load(f)    # 从元数据中获取准确率
            if meta.get('r2') is not None:
                accuracy = round(meta.get('r2'), 3)
        except FileNotFoundError:
            pass

    # 今日预测调用次数
    today_calls = SalaryPrediction.objects.filter(created_at__gte=today_start).count()

    # 状态判断
    if salary_model and salary_model.is_active:
        status = "running"
    elif last_train_time:
        status = "running"  # 有模型文件就算运行中
    else:
        status = "pending"
    
    # 2. 简历匹配模型
    match_model = MLModel.objects.filter(
        model_type='resume_matcher', is_active=True
    ).first()

    # 今日匹配次数
    today_matches = ResumeMatchResult.objects.filter(created_at__gte=today_start)
    match_count = today_matches.count()

    # 最佳匹配平均相似度
    all_scores = []
    for record in today_matches:
        all_scores.append(max(record.results.values()))  # list.extend(可迭代对象)：把传入序列里的每一个元素，逐个追加到原列表尾部
    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

    # 状态判断
    if match_model and match_model.is_active:
        match_status = "running"
    elif match_count > 0:
        match_status = "pending"
    else:
        match_status = "pending"
    
    # 3. 岗位推荐模型
    rec_model = MLModel.objects.filter(
        model_type='recommender', is_active=True
    ).first()

    # 今日推荐次数
    today_recs = RecommendationLog.objects.filter(created_at__gte=today_start)
    hybrid_count = today_recs.filter(strategy='hybrid').count()
    svd_count = today_recs.filter(strategy='svd').count()
    content_count = today_recs.filter(strategy='content').count()

    # 状态判断
    if rec_model and rec_model.is_active:
        rec_status = "running"
    elif hybrid_count > 0 or svd_count > 0 or content_count > 0:
        rec_status = "pending"
    else:
        rec_status = "pending"

    return Response({
        "salary_prediction": {
            "last_train_time": last_train_time or "--",
            "accuracy": accuracy,
            "today_calls": today_calls,
            "status": status,
        },
        "resume_match": {
            "today_matches": match_count,
            "avg_score": avg_score,
            "status": match_status,
        },
        "job_recommend": {
            "strategies": {
                "hybrid": hybrid_count,
                "cf": svd_count,
                "content": content_count,
            },
            "status": rec_status,
        },
    })
