<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-100">仪表盘</h1>
        <p class="text-gray-500 mt-1">欢迎回来，{{ username }}！以下是系统概览</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="glass-card px-4 py-2 flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span class="text-sm text-gray-400">系统运行中</span>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="stat-card group">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-gray-500 mb-1">岗位总数</p>
            <p class="text-2xl font-bold text-gray-100">{{ stats.jobCount.toLocaleString() }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-primary-500/10 transition-all duration-300 group-hover:scale-110">
            <svg class="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="stat-card group">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-gray-500 mb-1">公司总数</p>
            <p class="text-2xl font-bold text-gray-100">{{ stats.companyCount.toLocaleString() }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-accent-500/10 transition-all duration-300 group-hover:scale-110">
            <svg class="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
        </div>
      </div>

      <div class="stat-card group">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-gray-500 mb-1">平均薪资</p>
            <p class="text-2xl font-bold text-gray-100">{{ avgSalaryFormatted }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-orange-500/10 transition-all duration-300 group-hover:scale-110">
            <svg class="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="stat-card group">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-gray-500 mb-1">覆盖城市</p>
            <p class="text-2xl font-bold text-gray-100">{{ stats.cityCount }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-purple-500/10 transition-all duration-300 group-hover:scale-110">
            <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Access Modules -->
    <div class="glass-card p-6">
      <h2 class="section-title">
        <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        快速访问
      </h2>

      <!-- 数据分析 -->
      <div class="mt-5">
        <h3 class="text-sm font-semibold text-gray-400 mb-3">数据分析</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <router-link to="/analysis/company" class="glass-card p-5 hover:border-primary-500/40 transition-all group">
            <div class="w-10 h-10 rounded-xl bg-primary-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 class="text-gray-200 font-medium mb-1">公司分析</h3>
            <p class="text-sm text-gray-500">分析公司规模、行业分布</p>
          </router-link>

          <router-link to="/analysis/location" class="glass-card p-5 hover:border-accent-500/40 transition-all group">
            <div class="w-10 h-10 rounded-xl bg-accent-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 class="text-gray-200 font-medium mb-1">地区分布</h3>
            <p class="text-sm text-gray-500">岗位地域分布可视化</p>
          </router-link>

          <router-link to="/analysis/jobs" class="glass-card p-5 hover:border-purple-500/40 transition-all group">
            <div class="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 class="text-gray-200 font-medium mb-1">岗位搜索</h3>
            <p class="text-sm text-gray-500">多条件精准搜索岗位</p>
          </router-link>

          <router-link to="/analysis/salary" class="glass-card p-5 hover:border-orange-500/40 transition-all group">
            <div class="w-10 h-10 rounded-xl bg-orange-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-gray-200 font-medium mb-1">薪资分析</h3>
            <p class="text-sm text-gray-500">薪资分布与趋势分析</p>
          </router-link>
        </div>
      </div>

      <!-- 机器学习 -->
      <div class="mt-6">
        <h3 class="text-sm font-semibold text-gray-400 mb-3">机器学习</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <router-link to="/ml/resume-match" class="glass-card p-5 hover:border-pink-500/40 transition-all group">
            <div class="w-10 h-10 rounded-xl bg-pink-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 class="text-gray-200 font-medium mb-1">简历匹配</h3>
            <p class="text-sm text-gray-500">智能匹配岗位与简历</p>
          </router-link>

          <router-link to="/ml/salary-predict" class="glass-card p-5 hover:border-accent-500/40 transition-all group">
            <div class="w-10 h-10 rounded-xl bg-accent-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <h3 class="text-gray-200 font-medium mb-1">薪资预测</h3>
            <p class="text-sm text-gray-500">基于经验技能的薪资预测</p>
          </router-link>

          <router-link to="/ml/recommend" class="glass-card p-5 hover:border-primary-500/40 transition-all group">
            <div class="w-10 h-10 rounded-xl bg-primary-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 class="text-gray-200 font-medium mb-1">岗位推荐</h3>
            <p class="text-sm text-gray-500">个性化岗位推荐</p>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Bottom Cards -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 岗位类别 -->
      <div class="glass-card p-6 flex flex-col">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">岗位类别</h3>
        <div class="flex-1 flex flex-col justify-center space-y-5">
          <div v-for="cat in categories" :key="cat.name" class="flex items-center gap-4">
            <div class="flex items-center gap-2.5 w-28 flex-shrink-0">
              <div class="w-2.5 h-2.5 rounded-full" :class="cat.color" />
              <span class="text-sm text-gray-300 truncate">{{ cat.name }}</span>
            </div>
            <div class="flex-1 h-2 bg-dark-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-500" :class="cat.color" :style="{ width: cat.percentage + '%' }" />
            </div>
            <span class="text-sm text-gray-400 w-14 text-right flex-shrink-0">{{ cat.count }}</span>
          </div>
        </div>
      </div>

      <!-- 机器学习模型运行状态 -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-5">机器学习模型运行状态</h3>
        <div class="space-y-5">
          <!-- 薪资预测模型 -->
          <div class="bg-dark-800/50 rounded-xl p-4 border border-dark-700/50">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-accent-500/10 flex items-center justify-center">
                  <svg class="w-4 h-4 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-gray-200">薪资预测模型</span>
              </div>
              <span class="px-2 py-0.5 rounded-full text-xs font-medium flex items-center gap-1"
                    :class="salaryPredStatus.class">
                <span class="w-1.5 h-1.5 rounded-full" :class="salaryPredStatus.dot" />
                {{ salaryPredStatus.label }}
              </span>
            </div>
            <div class="grid grid-cols-3 gap-2">
              <div class="bg-dark-700/50 rounded-lg px-2 py-1.5 text-center">
                <p class="text-gray-500 text-[10px] mb-0.5">最新训练时间</p>
                <p class="text-gray-300 font-medium text-xs">{{ salaryPred.lastTrainTime }}</p>
              </div>
              <div class="bg-dark-700/50 rounded-lg px-2 py-1.5 text-center">
                <p class="text-gray-500 text-[10px] mb-0.5">R²</p>
                <p class="text-accent-400 font-medium text-xs">{{ salaryPred.accuracy != null ? salaryPred.accuracy.toFixed(3) : '--' }}</p>
              </div>
              <div class="bg-dark-700/50 rounded-lg px-2 py-1.5 text-center">
                <p class="text-gray-500 text-[10px] mb-0.5">今日预测次数</p>
                <p class="text-gray-300 font-medium text-xs">{{ salaryPred.todayCalls }}</p>
              </div>
            </div>
          </div>

          <!-- 简历匹配模型 -->
          <div class="bg-dark-800/50 rounded-xl p-4 border border-dark-700/50">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-pink-500/10 flex items-center justify-center">
                  <svg class="w-4 h-4 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-gray-200">简历匹配模型</span>
              </div>
              <span class="px-2 py-0.5 rounded-full text-xs font-medium flex items-center gap-1"
                    :class="resumeMatchStatus.class">
                <span class="w-1.5 h-1.5 rounded-full" :class="resumeMatchStatus.dot" />
                {{ resumeMatchStatus.label }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div class="bg-dark-700/50 rounded-lg px-2 py-1.5 text-center">
                <p class="text-gray-500 text-[10px] mb-0.5">今日匹配次数</p>
                <p class="text-gray-300 font-medium text-xs">{{ resumeMatch.todayMatches }}</p>
              </div>
              <div class="bg-dark-700/50 rounded-lg px-2 py-1.5 text-center">
                <p class="text-gray-500 text-[10px] mb-0.5">最佳匹配平均得分</p>
                <p class="text-pink-400 font-medium text-xs">{{ resumeMatch.avgScore }}</p>
              </div>
            </div>
          </div>

          <!-- 岗位推荐模型 -->
          <div class="bg-dark-800/50 rounded-xl p-4 border border-dark-700/50">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-primary-500/10 flex items-center justify-center">
                  <svg class="w-4 h-4 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <span class="text-sm font-medium text-gray-200">岗位推荐模型</span>
              </div>
              <span class="px-2 py-0.5 rounded-full text-xs font-medium flex items-center gap-1"
                    :class="jobRecStatus.class">
                <span class="w-1.5 h-1.5 rounded-full" :class="jobRecStatus.dot" />
                {{ jobRecStatus.label }}
              </span>
            </div>
            <div class="text-xs">
              <div class="grid grid-cols-3 gap-2">
                <div class="bg-dark-700/50 rounded-lg px-2 py-1.5 text-center">
                  <p class="text-primary-400 font-medium text-xs">{{ jobRec.strategies.hybrid }}</p>
                  <p class="text-gray-600 text-[10px]">混合推荐</p>
                </div>
                <div class="bg-dark-700/50 rounded-lg px-2 py-1.5 text-center">
                  <p class="text-accent-400 font-medium text-xs">{{ jobRec.strategies.cf }}</p>
                  <p class="text-gray-600 text-[10px]">协同过滤</p>
                </div>
                <div class="bg-dark-700/50 rounded-lg px-2 py-1.5 text-center">
                  <p class="text-purple-400 font-medium text-xs">{{ jobRec.strategies.content }}</p>
                  <p class="text-gray-600 text-[10px]">内容推荐</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { analysisAPI, mlAPI } from '@/api'

const authStore = useAuthStore()
const username = computed(() => authStore.username)

// --- 仪表盘统计数据 ---
const stats = reactive({
  jobCount: 0,
  companyCount: 0,
  avgSalary: 0,
  cityCount: 0,
})

const avgSalaryFormatted = computed(() => {
  if (!stats.avgSalary) return '¥0'
  return `¥${Math.round(stats.avgSalary).toLocaleString()}`
})

// --- 岗位类别数据（从 API 计算百分比） ---
const categoryColors = [
  'bg-primary-500', 'bg-accent-500', 'bg-blue-500',
  'bg-purple-500', 'bg-orange-500', 'bg-pink-500',
  'bg-teal-500', 'bg-red-500', 'bg-yellow-500', 'bg-indigo-500',
]

const categories = computed(() => {
  const raw = stats.categoryList || []
  const total = raw.reduce((s, c) => s + c.count, 0) || 1
  return raw.slice(0, 10).map((item, i) => ({
    name: item.category || '未知',
    count: item.count.toLocaleString(),
    percentage: Math.round(item.count / total * 100),
    color: categoryColors[i % categoryColors.length],
  }))
})

async function fetchDashboard() {
  try {
    const res = await analysisAPI.getDashboard()
    const data = res.data
    Object.assign(stats, {
      jobCount: data.jobCount,
      companyCount: data.companyCount,
      avgSalary: data.avgSalary,
      cityCount: data.cityCount,
      categoryList: data.categoryList,
    })
  } catch (e) {
    console.error('获取仪表盘数据失败', e)
  }
}

// --- 模型状态数据 ---
const salaryPred = reactive({ lastTrainTime: '--', accuracy: null, todayCalls: 0, status: 'idle' })
const resumeMatch = reactive({ todayMatches: 0, avgScore: 0, status: 'idle' })
const jobRec = reactive({ strategies: { hybrid: 0, cf: 0, content: 0 }, status: 'idle' })

const statusMap = {
  running: { label: '运行中', class: 'bg-green-500/10 text-green-400', dot: 'bg-green-500' },
  pending: { label: '待训练', class: 'bg-yellow-500/10 text-yellow-400', dot: 'bg-yellow-500' },
  idle: { label: '空闲', class: 'bg-gray-500/10 text-gray-400', dot: 'bg-gray-500' },
}

const salaryPredStatus = computed(() => statusMap[salaryPred.status] || statusMap.idle)
const resumeMatchStatus = computed(() => statusMap[resumeMatch.status] || statusMap.idle)
const jobRecStatus = computed(() => statusMap[jobRec.status] || statusMap.idle)

async function fetchModelStatus() {
  try {
    const res = await mlAPI.getModelStatus()
    const data = res.data
    Object.assign(salaryPred, {
      lastTrainTime: data.salaryPrediction.lastTrainTime,
      accuracy: data.salaryPrediction.accuracy,
      todayCalls: data.salaryPrediction.todayCalls,
      status: data.salaryPrediction.status,
    })
    Object.assign(resumeMatch, {
      todayMatches: data.resumeMatch.todayMatches,
      avgScore: data.resumeMatch.avgScore,
      status: data.resumeMatch.status,
    })
    Object.assign(jobRec, {
      strategies: data.jobRecommend.strategies,
      status: data.jobRecommend.status,
    })
  } catch (e) {
    console.error('获取模型状态失败', e)
  }
}

onMounted(() => {
  fetchDashboard()
  fetchModelStatus()
})
</script>