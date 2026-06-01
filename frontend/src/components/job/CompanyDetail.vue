<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 公司信息头部 -->
    <div class="glass-card p-6">
      <div class="flex items-start justify-between">
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <!-- 公司图标 -->
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-600/20 to-primary-400/10 border border-primary-500/20 flex items-center justify-center flex-shrink-0">
              <span class="text-lg font-bold text-primary-400">
                {{ companyName.charAt(0) }}
              </span>
            </div>
            <div>
              <h2 class="text-xl font-bold text-gray-100">{{ companyName }}</h2>
              <p class="text-sm text-gray-400">
              <template v-if="companyIndustry && companyIndustry !== '--'">{{ companyIndustry }}</template>
              {{ companyScale }}
            </p>
            </div>
          </div>
        </div>
      </div>
      <!-- 公司统计数据 2x3 网格 -->
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mt-5 pt-5 border-t border-dark-700/50">
        <div class="text-center p-3 rounded-lg bg-dark-800/50">
          <p class="text-2xl font-bold text-primary-400">{{ companyStats.jobCount }}</p>
          <p class="text-xs text-gray-500 mt-1">在招岗位</p>
        </div>
        <div class="text-center p-3 rounded-lg bg-dark-800/50">
          <p class="text-2xl font-bold text-primary-400">{{ companyStats.recruitTotal }}</p>
          <p class="text-xs text-gray-500 mt-1">招聘总人数</p>
        </div>
        <div class="text-center p-3 rounded-lg bg-dark-800/50">
          <p class="text-2xl font-bold text-primary-400">{{ companyStats.avgSalary }}</p>
          <p class="text-xs text-gray-500 mt-1">平均薪资</p>
        </div>
      </div>
    </div>

    <!-- 该公司在招岗位列表（内部复用 JobList） -->
    <div>
      <h3 class="text-base font-semibold text-gray-200 mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        {{ companyName }} · 在招岗位
      </h3>
      <JobList
        :jobs="paginatedCompanyJobs"
        :total-count="companyJobs.length"
        :current-page="companyCurrentPage"
        :total-pages="companyTotalPages"
        :favorite-ids="favoriteIds"
        @view-job="(job) => $emit('view-job', job)"
        @toggle-favorite="(job) => $emit('toggle-favorite', job)"
        @page-change="companyCurrentPage = $event"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import JobList from './JobList.vue'

/**
 * 公司详情子组件
 *
 * Props:
 *   companyName  - 公司名称
 *   companyJobs  - 该公司所有岗位列表
 *   companyStats - 公司统计数据 { jobCount, recruitTotal, avgSalary }
 *   favoriteIds  - 已收藏岗位 ID 的 Set
 *
 * Emits:
 *   view-job(job)        - 点击岗位进入详情
 *   toggle-favorite(job) - 切换收藏
 *   back()               - 返回上一级
 */
const props = defineProps({
  companyName: { type: String, required: true },
  companyJobs: { type: Array, default: () => [] },
  companyStats: { type: Object, default: () => ({ jobCount: 0, recruitTotal: 0, avgSalary: '--' }) },
  favoriteIds: { type: Set, default: () => new Set() },
})

defineEmits(['view-job', 'toggle-favorite', 'back'])

/** 从第一个岗位中获取公司行业和规模信息 */
const companyIndustry = computed(() => {
  return props.companyJobs.length > 0 ? props.companyJobs[0].company_industry : '--'
})

const companyScale = computed(() => {
  return props.companyJobs.length > 0 ? props.companyJobs[0].company_scale : '--'
})

/**
 * CompanyDetail 内部管理自己的翻页状态
 * 翻页逻辑与父组件的搜索列表翻页相互独立
 */
const pageSize = 10
const companyCurrentPage = ref(1)

const companyTotalPages = computed(() => {
  return Math.max(1, Math.ceil(props.companyJobs.length / pageSize))
})

const paginatedCompanyJobs = computed(() => {
  const start = (companyCurrentPage.value - 1) * pageSize
  return props.companyJobs.slice(start, start + pageSize)
})
</script>