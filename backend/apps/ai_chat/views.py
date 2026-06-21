"""
AI 助手 API
纯代理转发 ，没有任何 agent 逻辑
"""

from django.shortcuts import render
from openai import OpenAI
from job_analysis import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1",
)

SYSTEM_PROMPT = """你是"猎聘分析"平台的AI职业助手，专注于职业规划和模拟面试。
你可以：
1. 职业规划：分析行业趋势、推荐技能提升方向、规划职业发展路径
2. 模拟面试：根据岗位要求出面试题、评估回答、提供建议

请使用中文回答，语气专业且亲切。回答内容基于通用职业知识，不依赖具体的岗位数据库。"""

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat(request):
    """AI 助手 API"""
    messages = request.data.get("messages")
    
    # 构造给 API 的消息列表
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        response = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=api_messages,
            temperature=0.7,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content
        return Response({"reply": reply})
    except Exception as e:
        return Response({"reply": f"抱歉，请求失败：{str(e)}"}, status=500)
