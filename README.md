# 猎聘数据分析平台

> Django + Vue 3 + DRF + scikit-learn 全栈项目  
> 涵盖数据采集、清洗建模、智能推荐与可视化展示的完整机器学习数据管道

---

## 技术栈

| 分类 | 技术 |
|------|------|
| **后端框架** | Django 5.2, Django REST Framework, SimpleUI |
| **数据库** | MySQL 8.0 (utf8mb4), Redis (缓存) |
| **前端** | Vue 3 (Composition API), Vue Router 4, Pinia, Tailwind CSS 3, ECharts 5 |
| **机器学习** | scikit-learn (RandomForest, SVD, TF-IDF), jieba, CatBoost |
| **爬虫** | DrissionPage (浏览器自动化), 快代理 IP 轮换 |
| **AI** | DeepSeek API (智能客服) |
| **部署** | Nginx, cpolar 内网穿透 |

---

## 项目结构

```
liepin-analysis-visualization/
├── backend/
│   ├── job_analysis/              # Django 项目配置
│   ├── apps/
│   │   ├── users/                 # 用户系统：认证/收藏/浏览历史/个人资料
│   │   ├── jobs/                  # 岗位数据模型（50+ 字段，12次迭代迁移）
│   │   ├── analysis/              # 数据分析：搜索/筛选、公司/地区/薪资分析
│   │   │   └── recommenders/      # 可插拔推荐系统（多源聚合引擎）
│   │   ├── ml_models/             # 机器学习：薪资预测/岗位推荐/简历匹配
│   │   │   ├── recommenders/      # SVD协同过滤 / 内容推荐 / 混合推荐
│   │   │   ├── salary_predict.py  # RandomForest薪资预测
│   │   │   ├── matcher.py         # TF-IDF + 余弦相似度简历匹配
│   │   │   └── classifier.py      # 岗位类别分类器
│   │   ├── spider/                # 猎聘爬虫（DrissionPage + 反爬策略）
│   │   └── ai_chat/               # DeepSeek AI 智能客服
│   ├── models/                    # 训练好的模型文件
│   └── utils/                     # 公共工具
├── frontend/
│   └── src/
│       ├── views/                 # 11 个业务页面
│       ├── components/            # JobList / JobDetail / CompanyDetail 等
│       ├── api/                   # Axios 接口封装
│       ├── router/                # 路由 + 鉴权守卫
│       └── stores/                # Pinia 状态管理
└── data/                          # 词表与数据文件
```

---

## 核心功能

### 数据分析与可视化（5 个页面）

| 页面 | 功能 |
|------|------|
| **仪表盘** | 全量数据总览、今日新增、活跃公司统计 |
| **岗位搜索** | 多维度筛选（城市/薪资/学历/经验）、排序、分页、热门面板联动 |
| **公司分析** | Top10 公司排行榜、行业/城市/薪资多维度分布、热力图 |
| **地区分布** | 自定义省份分区体系、地图热力、学历经验交叉分析 |
| **薪资分析** | 城市薪资排名、行业薪资排名、薪资分布可视化 |

### 机器学习（3 个模块）

**薪资预测**
- RandomForest Regressor，基于城市/类别/经验/学历/公司规模等特征
- 输出月薪 + MAE 置信区间（最低/最高估计）
- 自动提取特征重要性并可视化各因子影响占比

**岗位推荐**
- 协同过滤（SVD）：基于用户收藏/浏览行为的矩阵分解
- 内容推荐：基于用户期望城市和岗位类别的特征匹配
- 混合推荐：SVD(60%) + 内容(40%) 加权融合，兼顾探索与精准
- 支持三种策略切换，匹配度分数归一化展示

**简历匹配**
- TF-IDF 向量化 + 余弦相似度
- 城市/薪资/类别/经验四重过滤
- 支持 PDF/DOCX/DOC 格式简历上传

### 智能客服
- 集成 DeepSeek API，流式响应对话
- 上下文保持，可回答平台使用和数据含义等问题

### 用户系统
- Token 认证登录/注册
- 岗位收藏/取消收藏
- 浏览历史自动记录
- 个人资料管理

### 数据采集
- 基于 DrissionPage 的浏览器自动化爬虫
- 监听 XHR 接口捕获列表数据，lxml 解析详情页
- 反爬策略：快代理 IP 轮换、UA 随机切换、Cookie 池持久化
- 40+ 岗位类别关键词，覆盖万级岗位数据

---

## API 接口

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `/api/auth/` | 登录/注册/登出/用户信息 |
| 收藏 | `/api/auth/favorites/` | 收藏/取消/列表 |
| 浏览历史 | `/api/auth/browse-history/` | 记录/查询 |
| 岗位搜索 | `/api/analysis/jobs/` | 多条件筛选/排序/分页 |
| 岗位详情 | `/api/analysis/jobs/<id>/` | 详情/相似推荐/薪资分析 |
| 公司分析 | `/api/analysis/company/` | 多维度统计 |
| 地区分布 | `/api/analysis/location/` | 城市/省份/分区统计 |
| 薪资分析 | `/api/analysis/salary/` | 城市/行业薪资排行 |
| 仪表盘 | `/api/analysis/dashboard/` | 全量数据总览 |
| 薪资预测 | `/api/ml/salary-predict/` | 参数提交 → 预测薪资 |
| 岗位推荐 | `/api/ml/recommend/` | 三种策略 → 推荐列表 |
| 简历匹配 | `/api/ml/resume-match/` | 简历上传 → 匹配结果 |
| 模型状态 | `/api/ml/ml-models/` | 各模型运行状态 |
| AI 聊天 | `/api/chat/chat/` | DeepSeek 对话 |

---

## 快速开始

### 前置条件

- Python 3.12+, Node.js 18+, MySQL 8.0

### 后端启动

```bash
cd backend
pip install -r requirements.txt

# 修改 job_analysis/settings.py 中 DATABASES 配置

python manage.py makemigrations
python manage.py migrate
python manage.py import_jobs        # 导入岗位数据
python manage.py init_ml_models     # 初始化 ML 模型
python manage.py train_salary_model # 训练薪资预测模型（可选）
python manage.py train_svd_model    # 训练推荐模型（可选）

python manage.py runserver 8000
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

---

## 关键设计决策

**为什么用 DrissionPage 而非 Scrapy/requests？**
猎聘前端客户端渲染，列表数据通过 XHR 返回，存在反爬验证。DrissionPage 可监听网络请求直接捕获 API 响应，同时复用浏览器环境绕过验证。

**为什么用 RandomForest 而非深度学习？**
岗位数据维度有限（~10 个特征），RandomForest 在小样本场景下表现优异、可解释性强，直接输出特征重要性。

**为什么岗位推荐分三种策略？**
SVD 适合有行为数据的用户；内容推荐适合新用户（冷启动）；混合推荐综合两者优势，为默认策略。

**为什么可插拔推荐系统？**
将推荐逻辑拆分为独立插件，核心引擎仅负责调度聚合。新增推荐策略只需新增文件 + 注册一行权重，完全不影响现有代码。

---

## 开发历程

项目历时约 6 周，按以下节奏推进：

1. **爬虫开发** — 基于 DrissionPage 的猎聘爬虫，逐步增强反爬能力
2. **数据工程** — 清洗/预处理/标注/分词/向量化全自动 pipeline
3. **Django 后端** — 企业级项目结构重构，6 个业务 App
4. **数据分析 API** — 岗位搜索/公司分析/地区分布/薪资分析
5. **前端开发** — Vue 3 框架搭建 + 11 个页面 + ECharts 可视化
6. **ML 模块** — 薪资预测/简历匹配/岗位推荐
7. **用户系统** — 认证/收藏/浏览历史/个人中心
8. **AI 客服** — DeepSeek API 集成
9. **全局优化** — 仪表盘、Z-index 修复、推荐日志重构、密钥安全清理
