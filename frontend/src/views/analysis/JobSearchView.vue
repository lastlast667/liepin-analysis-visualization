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
              <option value="10k以内">10K以下</option>
              <option value="10-20k">10-20K</option>
              <option value="20-30k">20-30K</option>
              <option value="30-50k">30-50K</option>
              <option value="50k以上">50K以上</option>
              <option value="薪资面议">薪资面议</option>
            </select>
          </div>
          <!-- 学历要求 -->
          <div>
            <label class="block text-sm text-gray-400 mb-2">学历要求</label>
            <select v-model="filters.education" class="glass-input w-full">
              <option value="">不限</option>
              <option value="大专">大专</option>
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
              <option value="实习生">实习</option>
              <option value="应届生">应届</option>
              <option value="1-3年">1-3年</option>
              <option value="3-5年">3-5年</option>
              <option value="5-10年">5-10年</option>
            </select>
          </div>
          <!-- 搜索按钮 + 重置按钮 -->
          <div class="flex gap-2">
            <button @click="searchJobs" class="btn-primary flex-1 flex items-center justify-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              搜索
            </button>
            <button @click="resetFilters" class="px-3 py-3 rounded-xl bg-dark-800 hover:bg-dark-700 text-gray-400 hover:text-gray-200 transition-all duration-300 border border-dark-600 hover:border-dark-500 flex items-center justify-center" title="重置筛选条件">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
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
            :total-count="jobTotal"
            :current-page="currentPage"
            :total-pages="jobTotalPages"
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
                  <p class="text-xs text-gray-500 truncate">{{ job.companyName }}</p>
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
                <span class="text-xs text-gray-500 flex-shrink-0">{{ company.count }}个岗位</span>
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
        :company-jobs="companyJobs"
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
import { reactive, ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import JobList from '@/components/job/JobList.vue'
import JobDetail from '@/components/job/JobDetail.vue'
import CompanyDetail from '@/components/job/CompanyDetail.vue'
import { analysisAPI, authAPI } from '@/api'

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
const favoriteMap = ref({})  // { jobId: favoriteRecordId }
const favoriteIds = computed(() => new Set(Object.keys(favoriteMap.value).map(Number)))

function isFavorited(jobId) {
  return jobId in favoriteMap.value
}

async function toggleFavorite(job) {
  if (isFavorited(job.id)) {
    await authAPI.removeFavorite(favoriteMap.value[job.id])
    const newMap = { ...favoriteMap.value }
    delete newMap[job.id]
    favoriteMap.value = newMap
  } else {
    const res = await authAPI.addFavorite({ job_id: job.id })
    favoriteMap.value = { ...favoriteMap.value, [job.id]: res.data.id }
  }
}

async function fetchFavoriteMap() {
  try {
    const res = await authAPI.getFavorites()
    const map = {}
    for (const fav of (res.data || [])) {
      map[fav.job.id] = fav.id
    }
    favoriteMap.value = map
  } catch (e) {
    console.error('加载收藏数据失败', e)
  }
}

/* ============================================================
 *   加载状态
 * ============================================================ */
const loading = ref(false)

/* ============================================================
 *   搜索列表 - API 数据
 * ============================================================ */
const jobResults = ref([])
const jobTotal = ref(0)
const jobTotalPages = ref(1)

/* 下拉选项（仅首次加载后赋值，多次搜索不覆盖） */
const cityOptions = ref([])

/* 右侧统计栏（仅首次加载后赋值，确保不受筛选影响） */
const hotJobs = ref([])
const hotCities = ref([])
const hotCompanies = ref([])

/* ============================================================
 *   详情页 - API 数据
 * ============================================================ */
const jobDetailCompanyStats = ref({ jobCount: 0, recruitTotal: 0, avgSalary: '--' })
const similarJobs = ref([])
const salaryAnalysis = ref({
  industryAvg: '--', abovePercentage: 0,
  rangeMin: '--', rangeMax: '--', positionPercentage: 50
})

/* ============================================================
 *   公司详情页 - API 数据
 * ============================================================ */
const companyJobs = ref([])
const companyDetailStats = ref({ jobCount: 0, recruitTotal: 0, avgSalary: '--' })

/* ============================================================
 *   computed - 翻页后的岗位列表（API 已分页，直接返回）
 * ============================================================ */
const paginatedJobs = computed(() => jobResults.value)

/* ============================================================
 *   API - 加载岗位搜索列表
 * ============================================================ */
async function loadJobs() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      sort_by: sortBy.value,
    }
    if (filters.keyword.trim()) params.keyword = filters.keyword.trim()
    if (filters.city) params.location_city = filters.city
    if (filters.salary) params.salary = filters.salary
    if (filters.education) params.education = filters.education
    if (filters.experience) params.experience_level = filters.experience

    const res = await analysisAPI.searchJobs(params)
    const data = res.data

    jobResults.value = data.results || []
    jobTotal.value = data.total || 0
    jobTotalPages.value = data.totalPages || 1

    /* 下拉选项 + 右侧统计栏：仅首次赋值，后续筛选不覆盖 */
    if (cityOptions.value.length === 0) {
      cityOptions.value = data.cityOptions || []
    }

    if (hotJobs.value.length === 0) {
      hotJobs.value = data.hotJobs || []
    }
    if (hotCities.value.length === 0) {
      hotCities.value = data.hotCities || []
    }
    if (hotCompanies.value.length === 0) {
      hotCompanies.value = data.hotCompanies || []
    }
  } catch (e) {
    console.error('加载岗位列表失败', e)
  } finally {
    loading.value = false
  }
}

/* ============================================================
 *   API - 加载岗位详情
 * ============================================================ */
async function loadJobDetail(jobId) {
  try {
    const res = await analysisAPI.getJobDetail(jobId)
    const data = res.data

    selectedJob.value = data

    /* 公司统计 */
    jobDetailCompanyStats.value = {
      jobCount: data.companyStats.jobCount || 0,
      recruitTotal: data.companyStats.recruitTotal || 0,
      avgSalary: data.companyStats.avgSalary
        ? (data.companyStats.avgSalary / 1000).toFixed(1) + 'k'
        : '--',
    }

    similarJobs.value = data.similarJobs || []

    /* 薪资分析 */
    const sa = data.salaryAnalysis || {}
    const rangeMin = sa.rangeMin || 0
    const rangeMax = sa.rangeMax || 0
    const currentSalary = data.monthSalaryAvg || 0
    const position = rangeMax > rangeMin
      ? ((currentSalary - rangeMin) / (rangeMax - rangeMin)) * 100
      : 50

    salaryAnalysis.value = {
      industryAvg: sa.industryAvg ? (sa.industryAvg / 1000).toFixed(1) + 'k' : '--',
      abovePercentage: sa.abovePercentage ?? 0,
      rangeMin: rangeMin ? (rangeMin / 1000).toFixed(0) + 'k' : '--',
      rangeMax: rangeMax ? (rangeMax / 1000).toFixed(0) + 'k' : '--',
      positionPercentage: Math.min(100, Math.max(0, position)),
    }
  } catch (e) {
    console.error('加载岗位详情失败', e)
  }
}

/* ============================================================
 *   API - 加载公司岗位列表（用于公司详情页）
 * ============================================================ */
async function loadCompanyJobs(companyName) {
  try {
    const res = await analysisAPI.searchJobs({
      company_name: companyName,
      page: 1,
      page_size: 200,
    })
    const jobs = res.data.results || []
    companyJobs.value = jobs

    const jc = jobs.length
    const rt = jobs.reduce((s, j) => s + (j.recruitCountParsed || 1), 0)
    const salaries = jobs.map(j => j.monthSalaryAvg).filter(Boolean)
    const avg = salaries.length > 0
      ? salaries.reduce((s, v) => s + v, 0) / salaries.length
      : 0
    companyDetailStats.value = {
      jobCount: jc,
      recruitTotal: rt,
      avgSalary: avg > 0 ? (avg / 1000).toFixed(1) + 'k' : '--',
    }
  } catch (e) {
    console.error('加载公司岗位列表失败', e)
  }
}

/* ============================================================
 *   方法 - 搜索触发
 * ============================================================ */
function searchJobs() {
  if (currentPage.value === 1) {
    loadJobs()
  } else {
    currentPage.value = 1
  }
}

/* ============================================================
 *   方法 - 重置筛选条件
 * ============================================================ */
function resetFilters() {
  filters.keyword = ''
  filters.city = ''
  filters.salary = ''
  filters.education = ''
  filters.experience = ''
  currentPage.value = 1
  loadJobs()
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
 *   goJobDetail:    列表 / 公司详情 → 岗位详情（先拉取 API）
 *   goCompanyDetail:列表 / 岗位详情 → 公司详情（先拉取 API）
 *   goSimilarJob:   详情页 → 另一岗位详情（视图不变）
 *   backToList:     岗位详情 / 公司详情 → 返回
 * ============================================================ */
async function goJobDetail(job) {
  await loadJobDetail(job.id)
  currentView.value = 'detail'
  // 记录浏览历史
  authAPI.recordBrowseHistory({ job_id: job.id }).catch(e => console.warn('记录浏览失败', e))
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function goCompanyDetail(companyName) {
  previousView.value = currentView.value
  selectedCompany.value = companyName
  await loadCompanyJobs(companyName)
  currentView.value = 'company'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function goSimilarJob(job) {
  await loadJobDetail(job.id)
  authAPI.recordBrowseHistory({ job_id: job.id }).catch(e => console.warn('记录浏览失败', e))
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function backToList() {
  if (currentView.value === 'company') {
    /* 公司详情页返回：回到进入公司前的视图（列表 或 岗位详情） */
    currentView.value = previousView.value
  } else {
    /* 岗位详情页返回：回到搜索列表 */
    currentView.value = 'list'
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

/* ============================================================
 *   监听排序和翻页变化，自动重新加载数据
 * ============================================================ */
watch(sortBy, () => {
  if (currentView.value === 'list') {
    searchJobs()
  }
})
watch(currentPage, () => {
  if (currentView.value === 'list') {
    loadJobs()
  }
})

/* ============================================================
 *   首次加载
 * ============================================================ */
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  loadJobs()
  fetchFavoriteMap()
  // 如果有 ?detail=xxx，自动打开详情
  const detailId = route.query.detail
  if (detailId) {
    try {
      const res = await analysisAPI.getJobDetail(detailId)
      selectedJob.value = res.data
      const d = res.data
      jobDetailCompanyStats.value = {
        jobCount: d.companyStats?.jobCount || 0,
        recruitTotal: d.companyStats?.recruitTotal || 0,
        avgSalary: d.companyStats?.avgSalary ? (d.companyStats.avgSalary / 1000).toFixed(1) + 'k' : '--',
      }
      similarJobs.value = d.similarJobs || []
      const sa = d.salaryAnalysis || {}
      const rMin = sa.rangeMin || 0
      const rMax = sa.rangeMax || 0
      const cur = d.monthSalaryAvg || 0
      salaryAnalysis.value = {
        industryAvg: sa.industryAvg ? (sa.industryAvg / 1000).toFixed(1) + 'k' : '--',
        abovePercentage: sa.abovePercentage ?? 0,
        rangeMin: rMin ? (rMin / 1000).toFixed(0) + 'k' : '--',
        rangeMax: rMax ? (rMax / 1000).toFixed(0) + 'k' : '--',
        positionPercentage: rMax > rMin ? Math.min(100, Math.max(0, ((cur - rMin) / (rMax - rMin)) * 100)) : 50,
      }
      currentView.value = 'detail'
      // 移除 URL 中的 ?detail= 参数
      router.replace('/analysis/jobs')
    } catch (e) {
      console.error('加载指定岗位详情失败', e)
    }
  }
})
</script>