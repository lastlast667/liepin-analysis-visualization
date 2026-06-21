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
    # 从请求中获取文件和筛选条件
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
    
    resume_text = extract_text_from_file(file)

    results = matcher.match(resume_text, filters)

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
    params = request.data
    result = predict(params)
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

    # 4. 序列化岗位，传入 score_map 给 context
    score_map = {item["job_id"]: item["score"] for item in results}
    serializer = JobBriefSerializer(ordered_jobs, many=True, context={"score_map": score_map})
    
    return Response({
        "strategy": strategy_param,
        "top_k": top_k,
        "recommendations": serializer.data,
    })

    
