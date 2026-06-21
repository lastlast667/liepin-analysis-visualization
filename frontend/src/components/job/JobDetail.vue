<template>
  <div class="flex gap-6">
    <!-- 左侧详情区 -->
    <div class="flex-1 min-w-0 space-y-5">
      <!-- 顶部大卡片：岗位基本信息 -->
      <div class="glass-card p-6">
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0 space-y-3">
            <h2 class="text-xl font-bold text-gray-100">{{ job.title }}</h2>
            <!-- 公司名称（仅展示，跳转功能由下方"查看该公司所有岗位"提供） -->
            <p class="text-lg text-gray-300">{{ job.companyName }}</p>
            <!-- 薪资 / 城市 / 学历 / 经验 / 招聘人数 -->
            <div class="flex items-center gap-4 text-sm text-gray-400 flex-wrap">
              <span class="flex items-center gap-1 text-primary-400 font-semibold text-base">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ job.salary }}
              </span>
              <span v-if="job.locationCity">· {{ job.locationCity }}</span>
              <span v-if="job.education">· {{ job.education }}</span>
              <span v-if="job.experience">· {{ job.experience }}</span>
              <span v-if="job.recruitCount">· {{ job.recruitCount }}</span>
            </div>
            <!-- 行业 / 公司规模 / 周末双休或弹性工作 -->
            <div class="flex items-center gap-3 text-sm text-gray-400">
              <span v-if="job.companyIndustry">{{ job.companyIndustry }}</span>
              <span v-if="job.companyIndustry && job.companyScale">·</span>
              <span v-if="job.companyScale">{{ job.companyScale }}</span>
              <span v-if="(job.companyIndustry || job.companyScale) && job.hasWeekendOff !== null">·</span>
              <span :class="job.hasWeekendOff ? 'text-green-400' : 'text-orange-400'">
                {{ job.hasWeekendOff ? '周末双休' : '弹性工作' }}
              </span>
              <span v-if="job.updateTimeParsed">· {{ job.updateTimeParsed }} 更新</span>
            </div>
            
          </div>
          <!-- 右侧操作按钮：收藏 + 立即申请 -->
          <div class="flex flex-col gap-2 flex-shrink-0 ml-4 w-28">
            <button @click="$emit('toggle-favorite', job)"
                    class="w-full px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 flex items-center justify-center gap-2"
                    :class="isFavorited ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' : 'bg-dark-800 text-gray-400 hover:text-yellow-400 border border-dark-600 hover:border-yellow-500/30'">
              <svg class="w-4 h-4 flex-shrink-0" :fill="isFavorited ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              {{ isFavorited ? '已收藏' : '收藏' }}
            </button>
            <a :href="job.jobUrl" target="_blank"
               class="w-full px-4 py-2 rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 text-white text-sm font-medium transition-all duration-300 text-center shadow-lg shadow-primary-500/25">
              立即申请
            </a>
          </div>
        </div>
      </div>

      <!-- 岗位详情卡片：亮点标签 + 描述 + 语言要求 -->
      <div class="glass-card p-6">
        <h3 class="text-base font-semibold text-gray-200 mb-4">岗位详情</h3>
        <!-- 岗位亮点标签 -->
        <div v-if="job.companyTags && job.companyTags.length > 0" class="mb-4">
          <p class="text-sm text-gray-500 mb-2">岗位亮点</p>
          <div class="flex flex-wrap gap-2">
            <span v-for="tag in job.companyTags" :key="tag"
                  class="px-2.5 py-1 rounded-lg text-xs bg-primary-500/10 text-primary-400 border border-primary-500/20">
              {{ tag }}
            </span>
          </div>
        </div>
        <!-- 岗位描述 -->
        <div class="mb-4">
          <p class="text-sm text-gray-500 mb-2">岗位描述</p>
          <p class="text-sm text-gray-300 leading-relaxed whitespace-pre-line">{{ job.jobDescription }}</p>
        </div>
        <!-- 语言要求 -->
        <div v-if="job.languageRequirement">
          <p class="text-sm text-gray-500 mb-2">语言要求</p>
          <p class="text-sm text-gray-300">{{ job.languageRequirement }}</p>
        </div>
      </div>

      <!-- 公司介绍卡片 -->
      <div class="glass-card p-6">
        <h3 class="text-base font-semibold text-gray-200 mb-4">公司介绍</h3>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-gray-500">公司名称</p>
            <p class="text-gray-200 font-medium">{{ job.companyName }}</p>
          </div>
          <div v-if="job.companyIndustry">
            <p class="text-gray-500">所属行业</p>
            <p class="text-gray-200">{{ job.companyIndustry }}</p>
          </div>
          <div v-if="job.companyScale">
            <p class="text-gray-500">公司规模</p>
            <p class="text-gray-200">{{ job.companyScale }}</p>
          </div>
          <div>
            <p class="text-gray-500">岗位数量</p>
            <p class="text-gray-200">{{ companyStats.jobCount }} 个</p>
          </div>
          <div>
            <p class="text-gray-500">招聘人数</p>
            <p class="text-gray-200">{{ companyStats.recruitTotal }} 人</p>
          </div>
          <div>
            <p class="text-gray-500">平均薪资</p>
            <p class="text-gray-200 text-primary-400 font-medium">{{ companyStats.avgSalary }}</p>
          </div>
        </div>
        <!-- 查看该公司所有岗位 -->
        <div class="mt-5 pt-4 border-t border-dark-700/50">
          <button @click="$emit('view-company', job.companyName)"
                  class="text-sm text-primary-400 hover:text-primary-300 transition-colors flex items-center gap-1">
            查看该公司所有岗位
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 右侧推荐区 -->
    <div class="w-80 flex-shrink-0 space-y-5">
      <!-- 卡片1：相似岗位推荐 Top3 -->
      <div class="glass-card p-5">
        <h3 class="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          相似岗位推荐
        </h3>
        <div class="space-y-3">
          <div v-for="simJob in similarJobs" :key="simJob.id"
               class="group cursor-pointer hover:bg-dark-800/50 rounded-lg p-2 -mx-2 transition-colors">
            <p @click="$emit('view-similar', simJob)"
               class="text-sm text-gray-300 group-hover:text-primary-400 transition-colors font-medium truncate">{{ simJob.title }}</p>
            <p class="text-xs text-gray-500 mt-0.5">{{ simJob.companyName }} · {{ simJob.locationCity }}</p>
            <p class="text-xs text-primary-400 mt-0.5 font-medium">{{ simJob.salary }}</p>
          </div>
        </div>
      </div>

      <!-- 卡片2：薪资分析 -->
      <div class="glass-card p-5">
        <h3 class="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          薪资分析
        </h3>
        <div class="space-y-3 text-sm">
          <div>
            <p class="text-gray-500">当前岗位薪资</p>
            <p class="text-primary-400 font-semibold text-base">{{ job.salary }}</p>
          </div>
          <div>
            <p class="text-gray-500">行业平均薪资</p>
            <p class="text-gray-200">{{ salaryAnalysis.industryAvg }}</p>
          </div>
          <div>
            <p class="text-gray-500">高于行业平均</p>
            <p class="font-semibold" :class="salaryAnalysis.abovePercentage >= 0 ? 'text-green-400' : 'text-red-400'">{{ salaryAnalysis.abovePercentage >= 0 ? '' : '' }}{{ salaryAnalysis.abovePercentage }}%</p>
          </div>
          <!-- 薪资范围分布条 -->
          <div>
            <p class="text-gray-500 mb-2">行业薪资范围分布</p>
            <div class="relative h-6 bg-dark-800 rounded-full overflow-hidden">
              <div class="absolute inset-0 bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-red-500/30" />
              <!-- 当前薪资位置标记 -->
              <div class="absolute top-0 bottom-0 w-0.5 bg-white shadow-lg"
                   :style="{ left: salaryAnalysis.positionPercentage + '%' }">
                <div class="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-white rounded-full border-2 border-dark-900" />
              </div>
            </div>
            <div class="flex justify-between text-xs text-gray-500 mt-1">
              <span>{{ salaryAnalysis.rangeMin }}</span>
              <span>{{ salaryAnalysis.rangeMax }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 岗位详情子组件
 *
 * Props:
 *   job            - 当前展示的岗位对象
 *   companyStats   - 该公司统计数据 { jobCount, recruitTotal, avgSalary }
 *   similarJobs    - 相似岗位列表
 *   salaryAnalysis - 薪资分析数据 { industryAvg, abovePercentage, rangeMin, rangeMax, positionPercentage }
 *   isFavorited    - 当前岗位是否已收藏
 *
 * Emits:
 *   view-company(companyName) - 跳转到公司详情页
 *   toggle-favorite(job)      - 切换收藏
 *   view-similar(job)         - 跳转到相似岗位详情
 */
defineProps({
  job: { type: Object, required: true },
  companyStats: { type: Object, default: () => ({ jobCount: 0, recruitTotal: 0, avgSalary: '--' }) },
  similarJobs: { type: Array, default: () => [] },
  salaryAnalysis: { type: Object, default: () => ({ industryAvg: '--', abovePercentage: 0, rangeMin: '--', rangeMax: '--', positionPercentage: 50 }) },
  isFavorited: { type: Boolean, default: false },
})

defineEmits(['view-company', 'toggle-favorite', 'view-similar'])
</script>