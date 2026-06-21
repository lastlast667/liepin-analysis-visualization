<template>
  <aside class="w-64 h-screen fixed left-0 top-0 z-40 flex flex-col border-r border-dark-600/80 bg-dark-900/95 backdrop-blur-xl">
    <div class="p-6 border-b border-dark-600/80">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/25">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-bold text-gradient">猎聘分析</h1>
          <p class="text-xs text-gray-500">数据驱动决策</p>
        </div>
      </div>
    </div>

    <nav class="flex-1 overflow-y-auto p-4 space-y-1">
      <!-- Dashboard -->
      <router-link to="/dashboard" class="nav-item" :class="{ active: isActive('/dashboard') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <span>仪表盘</span>
      </router-link>

      <!-- Section: 数据分析 -->
      <div class="pt-4 pb-2">
        <p class="px-3 text-xs font-semibold uppercase tracking-wider text-gray-600">数据分析</p>
      </div>

      <router-link to="/analysis/company" class="nav-item" :class="{ active: isActive('/analysis/company') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <span>公司分析</span>
      </router-link>

      <router-link to="/analysis/location" class="nav-item" :class="{ active: isActive('/analysis/location') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span>地区分布</span>
      </router-link>

      <router-link to="/analysis/jobs" class="nav-item" :class="{ active: isActive('/analysis/jobs') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <span>岗位搜索</span>
      </router-link>

      <router-link to="/analysis/salary" class="nav-item" :class="{ active: isActive('/analysis/salary') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>薪资分析</span>
      </router-link>

      <!-- Section: 机器学习 -->
      <div class="pt-4 pb-2">
        <p class="px-3 text-xs font-semibold uppercase tracking-wider text-gray-600">机器学习</p>
      </div>

      <router-link to="/ml/resume-match" class="nav-item" :class="{ active: isActive('/ml/resume-match') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span>简历匹配</span>
      </router-link>

      <router-link to="/ml/salary-predict" class="nav-item" :class="{ active: isActive('/ml/salary-predict') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        <span>薪资预测</span>
      </router-link>

      <router-link to="/ml/recommend" class="nav-item" :class="{ active: isActive('/ml/recommend') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <span>岗位推荐</span>
      </router-link>

      <!-- Section: AI -->
      <div class="pt-4 pb-2">
        <p class="px-3 text-xs font-semibold uppercase tracking-wider text-gray-600">AI</p>
      </div>

      <router-link to="/ai/chat" class="nav-item" :class="{ active: isActive('/ai/chat') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
        <span>AI 客服</span>
      </router-link>
    </nav>

    <div class="p-4 border-t border-dark-600/80 space-y-2">
      <router-link to="/user/center" class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-dark-800 transition-colors">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-sm font-medium">
          {{ username.charAt(0).toUpperCase() }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-200 truncate">{{ username }}</p>
          <p class="text-xs text-gray-500">用户中心</p>
        </div>
        <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </router-link>
      <button @click="handleLogout"
              class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-500/10 transition-colors w-full text-left">
        <div class="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
          <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-red-400">退出登录</p>
          <p class="text-xs text-gray-500">安全退出当前账号</p>
        </div>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const username = authStore.username

function isActive(path) {
  return route.path === path
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
