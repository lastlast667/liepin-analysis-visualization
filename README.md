# 基于机器学习的招聘数据分析与可视化预测推荐系统

&gt; Django + Vue3 + DRF + scikit-learn + DeepSeek 全栈项目

## 技术栈
[表格：后端/前端/ML/数据库/爬虫分别用什么]

## 项目结构
[表格：项目目录结构]

## 快速开始
[怎么启动后端、怎么启动前端、怎么初始化数据库]
```text
liepin-analysis-visualization/                 ← 项目根目录
│
├── backend/                          ← Django 后端（整家公司）
│   │
│   ├── job_analysis/                ← 公司总部（Project配置）
│   │   ├── settings.py              ← 公司规章制度
│   │   ├── urls.py                  ← 公司总前台（路由入口）
│   │   ├── wsgi.py                  ← 公司大门（接收外部请求）
│   │   └── asgi.py                  ← 公司侧门（异步请求入口）
│   │
│   ├── apps/                        ← 各部门办公区（所有App）
│   │   │
│   │   ├── users/                   ← 人事部（用户管理）
│   │   │   ├── models.py           ← 【数据库表定义】User表、收藏表、浏览历史表
│   │   │   ├── views.py            ← 【API接口】登录/注册/收藏/历史
│   │   │   ├── urls.py             ← 【子路由】/api/users/login/ 走哪个函数
│   │   │   ├── serializers.py      ← 【数据转换器】Python对象 → JSON
│   │   │   ├── admin.py            ← 【后台注册】SimpleUI里能看到用户数据
│   │   │   └── apps.py             ← App配置信息
│   │   │
│   │   ├── jobs/                    ← 数据部（岗位数据管理）
│   │   │   ├── models.py           ← 【数据库表定义】Job表（标题/公司/薪资/类别...）
│   │   │   ├── views.py            ← 【API接口】岗位列表/搜索/详情
│   │   │   ├── urls.py             ← 【子路由】/api/jobs/、/api/jobs/<id>/
│   │   │   ├── serializers.py
│   │   │   └── admin.py
│   │   │
│   │   ├── analysis/                ← 分析部（数据分析+可视化）
│   │   │   ├── models.py           ← 【数据库表定义】分析报告快照表
│   │   │   ├── views.py            ← 【API接口】仪表盘数据/薪资分布/城市分布
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   └── services.py         ← 【分析逻辑】算平均值、统计分布、生成图表数据
│   │   │
│   │   ├── ml_models/               ← 机器学习部
│   │   │   ├── models.py           ← 【数据库表定义】ML模型元数据表
│   │   │   ├── views.py            ← 【API接口】薪资预测/文本分类/模型训练触发
│   │   │   ├── urls.py
│   │   │   ├── serializers.py
│   │   │   └── services.py         ← 【ML逻辑】RandomForest训练预测/LSTM分类
│   │   │
│   │   ├── recommendation/          ← 推荐部（协同过滤）
│   │   │   ├── models.py
│   │   │   ├── views.py            ← 【API接口】推荐岗位TOP5
│   │   │   ├── urls.py
│   │   │   └── services.py         ← 【推荐算法】用户相似度计算/协同过滤
│   │   │
│   │   ├── resume_match/            ← 匹配部（简历匹配）
│   │   │   ├── models.py
│   │   │   ├── views.py            ← 【API接口】上传简历→返回匹配结果
│   │   │   ├── urls.py
│   │   │   └── services.py         ← 【匹配逻辑】TF-IDF向量化/余弦相似度排序
│   │   │
│   │   ├── spider/                  ← 采集部（爬虫控制）
│   │   │   ├── models.py
│   │   │   ├── views.py            ← 【API接口】管理员触发爬取/查看状态
│   │   │   ├── urls.py
│   │   │   └── services.py         ← 【爬虫调度】调用DrissionPage执行爬取
│   │   │
│   │   └── ai_chat/                 ← 客服部（DeepSeek AI）
│   │       ├── models.py           ← 【数据库表定义】对话记录表
│   │       ├── views.py            ← 【API接口】发送消息→返回AI回复
│   │       ├── urls.py
│   │       └── services.py         ← 【AI逻辑】调用DeepSeek API/流式响应
│   │
│   ├── utils/                       ← 公共工具箱
│   │   ├── response.py             ← 统一API响应格式
│   │   ├── exceptions.py           ← 自定义异常
│   │   └── pagination.py           ← 分页配置
│   │
│   ├── models/                   ← 训练好的模型文件（存在磁盘上）
│   │   ├── salary_rf_model.pkl
│   │   ├── text_classifier.pkl
│   │   └── tfidf_vectorizer.pkl
│   │
│   ├── manage.py                    ← Django管理命令入口
│   └── requirements.txt             ← Python依赖包清单
│
├── frontend/                        ← Vue3 前端
│   ├── src/
│   │   ├── views/                   ← 页面文件（每个侧边栏菜单对应一个）
│   │   │   ├── Dashboard.vue       ← 仪表盘页面
│   │   │   ├── JobSearch.vue       ← 岗位搜索页面
│   │   │   ├── Analysis.vue        ← 数据分析页面
│   │   │   ├── SalaryPredict.vue   ← 薪资预测页面
│   │   │   ├── ResumeMatch.vue     ← 简历匹配页面
│   │   │   ├── AIChat.vue          ← AI客服页面
│   │   │   └── ...
│   │   │
│   │   ├── components/              ← 公共组件（复用的UI块）
│   │   │   ├── Sidebar.vue         ← 侧边栏
│   │   │   ├── Header.vue          ← 顶部导航
│   │   │   └── Chart.vue           ← ECharts图表封装
│   │   │
│   │   ├── api/                     ← 前端调用后端的接口封装
│   │   │   ├── jobs.js             ← 岗位相关请求
│   │   │   ├── analysis.js         ← 数据分析请求
│   │   │   └── users.js            ← 用户相关请求
│   │   │
│   │   ├── router/                  ← 页面路由配置
│   │   ├── stores/                  ← 全局状态管理（Pinia）
│   │   ├── App.vue                  ← 根组件
│   │   └── main.js                  ← 入口文件
│   │
│   ├── index.html
│   └── package.json
│
├── data/                            ← 爬虫原始数据
│   └── raw/
│
├── docs/                            ← 文档
│   └── README.md
│
└── .gitignore                       ← Git忽略文件配置
```

## 核心功能
- 仪表盘：岗位数据总览、趋势分析
- 岗位搜索：关键词+多条件筛选
- 数据分析：薪资分布/地区分布/公司统计
- 薪资预测：输入城市/经验/学历预测薪资(RandomForest)
- 岗位推荐：基于用户收藏+浏览的协同过滤
- 简历匹配：上传简历，TF-IDF+余弦相似度匹配Top5岗位
- AI客服：DeepSeek API智能问答

## 关键设计决策
[这是面试官最关心的！]
- 为什么用Django+DRF而不是Flask：需要Admin后台和用户认证
- 为什么爬虫用DrissionPage不用requests：猎聘反爬升级
- 标注策略：搜索关键词默认+标题校验修正，不用if-else全量推断
- ML模型选择：RandomForest vs TensorFlow LSTM对比实验
- 单池搜索而非多池：数据量充足，简化架构

## 开发顺序
[表格：开发顺序]
| 天数      | 步骤                           | 做什么                                                        |
| ------- | ---------------------------- | ---------------------------------------------------------- |
| **第1天** | 写爬虫文件                  | 用 DrissionPage 爬猎聘岗位数据，保存到 data/raw/ 目录下 |
| **第1天** | 写数据预处理和标注文件                  | 读取 raw.csv，处理缺失值、异常值、重复值，标注岗位类型category |
| **第2天** | 补齐 App 基础文件                  | 给 analysis/spider/ml\_models 等 8 个 App 执行 startapp / 手动补文件 |
| **第2天** | 写 `settings.py`              | 注册所有 App、配 MySQL、配 DRF、配 CORS、配 SimpleUI                   |
| **第2天** | 写所有 `models.py`              | 定义数据库表（Job/User/Favorite/History/MLModel 等）                |
| **第3天** | `makemigrations` + `migrate` | 在 MySQL 里**创建空表**                                          |
| **第3天** | 数据导入脚本                       | 把 processed.csv → 写入 MySQL（用 Django ORM 或 raw SQL）         |
| **第4天** | **写 services.py / ML 逻辑**    | 薪资预测模型训练/加载、文本分类器训练、协同过滤算法实现、简历匹配 TF-IDF 加载                |
| **第4天** | **写 analysis 的 services.py** | 仪表盘统计计算、薪资分布聚合、城市分布统计                                      |
| **第5天** | 写 `views.py` 框架（空壳）          | 所有 API 先返回空数据或 mock 数据，保证 URL 能访问通                         |
| **第6天** | 写 `views.py` 真实逻辑            | 调用 services/ML 逻辑，返回真实数据                                   |
| **第6天** | 写前端 Vue3 架子                  | 搭 Sidebar + Router + 页面空壳                                  |
| **第7天** | 前端对接 API                     | Axios 调后端接口，绑数据到 ECharts                                   |
| **第8天** | 联调 + bug 修复                  | 字段名不对、格式不对、跨域问题等                                           |
