<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">公司分析</h1>
        <p class="text-gray-500 mt-1">分析招聘公司规模、行业分布等信息</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="glass-card p-5">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm text-gray-400 mb-2">行业</label>
          <select v-model="filters.industry" class="glass-input w-full">
            <option value="">全部行业</option>
            <option value="互联网">互联网</option>
            <option value="金融">金融</option>
            <option value="教育">教育</option>
            <option value="医疗">医疗</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">公司规模</label>
          <select v-model="filters.scale" class="glass-input w-full">
            <option value="">全部规模</option>
            <option value="0-50">0-50人</option>
            <option value="50-200">50-200人</option>
            <option value="200-1000">200-1000人</option>
            <option value="1000+">1000人以上</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">城市</label>
          <input v-model="filters.city" type="text" class="glass-input w-full" placeholder="输入城市" />
        </div>
        <div class="flex items-end">
          <button @click="searchCompany" class="btn-primary w-full">查询分析</button>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="stat-card">
        <p class="text-sm text-gray-500">公司总数</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">3,256</p>
        <p class="text-xs text-green-400 mt-2">↑ 较上月增长 5.2%</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">平均规模</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">286 人</p>
        <p class="text-xs text-gray-500 mt-2">中型企业为主</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">覆盖行业</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">24</p>
        <p class="text-xs text-accent-400 mt-2">互联网/IT 占比最高</p>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">行业分布 Top 10</h3>
        <div class="space-y-3">
          <div v-for="(item, idx) in industryData" :key="idx" class="flex items-center gap-3">
            <span class="text-sm text-gray-500 w-6">{{ idx + 1 }}</span>
            <span class="text-sm text-gray-300 w-24">{{ item.name }}</span>
            <div class="flex-1 h-2 bg-dark-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-400"
                   :style="{ width: item.percentage + '%' }" />
            </div>
            <span class="text-sm text-gray-400 w-16 text-right">{{ item.count }}</span>
          </div>
        </div>
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">公司规模分布</h3>
        <div class="flex items-center justify-center h-64">
          <div class="text-center text-gray-500">
            <svg class="w-16 h-16 mx-auto mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
            </svg>
            <p>图表加载区域</p>
            <p class="text-xs mt-1">将使用 ECharts 渲染</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Company Table -->
    <div class="glass-card">
      <div class="p-6 border-b border-dark-700/50">
        <h3 class="text-lg font-semibold text-gray-200">公司列表</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-dark-700/50">
              <th class="text-left p-4 text-sm text-gray-400 font-medium">公司名称</th>
              <th class="text-left p-4 text-sm text-gray-400 font-medium">行业</th>
              <th class="text-left p-4 text-sm text-gray-400 font-medium">规模</th>
              <th class="text-left p-4 text-sm text-gray-400 font-medium">城市</th>
              <th class="text-left p-4 text-sm text-gray-400 font-medium">在招岗位</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(company, idx) in companies" :key="idx"
                class="border-b border-dark-700/30 hover:bg-dark-800/50 transition-colors">
              <td class="p-4 text-sm text-gray-200">{{ company.name }}</td>
              <td class="p-4 text-sm text-gray-400">{{ company.industry }}</td>
              <td class="p-4 text-sm text-gray-400">{{ company.scale }}</td>
              <td class="p-4 text-sm text-gray-400">{{ company.city }}</td>
              <td class="p-4 text-sm">
                <span class="px-2 py-1 rounded-lg bg-primary-500/10 text-primary-400 text-xs">{{ company.jobs }} 个</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const filters = reactive({
  industry: '',
  scale: '',
  city: '',
})

const industryData = [
  { name: '互联网/IT', percentage: 35, count: '1,140' },
  { name: '金融', percentage: 18, count: '586' },
  { name: '教育/培训', percentage: 12, count: '391' },
  { name: '医疗健康', percentage: 10, count: '326' },
  { name: '制造业', percentage: 8, count: '260' },
  { name: '房地产', percentage: 6, count: '195' },
  { name: '文化传媒', percentage: 5, count: '163' },
  { name: '零售/贸易', percentage: 4, count: '130' },
  { name: '交通/物流', percentage: 2, count: '65' },
  { name: '其他', percentage: 0, count: '0' },
]

const companies = [
  { name: '字节跳动', industry: '互联网/IT', scale: '10000人以上', city: '北京', jobs: 245 },
  { name: '阿里巴巴', industry: '互联网/IT', scale: '10000人以上', city: '杭州', jobs: 198 },
  { name: '腾讯科技', industry: '互联网/IT', scale: '10000人以上', city: '深圳', jobs: 186 },
  { name: '华为技术', industry: '通信/硬件', scale: '10000人以上', city: '深圳', jobs: 312 },
  { name: '美团', industry: '互联网/IT', scale: '10000人以上', city: '北京', jobs: 156 },
  { name: '蚂蚁集团', industry: '金融', scale: '10000人以上', city: '杭州', jobs: 89 },
]

function searchCompany() {
  console.log('Search with filters:', filters)
}
</script>
