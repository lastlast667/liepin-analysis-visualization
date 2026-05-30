<template>
  <div class="space-y-6 animate-fade-in">
    <!-- ==================== 视图一：搜索列表页 ==================== -->
    <template v-if="currentView === 'list'">
      <!-- 页面标题 -->
      <div>
        <h1 class="text-2xl font-bold text-gray-100">岗位搜索</h1>
        <p class="text-gray-500 mt-1">多条件精准搜索招聘岗位</p>
      </div>

      <!-- 搜索栏：五个筛选条件 + 搜索按钮，同一行 -->
      <div class="glass-card p-5">
        <div class="grid grid-cols-1 md:grid-cols-6 gap-4 items-end">
          <!-- 关键词 -->
          <div>
            <label class="block text-sm text-gray-400 mb-2">关键词</label>
            <input v-model="filters.keyword" type="text" class="glass-input w-full" placeholder="岗位名称/公司/技能关键词" @keyup.enter="searchJobs" />
          </div>
          <!-- 城市 -->
          <div>
            <label class="block text-sm text-gray-400 mb-2">城市</label>
            <select v-model="filters.city" class="glass-input w-full">
              <option value="">全国</option>
              <option v-for="c in cityOptions" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <!-- 薪资范围 -->
          <div>
            <label class="block text-sm text-gray-400 mb-2">薪资范围</label>
            <select v-model="filters.salary" class="glass-input w-full">
              <option value="">不限</option>
              <option value="0-10K">10K以下</option>
              <option value="10-20K">10K-20K</option>
              <option value="20-30K">20K-30K</option>
              <option value="30-50K">30K-50K</option>
              <option value="50K+">50K以上</option>
            </select>
          </div>
          <!-- 学历要求 -->
          <div>
            <label class="block text-sm text-gray-400 mb-2">学历要求</label>
            <select v-model="filters.education" class="glass-input w-full">
              <option value="">不限</option>
              <option value="专科">专科</option>
              <option value="本科">本科</option>
              <option value="统招本科">统招本科</option>
              <option value="硕士">硕士</option>
              <option value="博士">博士</option>
            </select>
          </div>
          <!-- 经验要求 -->
          <div>
            <label class="block text-sm text-gray-400 mb-2">经验要求</label>
            <select v-model="filters.experience" class="glass-input w-full">
              <option value="">不限</option>
              <option value="实习生">实习生</option>
              <option value="应届生">应届生</option>
              <option value="1-3年">1-3年</option>
              <option value="3-5年">3-5年</option>
              <option value="5-10年">5-10年</option>
            </select>
          </div>
          <!-- 搜索按钮 -->
          <div>
            <button @click="searchJobs" class="btn-primary w-full flex items-center justify-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              搜索
            </button>
          </div>
        </div>
      </div>

      <!-- 主内容区域：左侧 JobList + 右侧统计栏 -->
      <div class="flex gap-6">
        <!-- 左侧：可复用的岗位列表 -->
        <div class="flex-1 min-w-0">
          <!-- 使用 header-right 插槽传入排序下拉框 -->
          <JobList
            :jobs="paginatedJobs"
            :total-count="filteredJobList.length"
            :current-page="currentPage"
            :total-pages="totalPages"
            :favorite-ids="favoriteIds"
            @view-job="goJobDetail"
            @toggle-favorite="toggleFavorite"
            @page-change="currentPage = $event"
          >
            <template #header-right>
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500">排序：</span>
                <select v-model="sortBy" class="glass-input text-sm py-1.5">
                  <option value="default">综合排序</option>
                  <option value="salary">薪资水平</option>
                  <option value="experience">经验要求</option>
                  <option value="education">学历要求</option>
                </select>
              </div>
            </template>
          </JobList>
        </div>

        <!-- 右侧统计栏：三张不受筛选影响的卡片 -->
        <div class="w-80 flex-shrink-0 space-y-5">
          <!-- 热门岗位 Top5 -->
          <div class="glass-card p-5">
            <h3 class="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
              <svg class="w-4 h-4 text-orange-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
              </svg>
              热门岗位
            </h3>
            <div class="space-y-2.5">
              <div v-for="(job, idx) in hotJobs" :key="job.id"
                   class="flex items-start gap-2 text-sm group cursor-pointer hover:bg-dark-800/50 rounded-lg p-1.5 -mx-1.5 transition-colors">
                <span class="w-5 h-5 rounded flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5"
                      :class="idx === 0 ? 'bg-orange-500/20 text-orange-400' : idx === 1 ? 'bg-gray-500/20 text-gray-400' : idx === 2 ? 'bg-amber-700/20 text-amber-600' : 'bg-dark-700 text-gray-500'">
                  {{ idx + 1 }}
                </span>
                <div class="min-w-0 flex-1">
                  <p @click="goJobDetail(job)" class="text-gray-300 group-hover:text-primary-400 transition-colors truncate cursor-pointer">{{ job.title }}</p>
                  <p class="text-xs text-gray-500 truncate">{{ job.company_name }}</p>
                </div>
                <span class="text-xs text-primary-400 font-medium flex-shrink-0">{{ job.salary }}</span>
              </div>
            </div>
          </div>

          <!-- 热门城市 Top10 -->
          <div class="glass-card p-5">
            <h3 class="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
              <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              热门城市
            </h3>
            <div class="flex flex-wrap gap-2">
              <button v-for="c in hotCities" :key="c.name"
                      @click="selectCity(c.name)"
                      class="px-2.5 py-1 rounded-lg text-xs transition-all duration-300"
                      :class="filters.city === c.name ? 'bg-primary-600/30 text-primary-400 border border-primary-500/40' : 'bg-dark-800 text-gray-400 hover:text-gray-200 hover:bg-dark-700 border border-dark-600'">
                {{ c.name }}（{{ c.count }}）
              </button>
            </div>
          </div>

          <!-- 热门公司 Top5 -->
          <div class="glass-card p-5">
            <h3 class="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
              <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              热门公司
            </h3>
            <div class="space-y-2.5">
              <div v-for="(company, idx) in hotCompanies" :key="company.name"
                   class="flex items-center justify-between text-sm group cursor-pointer hover:bg-dark-800/50 rounded-lg p-1.5 -mx-1.5 transition-colors"
                   @click="goCompanyDetail(company.name)">
                <div class="flex items-center gap-2 min-w-0">
                  <span class="w-5 h-5 rounded flex items-center justify-center text-xs font-bold flex-shrink-0"
                        :class="idx === 0 ? 'bg-purple-500/20 text-purple-400' : idx === 1 ? 'bg-gray-500/20 text-gray-400' : idx === 2 ? 'bg-amber-700/20 text-amber-600' : 'bg-dark-700 text-gray-500'">
                    {{ idx + 1 }}
                  </span>
                  <span class="text-gray-300 group-hover:text-primary-400 transition-colors truncate">{{ company.name }}</span>
                </div>
                <span class="text-xs text-gray-500 flex-shrink-0">{{ company.jobCount }}个岗位</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ==================== 视图二：岗位详情页 ==================== -->
    <template v-else-if="currentView === 'detail' && selectedJob">
      <!-- 返回按钮 -->
      <div>
        <button @click="backToList" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-primary-400 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回搜索结果
        </button>
      </div>

      <!-- 岗位详情组件 -->
      <JobDetail
        :job="selectedJob"
        :company-stats="jobDetailCompanyStats"
        :similar-jobs="similarJobs"
        :salary-analysis="salaryAnalysis"
        :is-favorited="isFavorited(selectedJob.id)"
        @view-company="goCompanyDetail"
        @toggle-favorite="toggleFavorite"
        @view-similar="goSimilarJob"
      />
    </template>

    <!-- ==================== 视图三：公司详情页 ==================== -->
    <template v-else-if="currentView === 'company' && selectedCompany">
      <!-- 返回按钮 -->
      <div>
        <button @click="backToList" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-primary-400 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ previousView === 'detail' ? '返回岗位详情' : '返回搜索结果' }}
        </button>
      </div>

      <!-- 公司详情组件 -->
      <CompanyDetail
        :company-name="selectedCompany"
        :company-jobs="companyJobsList"
        :company-stats="companyDetailStats"
        :favorite-ids="favoriteIds"
        @view-job="goJobDetail"
        @toggle-favorite="toggleFavorite"
        @back="backToList"
      />
    </template>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import JobList from '@/components/job/JobList.vue'
import JobDetail from '@/components/job/JobDetail.vue'
import CompanyDetail from '@/components/job/CompanyDetail.vue'

/* ============================================================
 *   视图与导航状态（父组件统一控制）
 *   currentView: 'list' | 'detail' | 'company'
 *   previousView: 记录进入 company 前的视图，用于正确返回
 * ============================================================ */
const currentView = ref('list')
const previousView = ref('list')
const selectedJob = ref(null)
const selectedCompany = ref('')

/* ============================================================
 *   筛选条件
 * ============================================================ */
const filters = reactive({
  keyword: '',
  city: '',
  salary: '',
  education: '',
  experience: '',
})

/* ============================================================
 *   排序与翻页
 * ============================================================ */
const sortBy = ref('default')
const currentPage = ref(1)
const pageSize = 10

/* ============================================================
 *   收藏列表
 * ============================================================ */
const favoriteIds = ref(new Set())

/* ============================================================
 *   父组件统一存储全部 mock 数据
 * ============================================================ */
const allJobsData = ref([
  {
    id: 1, title: '高级Java开发工程师', company_name: '字节跳动', salary: '35K-60K',
    location_city: '北京', education: '本科', experience: '5-10年', experience_level: '5-10年',
    recruit_count: '5', recruit_count_parsed: 5, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 47500,
    company_tags: ['六险一金', '弹性工作', '免费三餐', '房补'], update_time: '2小时前',
    job_description: '负责字节跳动核心业务系统的后端架构设计与开发；参与高并发分布式系统的性能优化；指导初中级工程师进行代码评审与技术方案设计；推动团队技术栈升级与最佳实践落地。',
    language_requirement: '英语读写能力良好', has_weekend_off: false,
    job_url: 'https://www.liepin.com/job/example1',
  },
  {
    id: 2, title: 'Python后端开发工程师', company_name: '阿里巴巴', salary: '25K-45K',
    location_city: '杭州', education: '本科', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '3', recruit_count_parsed: 3, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 35000,
    company_tags: ['五险一金', '年终奖金', '定期体检', '带薪年假'], update_time: '3小时前',
    job_description: '参与阿里云大数据平台的后端服务开发；负责数据处理管线的设计与实现；与数据科学家协作，将算法模型工程化落地；持续优化系统性能与稳定性。',
    language_requirement: '', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example2',
  },
  {
    id: 3, title: 'Go开发工程师', company_name: '腾讯科技', salary: '30K-50K',
    location_city: '深圳', education: '本科', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '2', recruit_count_parsed: 2, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 40000,
    company_tags: ['六险一金', '股票期权', '弹性工作制', '免费班车'], update_time: '5小时前',
    job_description: '负责腾讯云微服务平台的Go语言后端开发；设计并实现高性能API网关与中间件；参与云原生技术栈的选型与落地；编写技术文档并进行内部技术分享。',
    language_requirement: 'CET-6及以上', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example3',
  },
  {
    id: 4, title: 'C++开发工程师（搜索方向）', company_name: '百度', salary: '28K-45K',
    location_city: '北京', education: '硕士', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '4', recruit_count_parsed: 4, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 36500,
    company_tags: ['五险一金', '补充医疗', '弹性工作'], update_time: '6小时前',
    job_description: '参与百度搜索核心引擎的研发与优化；负责大规模索引构建与检索排序算法的实现；优化搜索引擎的响应延迟与吞吐量；与算法团队协作推进搜索质量提升。',
    language_requirement: '', has_weekend_off: false,
    job_url: 'https://www.liepin.com/job/example4',
  },
  {
    id: 5, title: '前端架构师', company_name: '美团', salary: '40K-65K',
    location_city: '北京', education: '本科', experience: '5-10年', experience_level: '5-10年',
    recruit_count: '1', recruit_count_parsed: 1, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 52500,
    company_tags: ['期权激励', '弹性工作', '技术氛围好', 'Mac办公'], update_time: '8小时前',
    job_description: '负责美团到店事业群前端架构设计与技术规划；推动微前端、组件化等前沿技术落地；制定前端编码规范与工程质量标准；带领前端团队进行技术攻坚。',
    language_requirement: '', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example5',
  },
  {
    id: 6, title: 'Python数据分析师', company_name: '蚂蚁集团', salary: '20K-35K',
    location_city: '杭州', education: '本科', experience: '1-3年', experience_level: '1-3年',
    recruit_count: '2', recruit_count_parsed: 2, company_industry: '云计算/大数据',
    company_scale: '10000人以上', month_salary_avg: 27500,
    company_tags: ['五险一金', '年终奖', '技术氛围好'], update_time: '10小时前',
    job_description: '负责支付业务数据分析与挖掘；构建用户行为画像与风险模型；通过数据驱动业务决策与产品优化；编写数据分析报告并向上汇报。',
    language_requirement: '', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example6',
  },
  {
    id: 7, title: 'Java开发（中间件方向）', company_name: '华为', salary: '30K-55K',
    location_city: '深圳', education: '本科', experience: '5-10年', experience_level: '5-10年',
    recruit_count: '6', recruit_count_parsed: 6, company_industry: 'IT服务',
    company_scale: '10000人以上', month_salary_avg: 42500,
    company_tags: ['五险一金', '补充公积金', '年终分红', '技术培训'], update_time: '12小时前',
    job_description: '负责华为云中间件产品的设计与研发；参与消息队列、分布式缓存等核心组件的性能优化；解决大规模分布式系统中的技术难题；参与开源社区贡献。',
    language_requirement: '英语流利', has_weekend_off: false,
    job_url: 'https://www.liepin.com/job/example7',
  },
  {
    id: 8, title: 'Go开发（微服务方向）', company_name: '字节跳动', salary: '35K-60K',
    location_city: '上海', education: '本科', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '3', recruit_count_parsed: 3, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 47500,
    company_tags: ['六险一金', '弹性工作', '免费三餐', '健身房'], update_time: '1天前',
    job_description: '负责字节跳动电商业务微服务架构的Go语言开发；设计高可用、高并发的分布式系统；参与服务治理、链路追踪等基础设施的建设；推动技术最佳实践的落地。',
    language_requirement: '', has_weekend_off: false,
    job_url: 'https://www.liepin.com/job/example8',
  },
  {
    id: 9, title: '全栈开发工程师', company_name: '滴滴出行', salary: '22K-38K',
    location_city: '北京', education: '本科', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '2', recruit_count_parsed: 2, company_industry: '互联网',
    company_scale: '5000-10000人', month_salary_avg: 30000,
    company_tags: ['五险一金', '补充医疗', '弹性工作'], update_time: '1天前',
    job_description: '参与滴滴出行运营管理平台的全栈开发；负责前后端技术方案设计与实现；与产品和运营团队紧密协作，快速迭代业务需求；持续优化系统性能和用户体验。',
    language_requirement: '', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example9',
  },
  {
    id: 10, title: '算法工程师（NLP方向）', company_name: '科大讯飞', salary: '30K-55K',
    location_city: '合肥', education: '硕士', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '3', recruit_count_parsed: 3, company_industry: '人工智能',
    company_scale: '5000-10000人', month_salary_avg: 42500,
    company_tags: ['五险一金', '人才公寓', '项目奖金', '学术氛围'], update_time: '1天前',
    job_description: '负责自然语言处理相关算法的研发与优化；参与大语言模型的训练、微调与部署；探索NLP技术在语音交互场景中的落地应用；撰写专利与学术论文。',
    language_requirement: '英语六级', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example10',
  },
  {
    id: 11, title: '运维开发工程师', company_name: '网易', salary: '20K-35K',
    location_city: '广州', education: '本科', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '2', recruit_count_parsed: 2, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 27500,
    company_tags: ['五险一金', '免费三餐', '健身房'], update_time: '2天前',
    job_description: '负责网易游戏运维平台的开发与维护；构建自动化运维工具链与监控体系；推动容器化与CI/CD流水线的建设；参与线上故障的排查与应急响应。',
    language_requirement: '', has_weekend_off: false,
    job_url: 'https://www.liepin.com/job/example11',
  },
  {
    id: 12, title: '嵌入式软件开发工程师', company_name: '大疆创新', salary: '25K-45K',
    location_city: '深圳', education: '本科', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '4', recruit_count_parsed: 4, company_industry: '人工智能',
    company_scale: '5000-10000人', month_salary_avg: 35000,
    company_tags: ['五险一金', '年终奖金', '创新氛围', '产品折扣'], update_time: '2天前',
    job_description: '负责无人机嵌入式系统的软件开发与调试；参与飞控算法在嵌入式平台上的优化实现；解决实时操作系统中的性能与稳定性问题；编写技术设计文档。',
    language_requirement: '', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example12',
  },
  {
    id: 13, title: '测试开发工程师', company_name: '拼多多', salary: '25K-40K',
    location_city: '上海', education: '本科', experience: '1-3年', experience_level: '1-3年',
    recruit_count: '3', recruit_count_parsed: 3, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 32500,
    company_tags: ['五险一金', '股票期权', '弹性工作'], update_time: '2天前',
    job_description: '负责电商平台的质量保障体系建设；开发自动化测试框架与工具；参与持续集成流水线的设计与维护；推动测试左移与质量内建的最佳实践。',
    language_requirement: '', has_weekend_off: false,
    job_url: 'https://www.liepin.com/job/example13',
  },
  {
    id: 14, title: 'Java开发（支付方向）', company_name: '蚂蚁集团', salary: '28K-50K',
    location_city: '杭州', education: '本科', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '5', recruit_count_parsed: 5, company_industry: '云计算/大数据',
    company_scale: '10000人以上', month_salary_avg: 39000,
    company_tags: ['五险一金', '期权激励', '弹性工作'], update_time: '3天前',
    job_description: '参与支付宝核心支付链路的开发与维护；负责高并发交易系统的架构设计与性能优化；保障支付系统的稳定性与资金安全；参与技术方案评审与代码审查。',
    language_requirement: '', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example14',
  },
  {
    id: 15, title: '前端开发工程师', company_name: '小红书', salary: '18K-30K',
    location_city: '上海', education: '本科', experience: '1-3年', experience_level: '1-3年',
    recruit_count: '2', recruit_count_parsed: 2, company_industry: '在线社交/媒体',
    company_scale: '2000-5000人', month_salary_avg: 24000,
    company_tags: ['五险一金', '零食下午茶', '弹性工作'], update_time: '3天前',
    job_description: '负责小红书社区前端页面的开发与迭代；参与组件库建设与前端工程化优化；与设计师协作，还原高保真UI界面；关注页面性能与用户体验指标。',
    language_requirement: '', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example15',
  },
  {
    id: 16, title: '数据开发工程师', company_name: '京东', salary: '22K-38K',
    location_city: '北京', education: '本科', experience: '1-3年', experience_level: '1-3年',
    recruit_count: '3', recruit_count_parsed: 3, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 30000,
    company_tags: ['五险一金', '年终奖金', '免费班车'], update_time: '3天前',
    job_description: '负责京东物流数据仓库的建设与维护；开发ETL数据 pipeline，保障数据质量与时效性；构建数据指标体系与可视化看板；支持业务部门的数据分析需求。',
    language_requirement: '', has_weekend_off: false,
    job_url: 'https://www.liepin.com/job/example16',
  },
  {
    id: 17, title: '安全开发工程师', company_name: '奇安信', salary: '25K-45K',
    location_city: '北京', education: '本科', experience: '3-5年', experience_level: '3-5年',
    recruit_count: '2', recruit_count_parsed: 2, company_industry: 'IT服务',
    company_scale: '5000-10000人', month_salary_avg: 35000,
    company_tags: ['五险一金', '技术培训', '行业影响力'], update_time: '4天前',
    job_description: '负责网络安全产品的研发与维护；参与安全检测引擎的优化与规则编写；研究最新安全威胁与攻防技术；编写安全技术方案与产品文档。',
    language_requirement: '英语读写', has_weekend_off: true,
    job_url: 'https://www.liepin.com/job/example17',
  },
  {
    id: 18, title: '实习生-后端开发', company_name: '字节跳动', salary: '8K-12K',
    location_city: '北京', education: '本科', experience: '应届', experience_level: '应届生',
    recruit_count: '10', recruit_count_parsed: 10, company_industry: '互联网',
    company_scale: '10000人以上', month_salary_avg: 10000,
    company_tags: ['导师制', '转正机会', '免费三餐', '技术成长'], update_time: '5天前',
    job_description: '在导师带领下参与字节跳动业务系统的后端开发；学习并实践分布式系统、微服务架构等技术；参与代码评审与技术讨论；完成分配的开发任务并撰写技术文档。',
    language_requirement: '', has_weekend_off: false,
    job_url: 'https://www.liepin.com/job/example18',
  },
])

/* ============================================================
 *   computed - 城市下拉选项
 * ============================================================ */
const cityOptions = computed(() => {
  const cities = [...new Set(allJobsData.value.map(j => j.location_city))]
  return cities.sort()
})

/* ============================================================
 *   computed - 筛选 + 排序后的岗位列表
 * ============================================================ */
const filteredJobList = computed(() => {
  let result = [...allJobsData.value]

  if (filters.keyword.trim()) {
    const kw = filters.keyword.trim().toLowerCase()
    result = result.filter(j =>
      j.title.toLowerCase().includes(kw) ||
      j.company_name.toLowerCase().includes(kw) ||
      (j.company_tags && j.company_tags.some(t => t.toLowerCase().includes(kw)))
    )
  }
  if (filters.city) {
    result = result.filter(j => j.location_city === filters.city)
  }
  if (filters.salary) {
    result = result.filter(j => {
      const avg = j.month_salary_avg
      switch (filters.salary) {
        case '0-10K': return avg < 10000
        case '10-20K': return avg >= 10000 && avg < 20000
        case '20-30K': return avg >= 20000 && avg < 30000
        case '30-50K': return avg >= 30000 && avg < 50000
        case '50K+': return avg >= 50000
        default: return true
      }
    })
  }
  if (filters.education) {
    result = result.filter(j => j.education === filters.education)
  }
  if (filters.experience) {
    result = result.filter(j => j.experience_level === filters.experience)
  }

  switch (sortBy.value) {
    case 'salary':
      result.sort((a, b) => (b.month_salary_avg || 0) - (a.month_salary_avg || 0))
      break
    case 'experience': {
      const expOrder = ['应届生', '实习生', '1-3年', '3-5年', '5-10年']
      result.sort((a, b) => {
        const ia = expOrder.indexOf(a.experience_level)
        const ib = expOrder.indexOf(b.experience_level)
        return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib)
      })
      break
    }
    case 'education': {
      const eduOrder = ['博士', '硕士', '统招本科', '本科', '专科', '学历不限']
      result.sort((a, b) => {
        const ia = eduOrder.indexOf(a.education)
        const ib = eduOrder.indexOf(b.education)
        return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib)
      })
      break
    }
    default: break
  }
  return result
})

/* ============================================================
 *   computed - 翻页
 * ============================================================ */
const totalPages = computed(() => Math.max(1, Math.ceil(filteredJobList.value.length / pageSize)))

const paginatedJobs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredJobList.value.slice(start, start + pageSize)
})

/* ============================================================
 *   右侧统计栏 - 热门岗位 Top5（不受筛选影响）
 * ============================================================ */
const hotJobs = computed(() => {
  return [...allJobsData.value]
    .sort((a, b) => (b.month_salary_avg || 0) - (a.month_salary_avg || 0))
    .slice(0, 5)
})

/* ============================================================
 *   右侧统计栏 - 热门城市 Top10（不受筛选影响）
 * ============================================================ */
const hotCities = computed(() => {
  const cityCount = {}
  allJobsData.value.forEach(j => {
    cityCount[j.location_city] = (cityCount[j.location_city] || 0) + 1
  })
  return Object.entries(cityCount)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
})

/* ============================================================
 *   右侧统计栏 - 热门公司 Top5（不受筛选影响）
 * ============================================================ */
const hotCompanies = computed(() => {
  const companyCount = {}
  allJobsData.value.forEach(j => {
    companyCount[j.company_name] = (companyCount[j.company_name] || 0) + 1
  })
  return Object.entries(companyCount)
    .map(([name, count]) => ({ name, jobCount: count }))
    .sort((a, b) => b.jobCount - a.jobCount)
    .slice(0, 5)
})

/* ============================================================
 *   详情页 - 公司统计数据（基于 selectedJob 的公司名称）
 * ============================================================ */
const jobDetailCompanyStats = computed(() => {
  if (!selectedJob.value) return { jobCount: 0, recruitTotal: 0, avgSalary: '--' }
  const companyJobs = allJobsData.value.filter(j => j.company_name === selectedJob.value.company_name)
  const jobCount = companyJobs.length
  const recruitTotal = companyJobs.reduce((sum, j) => sum + (j.recruit_count_parsed || 1), 0)
  const avg = jobCount > 0
    ? companyJobs.reduce((sum, j) => sum + (j.month_salary_avg || 0), 0) / jobCount
    : 0
  return {
    jobCount,
    recruitTotal,
    avgSalary: avg > 0 ? (avg / 1000).toFixed(1) + 'k' : '--',
  }
})

/* ============================================================
 *   详情页 - 相似岗位推荐（同行业 Top3）
 * ============================================================ */
const similarJobs = computed(() => {
  if (!selectedJob.value) return []
  return allJobsData.value
    .filter(j => j.id !== selectedJob.value.id && j.company_industry === selectedJob.value.company_industry)
    .slice(0, 3)
})

/* ============================================================
 *   详情页 - 薪资分析
 * ============================================================ */
const salaryAnalysis = computed(() => {
  if (!selectedJob.value) {
    return { industryAvg: '--', abovePercentage: 0, rangeMin: '--', rangeMax: '--', positionPercentage: 50 }
  }
  const industryJobs = allJobsData.value.filter(j => j.company_industry === selectedJob.value.company_industry)
  const industryAvg = industryJobs.length > 0
    ? industryJobs.reduce((sum, j) => sum + (j.month_salary_avg || 0), 0) / industryJobs.length
    : selectedJob.value.month_salary_avg || 0
  const currentSalary = selectedJob.value.month_salary_avg || 0
  const abovePercentage = industryAvg > 0 ? Math.round((currentSalary - industryAvg) / industryAvg * 100) : 0
  const salaries = industryJobs.map(j => j.month_salary_avg).filter(Boolean)
  const rangeMin = salaries.length > 0 ? Math.min(...salaries) : 0
  const rangeMax = salaries.length > 0 ? Math.max(...salaries) : 0
  const positionPercentage = rangeMax > rangeMin ? ((currentSalary - rangeMin) / (rangeMax - rangeMin)) * 100 : 50
  return {
    industryAvg: (industryAvg / 1000).toFixed(1) + 'k',
    abovePercentage,
    rangeMin: (rangeMin / 1000).toFixed(0) + 'k',
    rangeMax: (rangeMax / 1000).toFixed(0) + 'k',
    positionPercentage: Math.min(100, Math.max(0, positionPercentage)),
  }
})

/* ============================================================
 *   公司详情页 - 该公司所有岗位列表
 * ============================================================ */
const companyJobsList = computed(() => {
  if (!selectedCompany.value) return []
  return allJobsData.value.filter(j => j.company_name === selectedCompany.value)
})

/* ============================================================
 *   公司详情页 - 该公司统计数据
 * ============================================================ */
const companyDetailStats = computed(() => {
  const jobs = companyJobsList.value
  const jobCount = jobs.length
  const recruitTotal = jobs.reduce((sum, j) => sum + (j.recruit_count_parsed || 1), 0)
  const avg = jobCount > 0
    ? jobs.reduce((sum, j) => sum + (j.month_salary_avg || 0), 0) / jobCount
    : 0
  return {
    jobCount,
    recruitTotal,
    avgSalary: avg > 0 ? (avg / 1000).toFixed(1) + 'k' : '--',
  }
})

/* ============================================================
 *   方法 - 搜索触发
 * ============================================================ */
function searchJobs() {
  currentPage.value = 1
}

/* ============================================================
 *   方法 - 收藏功能
 * ============================================================ */
function toggleFavorite(job) {
  if (favoriteIds.value.has(job.id)) {
    favoriteIds.value.delete(job.id)
  } else {
    favoriteIds.value.add(job.id)
  }
  favoriteIds.value = new Set(favoriteIds.value)
}

function isFavorited(jobId) {
  return favoriteIds.value.has(jobId)
}

/* ============================================================
 *   方法 - 城市快速筛选
 * ============================================================ */
function selectCity(cityName) {
  if (filters.city === cityName) {
    filters.city = ''
  } else {
    filters.city = cityName
  }
  searchJobs()
}

/* ============================================================
 *   方法 - 视图跳转（父组件统一控制）
 *   goJobDetail:    列表 / 公司详情 → 岗位详情
 *   goCompanyDetail:列表 / 岗位详情 → 公司详情（记录上一视图）
 *   goSimilarJob:   详情页 → 另一岗位详情（视图不变）
 *   backToList:     岗位详情 / 公司详情 → 返回
 * ============================================================ */
function goJobDetail(job) {
  selectedJob.value = job
  currentView.value = 'detail'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goCompanyDetail(companyName) {
  previousView.value = currentView.value
  selectedCompany.value = companyName
  currentView.value = 'company'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goSimilarJob(job) {
  selectedJob.value = job
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function backToList() {
  if (currentView.value === 'company') {
    // 公司详情页返回：回到进入公司前的视图（列表 或 岗位详情）
    currentView.value = previousView.value
  } else {
    // 岗位详情页返回：回到搜索列表
    currentView.value = 'list'
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>