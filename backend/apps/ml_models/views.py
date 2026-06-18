import json
import tempfile
from pathlib import Path
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from apps.analysis.views import get_distinct_options
from apps.ml_models import matcher
from apps.ml_models.salary_predict import predict
from utils.extract_text import extract_pdf_text, extract_docx_text, extract_doc_text
from apps.jobs.models import Job
import pickle
from job_analysis.app_config import MODEL_DIR



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

# Create your views here.
@api_view(["GET"])
@permission_classes([AllowAny])
def match_options(request):
    """
    获取匹配选项，返回所有有岗位的城市列表、company_scale唯一值、company_industry唯一值
    """
    base_request = Job.objects.all()

    return Response({
        'cities': get_distinct_options(base_request, 'location_city'),
        'company_scales': get_distinct_options(base_request, 'company_scale'),
        'company_industries': get_distinct_options(base_request, 'company_industry'),
    })

@api_view(["POST"])
@permission_classes([AllowAny])
def match_resume(request):
    """
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
    预测薪资选项
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
    预测薪资
    """
    params = request.data
    result = predict(params)
    return Response(result)
