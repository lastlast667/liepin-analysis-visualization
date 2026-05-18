# SimpleUI 后台管理系统配置需求

> 本文件定义 Django Admin + SimpleUI 美化后的后台管理系统配置要求，供 AI 生成配置代码时遵循。

---

## 一、SimpleUI 作用与选型理由

SimpleUI 是基于 Django Admin 的第三方主题库，不替换 Admin 本身的功能逻辑，仅通过覆盖模板和注入静态资源改变界面风格。选型理由：
- 零侵入：不改 Django Admin 的注册逻辑，仅通过 `settings.py` 和 `admin.py` 配置即可生效
- 开箱即用：内置菜单收起、表格分页、筛选器、弹窗编辑等交互，无需手写前端
- 适配移动端：后台可在手机浏览器访问
- 与 DRF 共存：后台管理走 Django Admin 视图，API 走 DRF 接口，互不干扰

---

## 二、安装与全局配置思路

### 2.1 依赖注册

在 `settings.py` 的 `INSTALLED_APPS` 中，`simpleui` 必须放在 `django.contrib.admin` 之前，确保模板加载优先级正确。

### 2.2 主题与品牌配置

通过 `SIMPLEUI_CONFIG` 字典控制：
- 系统名称：显示为后台左上角 Logo 文字
- Logo 图标：使用 Font Awesome 图标类名，或自定义图片 URL
- 主题模式：默认 `light`，可切换 `dark`
- 菜单收起：默认展开或收起侧边栏
- 首页模块：控制是否显示默认的“快速操作”和“最近动作”面板

### 2.3 语言与时区

后台界面语言跟随 Django 的 `LANGUAGE_CODE`（简体中文），时区跟随 `TIME_ZONE`（Asia/Shanghai），确保时间戳和日期选择器正确显示。

---

## 三、菜单结构定制（核心）

SimpleUI 的菜单默认按照 `INSTALLED_APPS` 的注册顺序和 `admin.py` 的注册模型自动生成。需要通过 `SIMPLEUI_CONFIG['menus']` 进行**完全自定义**，以满足项目功能需求。

### 3.1 一级菜单规划

后台侧边栏应包含以下一级菜单：

1. **仪表盘** — 系统数据总览（非模型菜单，指向自定义 Admin 视图或外链）
2. **用户中心** — 注册用户、用户资料、收藏记录、浏览历史
3. **岗位数据** — 所有爬取的招聘岗位记录
4. **数据分析** — 分析报告快照
5. **机器学习** — 模型元数据、训练任务触发
6. **爬虫中心** — 爬取任务状态、触发控制
7. **AI 客服** — 对话记录查询
8. **系统管理** — Django 自带的权限、组、日志（保留默认）

### 3.2 二级菜单与模型映射

每个一级菜单下的二级菜单应精确对应到各 App 的 Model：

**用户中心**
- 用户列表 → users.User（扩展的 Django 用户模型）
- 用户资料 → users.UserProfile
- 用户收藏 → users.Favorite
- 浏览历史 → users.BrowseHistory

**岗位数据**
- 岗位列表 → jobs.Job（全部字段可筛选、可搜索）
- 城市分布统计 → jobs.Job（通过自定义 Admin 视图展示聚合数据，或跳转前端页面）

**数据分析**
- 分析报告 → analysis.AnalysisReport

**机器学习**
- 模型列表 → ml_models.MLModel
- 薪资预测记录 → ml_models.SalaryPrediction

**爬虫中心**
- 爬虫任务日志 → spider.SpiderTask（或类似日志模型）
- 手动触发爬取 → 非模型菜单，指向自定义 Admin 视图（页面内放置“开始爬取”按钮，调用后端接口）

**AI 客服**
- 对话记录 → ai_chat.ChatMessage

**系统管理**
- 保留 Django 默认的“认证和授权”菜单：用户、组、权限

### 3.3 菜单图标配置

每个一级菜单应绑定 Font Awesome 图标，提升辨识度：
- 仪表盘：chart-line 或 tachometer-alt
- 用户中心：users
- 岗位数据：briefcase
- 数据分析：chart-bar
- 机器学习：brain 或 robot
- 爬虫中心：spider 或 bug（若无可用图标，使用通用的 server）
- AI 客服：comments
- 系统管理：cog

---

## 四、各 App 的 Admin 注册规范

### 4.1 jobs（岗位数据）

Job 模型是后台管理的核心数据，Admin 配置应支持：
- 列表页显示字段：title、company、city、category、salary_min、salary_max、is_active、created_at
- 列表页可筛选字段：category（下拉）、city（下拉）、education、experience
- 列表页可搜索字段：title、company、description（全文搜索）
- 列表页默认排序：-created_at（最新在前）
- 编辑页字段分组：基础信息（title/company/location）、薪资信息（salary_min/salary_max/salary_months）、分类标签（category/labels）、文本内容（description）、元信息（source_url/is_active）
- 只读字段：source_url、created_at、updated_at

### 4.2 users（用户中心）

- User：继承自 AbstractUser，Admin 注册时保持 Django 默认用户管理字段，补充 phone、avatar 显示
- UserProfile：一对一关联 User，Inline 嵌入 User 编辑页，或独立列表页显示 expected_city、skills、resume_text
- Favorite：外键关联 User 和 Job，列表页显示用户 + 岗位标题 + 收藏时间，可筛选用户
- BrowseHistory：外键关联 User 和 Job，列表页显示用户 + 岗位 + 浏览时间 + 停留时长，可筛选用户和日期

### 4.3 analysis（数据分析）

- AnalysisReport：JSONField 存储报告数据，列表页显示 report_type、generated_at，可筛选 report_type
- 编辑页 JSON 数据以格式化文本区域展示，方便管理员查看原始 JSON

### 4.4 ml_models（机器学习）

- MLModel：列表页显示 name、model_type、accuracy、f1_score、is_active、created_at，可筛选 model_type 和 is_active
- SalaryPrediction：列表页显示 user（可为空）、city、experience_years、predicted_min、predicted_max、created_at，可筛选 city

### 4.5 recommendation（岗位推荐）

若无独立 Admin 可展示模型（推荐结果通常实时计算），该 App 在 Admin 中可隐藏，或注册一个空的占位模型用于菜单挂载。推荐逻辑通过前端页面调用 DRF 接口实现，后台仅需查看用户行为数据（已在 users 中体现）。

### 4.6 resume_match（简历匹配）

同理，匹配结果实时计算，后台不强制要求独立菜单。如需调试，可在 Admin 中查看 users.UserProfile 的 resume_text 字段。

### 4.7 spider（爬虫中心）

- 若定义了 SpiderTask/SpiderLog 模型：列表页显示 task_name、status、started_at、completed_at、items_count，可筛选 status
- 若无持久化模型：通过自定义 Admin 视图（继承 AdminSite 或 TemplateView）在后台放置“爬虫控制台”页面，页面内提供“开始爬取”按钮，点击后向后端 DRF 接口（或 Admin 自定义 action）发送指令

### 4.8 ai_chat（AI 客服）

- ChatMessage：列表页显示 user、role、content（摘要前50字）、created_at，可筛选 user 和 role，可搜索 content
- content 字段较长，列表页显示摘要即可，编辑页显示完整内容

---

## 五、自定义 Admin 视图（仪表盘与爬虫控制台）

SimpleUI 支持在菜单中嵌入**非模型页面**（自定义视图），用于展示仪表盘或操作控制台。

### 5.1 仪表盘视图

在 Admin 中注册一个自定义视图，路径如 `/admin/dashboard/`：
- 页面内容：展示系统核心指标的聚合卡片（岗位总数、用户总数、今日新增岗位、平均薪资、活跃模型数）
- 数据来源：直接调用各 App 的 services 层或 ORM 聚合查询（Job.objects.count()、User.objects.count() 等）
- 样式：使用 SimpleUI 内置的卡片、表格、进度条样式，或嵌入 ECharts 图表（通过 Admin 模板注入 script 标签）
- 权限：仅超级管理员可见（staff 用户不可见）

### 5.2 爬虫控制台视图

在 Admin 中注册一个自定义视图，路径如 `/admin/spider-control/`：
- 页面内容：显示上次爬取时间、上次爬取数量、爬虫状态（空闲/运行中）
- 操作按钮："启动全量爬取"、"增量更新"，点击后通过 Ajax 调用后端 DRF 接口（POST /api/spider/trigger/）
- 结果反馈：按钮点击后显示任务 ID 或提示"任务已提交"
- 权限：仅超级管理员可操作

### 5.3 自定义视图的菜单挂载

自定义视图必须通过 `SIMPLEUI_CONFIG['menus']` 显式挂载到侧边栏，并指定 `url` 为 Admin 内部路径或外部链接。图标、名称、排序均可自定义。

---

## 六、权限控制

### 6.1 用户分级

- **超级管理员（superuser）**：拥有全部菜单和操作权限，包括爬虫控制台、模型训练、仪表盘
- **Staff 用户（is_staff=True, is_superuser=False）**：仅可查看岗位数据、用户中心（只读）、AI 客服记录、数据分析报告，**不可操作爬虫、不可修改模型状态、不可删除用户**

### 6.2 Admin 权限钩子

- 各 `admin.py` 中通过 `has_delete_permission`、`has_change_permission` 控制 Staff 用户的写权限
- 敏感操作（删除 Job、修改 MLModel 的 is_active）仅限超级管理员
- 自定义视图通过 `AdminSite` 或 `permission_required` 装饰器控制访问

---

## 七、列表页优化

### 7.1 分页与字段显示

- 所有数据量大的模型（Job、BrowseHistory、ChatMessage）默认分页 20 条/页
- 列表页字段不超过 7 列，避免横向滚动
- 长文本字段（description、content）在列表页显示前 30 字摘要，完整内容在编辑页查看

### 7.2 筛选器配置

- 高频筛选字段：category、city、education、experience、is_active
- 日期筛选：created_at 使用 DateRangeFilter 或 SimpleUI 内置日期筛选

### 7.3 搜索框

- Job：title、company、description
- ChatMessage：content
- User：username、email、phone

---

## 八、与前端 Vue3 的分工边界

- **后台管理系统（Django Admin + SimpleUI）**：供管理员查看全量数据、手动触发爬虫、查看对话记录、管理用户权限、查看分析报告快照
- **前台展示系统（Vue3）**：供普通用户搜索岗位、查看图表、使用 AI 客服、上传简历匹配、接收推荐
- **数据共享**：两者共用同一套 MySQL 数据库和 DRF API，Admin 中的数据修改会实时反映到前台

**后台不直接复用前端的 ECharts 仪表盘**：后台仪表盘使用 SimpleUI 内置卡片样式或独立注入图表脚本，保持 Admin 的自闭环。前台 Vue3 的图表页面不受 Admin 样式影响。

---

## 九、配置检查清单

- [ ] `simpleui` 在 `INSTALLED_APPS` 中位于 `django.contrib.admin` 之前
- [ ] `SIMPLEUI_CONFIG` 字典已定义，包含 brand、menus、theme 等关键项
- [ ] 所有 8 个 App 的模型已注册到 `admin.py`
- [ ] 自定义仪表盘视图已注册并挂载到菜单
- [ ] 自定义爬虫控制台视图已注册并挂载到菜单
- [ ] 各 `admin.py` 中已配置 list_display、list_filter、search_fields
- [ ] 敏感模型已限制 Staff 用户的删除/修改权限
- [ ] 后台语言为简体中文，时区为 Asia/Shanghai
- [ ] 静态文件收集命令（collectstatic）已执行，确保 SimpleUI 的 CSS/JS 生效
