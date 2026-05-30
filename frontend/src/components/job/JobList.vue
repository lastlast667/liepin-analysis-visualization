<template>
  <div class="glass-card">
    <!-- 列表头部：结果数量信息 -->
    <div class="p-4 border-b border-dark-700/50 flex items-center justify-between">
      <span class="text-sm text-gray-400">
        找到 <span class="text-primary-400 font-semibold">{{ totalCount }}</span> 个匹配的岗位
      </span>
      <slot name="header-right" />
    </div>

    <!-- 岗位卡片列表 -->
    <div class="divide-y divide-dark-700/30">
      <!-- 空状态 -->
      <div v-if="jobs.length === 0" class="p-12 text-center text-gray-500">
        <svg class="w-12 h-12 mx-auto mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        未找到匹配的岗位，请调整筛选条件
      </div>
      <!-- 岗位卡片 -->
      <div v-for="job in jobs" :key="job.id"
           class="p-5 hover:bg-dark-800/30 transition-all duration-300 cursor-pointer group hover:shadow-lg hover:-translate-y-0.5">
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <!-- 岗位标题，点击进入详情 -->
            <div class="flex items-center gap-3 mb-1">
              <h3 @click="$emit('view-job', job)"
                  class="text-base font-semibold text-gray-200 group-hover:text-primary-400 transition-colors cursor-pointer truncate">
                {{ job.title }}
              </h3>
              <span class="px-2 py-0.5 rounded text-xs bg-dark-700 text-gray-400 flex-shrink-0">{{ job.company_industry }}</span>
            </div>
            <!-- 公司名 · 城市 -->
            <p class="text-sm text-gray-500 mb-2">{{ job.company_name }} · {{ job.location_city }}</p>
            <!-- 薪资 / 经验 / 学历 / 招聘人数 / 更新时间 -->
            <div class="flex items-center gap-3 text-xs text-gray-500 flex-wrap">
              <span class="flex items-center gap-1 text-primary-400 font-medium">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ job.salary }}
              </span>
              <span v-if="job.experience">· {{ job.experience }}</span>
              <span v-if="job.education">· {{ job.education }}</span>
              <span>· 招{{ job.recruit_count }}人</span>
              <span>· {{ job.update_time }}</span>
            </div>
          </div>
          <!-- 收藏按钮（hover 时显示） -->
          <button @click.stop="$emit('toggle-favorite', job)"
                  class="p-2 rounded-lg hover:bg-dark-700 transition-all flex-shrink-0"
                  :class="isFavorited(job.id) ? 'text-yellow-400' : 'text-gray-500 hover:text-yellow-400 opacity-0 group-hover:opacity-100'">
            <svg class="w-5 h-5" :fill="isFavorited(job.id) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 翻页控件 -->
    <div v-if="totalPages > 1" class="p-4 border-t border-dark-700/50 flex items-center justify-center gap-2">
      <button @click="$emit('page-change', Math.max(1, currentPage - 1))"
              :disabled="currentPage === 1"
              class="px-3 py-1.5 rounded-lg text-sm transition-all duration-300"
              :class="currentPage === 1 ? 'text-gray-600 cursor-not-allowed' : 'text-gray-400 hover:text-gray-200 hover:bg-dark-700'">
        上一页
      </button>
      <button v-for="page in displayPages" :key="page"
              @click="$emit('page-change', page)"
              class="w-8 h-8 rounded-lg text-sm transition-all duration-300"
              :class="currentPage === page ? 'bg-primary-600/20 text-primary-400 font-semibold' : 'text-gray-400 hover:text-gray-200 hover:bg-dark-700'">
        {{ page }}
      </button>
      <button @click="$emit('page-change', Math.min(totalPages, currentPage + 1))"
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 rounded-lg text-sm transition-all duration-300"
              :class="currentPage === totalPages ? 'text-gray-600 cursor-not-allowed' : 'text-gray-400 hover:text-gray-200 hover:bg-dark-700'">
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * 可复用的岗位卡片列表组件
 *
 * Props:
 *   jobs         - 当前页显示的岗位数组
 *   totalCount   - 匹配岗位总数（用于显示）
 *   currentPage  - 当前页码
 *   totalPages   - 总页数
 *   favoriteIds  - 已收藏岗位 ID 的 Set
 *
 * Emits:
 *   view-job(job)        - 点击岗位标题，通知父组件跳转详情
 *   toggle-favorite(job) - 点击收藏按钮，切换收藏状态
 *   page-change(page)    - 切换页码
 */
const props = defineProps({
  jobs: { type: Array, default: () => [] },
  totalCount: { type: Number, default: 0 },
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 },
  favoriteIds: { type: Set, default: () => new Set() },
})

defineEmits(['view-job', 'toggle-favorite', 'page-change'])

/** 判断岗位是否已收藏 */
function isFavorited(jobId) {
  return props.favoriteIds.has(jobId)
}

/** 计算显示的页码按钮列表（最多显示 5 个） */
const displayPages = computed(() => {
  const total = props.totalPages
  const current = props.currentPage
  const pages = []
  const maxShow = 5
  let startPage = Math.max(1, current - Math.floor(maxShow / 2))
  let endPage = Math.min(total, startPage + maxShow - 1)
  if (endPage - startPage + 1 < maxShow) {
    startPage = Math.max(1, endPage - maxShow + 1)
  }
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }
  return pages
})
</script>