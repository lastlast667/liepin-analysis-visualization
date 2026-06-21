<template>
  <div class="space-y-6 animate-fade-in">
    <!-- ==================== 视图一：推荐列表 ==================== -->
    <template v-if="currentView === 'list'">
      <!-- 页面标题 -->
      <div>
        <h1 class="text-2xl font-bold text-gray-100">岗位推荐</h1>
        <p class="text-gray-500 mt-1">基于你的行为和画像，智能推荐适合你的岗位</p>
      </div>

      <!-- 推荐策略卡片 -->
      <div class="glass-card p-5">
        <div class="flex items-center justify-between gap-6">
          <!-- 左侧：策略描述 -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 rounded-xl bg-primary-500/10 flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h3 class="text-base font-semibold text-gray-200">{{ strategyLabel }}</h3>
                <p class="text-sm text-gray-500">{{ strategyDescription }}</p>
              </div>
            </div>
          </div>
          <!-- 右侧：数量下拉 + 策略按钮 -->
          <div class="flex items-center gap-3 flex-shrink-0">
            <!-- 数量下拉 -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500 whitespace-nowrap">显示数量：</span>
              <select v-model="topK" @change="fetchRecommendations"
                      class="glass-input w-20 text-sm px-3 py-2 rounded-xl bg-dark-800 border border-dark-600 text-gray-300">
                <option :value="8">8</option>
                <option :value="12">12</option>
                <option :value="16">16</option>
              </select>
            </div>
            <!-- 策略按钮 -->
            <button v-for="s in strategies" :key="s.key"
                    @click="switchStrategy(s.key)"
                    class="px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 whitespace-nowrap"
                    :class="strategy === s.key
                      ? 'bg-primary-600 text-white shadow-lg shadow-primary-500/25'
                      : 'bg-dark-800 text-gray-400 hover:text-gray-200 border border-dark-600 hover:border-primary-500/30'">
              {{ s.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- 岗位列表卡片 -->
      <div class="glass-card">
        <!-- 头部 -->
        <div class="p-4 border-b border-dark-700/50 flex items-center justify-between">
          <span class="text-sm text-gray-400">
            <span v-if="loading">加载中...</span>
            <span v-else>
              找到 <span class="text-primary-400 font-semibold">{{ recommendations.length }}</span> 个推荐岗位
            </span>
          </span>
        </div>

        <!-- 加载中 -->
        <div v-if="loading" class="p-12 text-center text-gray-500">
          <svg class="w-8 h-8 mx-auto mb-3 animate-spin text-primary-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          正在为你生成推荐...
        </div>

        <!-- 空状态 -->
        <div v-else-if="recommendations.length === 0" class="p-12 text-center text-gray-500">
          <svg class="w-12 h-12 mx-auto mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          暂无推荐结果，先去浏览一些岗位吧
        </div>

        <!-- 4列网格 -->
        <div v-else class="p-5">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div v-for="job in recommendations" :key="job.id"
                 @click="goJobDetail(job)"
                 class="glass-card p-4 hover:border-primary-500/40 transition-all duration-300 cursor-pointer group hover:-translate-y-0.5 hover:shadow-lg">
              <div class="flex items-start justify-between gap-2">
                <div class="flex-1 min-w-0">
                  <!-- 岗位标题 + 行业标签 -->
                  <div class="flex items-center gap-2 mb-1">
                    <h3 class="text-sm font-semibold text-gray-200 group-hover:text-primary-400 transition-colors truncate">
                      {{ job.title }}
                    </h3>
                    <span v-if="job.companyIndustry" class="px-1.5 py-0.5 rounded text-[10px] bg-dark-700 text-gray-400 flex-shrink-0 leading-tight">{{ job.companyIndustry }}</span>
                  </div>
                  <!-- 公司名 · 城市 -->
                  <p class="text-xs text-gray-500 mb-2 truncate">{{ job.companyName }} · {{ job.locationCity }}</p>
                  <!-- 薪资 / 经验 / 学历 -->
                  <div class="flex items-center gap-2 text-[10px] text-gray-500 flex-wrap">
                    <span class="flex items-center gap-0.5 text-primary-400 font-medium text-xs">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ job.salary }}
                    </span>
                    <span v-if="job.experience">· {{ job.experience }}</span>
                    <span v-if="job.education">· {{ job.education }}</span>
                    <span v-if="job.recruitCount">· {{ job.recruitCount }}</span>
                  </div>
                </div>
                <!-- 匹配度 -->
                <div v-if="job.matchScore != null" class="text-center shrink-0">
                  <div class="w-12 h-12 rounded-full bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center">
                    <span class="text-sm font-bold text-white">{{ job.matchScore }}</span>
                  </div>
                  <span class="text-[10px] text-gray-500 mt-0.5 block leading-tight">匹配</span>
                </div>
                <!-- 收藏按钮 -->
                <button v-if="job.matchScore == null" @click.stop="toggleFavorite(job)"
                        class="p-1.5 rounded-lg hover:bg-dark-700 transition-all flex-shrink-0 self-start mt-0.5"
                        :class="isFavorited(job.id) ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400 opacity-0 group-hover:opacity-100'">
                  <svg class="w-4 h-4" :fill="isFavorited(job.id) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ==================== 视图二：岗位详情 ==================== -->
    <template v-else-if="currentView === 'detail' && selectedJob">
      <div>
        <button @click="backToList" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-primary-400 transition-colors mb-4">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回推荐列表
        </button>
      </div>
      <JobDetail
        :job="selectedJob"
        :company-stats="jobDetailCompanyStats"
        :similar-jobs="similarJobs"
        :salary-analysis="salaryAnalysis"
        :is-favorited="isFavorited(selectedJob.id)"
        @view-company="goCompanyDetail"
        @toggle-favorite="toggleFavorite"
      />
    </template>

    <!-- ==================== 视图三：公司详情 ==================== -->
    <template v-else-if="currentView === 'company'">
      <div>
        <button @click="backToList" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-primary-400 transition-colors mb-4">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回推荐列表
        </button>
      </div>
      <CompanyDetail
        :company-name="companyName"
        :company-jobs="companyJobs"
        :company-stats="companyDetailStats"
        :favorite-ids="favoriteIds"
        @view-job="goJobDetail"
        @toggle-favorite="toggleFavorite"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mlAPI, authAPI, analysisAPI } from '@/api'
import JobDetail from '@/components/job/JobDetail.vue'
import CompanyDetail from '@/components/job/CompanyDetail.vue'

/* ============================================================
 *   推荐策略配置
 * ============================================================ */
const strategies = [
  { key: 'hybrid', label: '混合推荐' },
  { key: 'svd', label: '协同过滤' },
  { key: 'content', label: '内容推荐' },
]

const strategyLabels = {
  svd: '协同过滤',
  content: '内容推荐',
  hybrid: '混合推荐',
}

const strategyDescriptions = {
  svd: '基于矩阵分解的协同过滤，分析你的浏览和收藏行为，挖掘潜在偏好岗位',
  content: '基于你的期望城市和岗位类别，匹配岗位内容特征，推荐与你画像相符的职位',
  hybrid: '综合 SVD(60%) 与内容推荐(40%) 的混合策略，兼顾个性化探索与精准匹配',
}

const strategy = ref('hybrid')
const topK = ref(12)

const strategyLabel = computed(() => strategyLabels[strategy.value])
const strategyDescription = computed(() => strategyDescriptions[strategy.value])

/* ============================================================
 *   视图控制
 * ============================================================ */
const currentView = ref('list')
const selectedJob = ref(null)
const companyName = ref('')

function goJobDetail(job) {
  loadJobDetail(job.id)
  // 记录浏览历史
  authAPI.recordBrowseHistory({ job_id: job.id }).catch(e => console.warn('记录浏览失败', e))
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function backToList() {
  if (currentView.value === 'company') {
    currentView.value = 'detail'
  } else {
    currentView.value = 'list'
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goCompanyDetail(name) {
  companyName.value = name
  currentView.value = 'company'
  loadCompanyJobs(name)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function switchStrategy(key) {
  strategy.value = key
  fetchRecommendations()
}

/* ============================================================
 *   推荐列表 - API 数据
 * ============================================================ */
const loading = ref(false)
const recommendations = ref([])

async function fetchRecommendations() {
  loading.value = true
  try {
    const res = await mlAPI.getRecommendations({
      strategy: strategy.value,
      top_k: topK.value,
    })
    recommendations.value = res.data.recommendations || []
  } catch (e) {
    console.error('获取推荐失败', e)
    recommendations.value = []
  } finally {
    loading.value = false
  }
}

/* ============================================================
 *   详情页 - API 数据
 * ============================================================ */
const jobDetailCompanyStats = ref({ jobCount: 0, recruitTotal: 0, avgSalary: '--' })
const similarJobs = ref([])
const salaryAnalysis = ref({
  industryAvg: '--', abovePercentage: 0,
  rangeMin: '--', rangeMax: '--', positionPercentage: 50,
})

async function loadJobDetail(jobId) {
  try {
    const res = await analysisAPI.getJobDetail(jobId)
    const d = res.data

    selectedJob.value = d

    /* 公司统计 */
    jobDetailCompanyStats.value = {
      jobCount: d.companyStats?.jobCount || 0,
      recruitTotal: d.companyStats?.recruitTotal || 0,
      avgSalary: d.companyStats?.avgSalary
        ? (d.companyStats.avgSalary / 1000).toFixed(1) + 'k'
        : '--',
    }

    similarJobs.value = d.similarJobs || []

    /* 薪资分析 */
    const sa = d.salaryAnalysis || {}
    const rangeMin = sa.rangeMin || 0
    const rangeMax = sa.rangeMax || 0
    const currentSalary = d.monthSalaryAvg || 0
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

    currentView.value = 'detail'
  } catch (e) {
    console.error('加载岗位详情失败', e)
  }
}

/* ============================================================
 *   公司详情 - API 数据
 * ============================================================ */
const companyJobs = ref([])
const companyDetailStats = ref({ jobCount: 0, recruitTotal: 0, avgSalary: '--' })

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
 *   收藏功能
 * ============================================================ */
const favoriteIds = ref(new Set())

async function fetchFavorites() {
  try {
    const res = await authAPI.getFavorites()
    favoriteIds.value = new Set((res.data || []).map(f => f.job.id))
  } catch { /* ignore */ }
}

async function toggleFavorite(job) {
  try {
    const isFav = favoriteIds.value.has(job.id)
    if (isFav) {
      const records = await authAPI.getFavorites()
      const record = (records.data || []).find(f => f.job.id === job.id)
      if (record) {
        await authAPI.removeFavorite(record.id)
        favoriteIds.value.delete(job.id)
      }
    } else {
      await authAPI.addFavorite({ job_id: job.id })
      favoriteIds.value.add(job.id)
    }
    // 刷新收藏列表
    favoriteIds.value = new Set(favoriteIds.value)
  } catch (e) { console.error('收藏操作失败', e) }
}

function isFavorited(jobId) {
  return favoriteIds.value.has(jobId)
}

/* ============================================================
 *   初始化
 * ============================================================ */
onMounted(() => {
  fetchRecommendations()
  fetchFavorites()
})
</script>