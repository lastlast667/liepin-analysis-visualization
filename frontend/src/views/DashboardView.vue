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
      <StatCard
        label="岗位总数"
        value="12,847"
        subtext="较上周 +12.5%"
        subtext-color="text-green-400"
        icon="briefcase"
        color="primary"
        :progress="85"
      />
      <StatCard
        label="公司数量"
        value="3,256"
        subtext="较上周 +5.2%"
        subtext-color="text-green-400"
        icon="users"
        color="accent"
        :progress="72"
      />
      <StatCard
        label="平均薪资"
        value="¥18,500"
        subtext="较上周 +3.8%"
        subtext-color="text-green-400"
        icon="currency"
        color="orange"
        :progress="68"
      />
      <StatCard
        label="覆盖城市"
        value="32"
        subtext="新增 2 个城市"
        subtext-color="text-blue-400"
        icon="location"
        color="purple"
        :progress="45"
      />
    </div>

    <!-- Quick Access Modules -->
    <div>
      <h2 class="section-title">
        <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        快速访问
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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

    <!-- ML Modules -->
    <div>
      <h2 class="section-title">
        <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        机器学习
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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

    <!-- Recent Activity / Charts Preview -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">热门岗位类别</h3>
        <div class="space-y-4">
          <div v-for="cat in topCategories" :key="cat.name" class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-2 h-2 rounded-full" :class="cat.color" />
              <span class="text-sm text-gray-300">{{ cat.name }}</span>
            </div>
            <div class="flex items-center gap-4">
              <div class="w-32 h-1.5 bg-dark-700 rounded-full overflow-hidden">
                <div class="h-full rounded-full" :class="cat.color" :style="{ width: cat.percentage + '%' }" />
              </div>
              <span class="text-sm text-gray-400 w-12 text-right">{{ cat.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">最新动态</h3>
        <div class="space-y-4">
          <div v-for="(activity, idx) in recentActivities" :key="idx"
               class="flex items-start gap-3 pb-4 border-b border-dark-700/50 last:border-0">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :class="activity.bg">
              <svg class="w-4 h-4" :class="activity.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="activity.icon" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-300">{{ activity.text }}</p>
              <p class="text-xs text-gray-600 mt-0.5">{{ activity.time }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import StatCard from '@/components/StatCard.vue'

const authStore = useAuthStore()
const username = computed(() => authStore.username)

const topCategories = [
  { name: 'Java开发', percentage: 85, count: '2,450', color: 'bg-primary-500' },
  { name: 'Python开发', percentage: 70, count: '1,890', color: 'bg-accent-500' },
  { name: 'Go开发', percentage: 55, count: '1,560', color: 'bg-blue-500' },
  { name: 'C++开发', percentage: 45, count: '1,230', color: 'bg-purple-500' },
  { name: '前端开发', percentage: 40, count: '1,120', color: 'bg-orange-500' },
]

const recentActivities = [
  {
    text: '数据爬取完成 - 新增 1,247 条 Python 开发岗位数据',
    time: '2 分钟前',
    bg: 'bg-green-500/10',
    iconColor: 'text-green-400',
    icon: 'M5 13l4 4L19 7',
  },
  {
    text: '薪资预测模型已完成训练，准确率 87.5%',
    time: '15 分钟前',
    bg: 'bg-accent-500/10',
    iconColor: 'text-accent-400',
    icon: 'M13 10V3L4 14h7v7l9-11h-7z',
  },
  {
    text: '新增 3 个城市的岗位数据 - 深圳、广州、杭州',
    time: '1 小时前',
    bg: 'bg-blue-500/10',
    iconColor: 'text-blue-400',
    icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z',
  },
  {
    text: '系统自动清洗完成 - 处理 5,832 条原始数据',
    time: '3 小时前',
    bg: 'bg-purple-500/10',
    iconColor: 'text-purple-400',
    icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15',
  },
]
</script>
