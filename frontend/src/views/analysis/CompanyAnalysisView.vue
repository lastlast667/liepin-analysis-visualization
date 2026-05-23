<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">公司分析</h1>
        <p class="text-gray-500 mt-1">分析招聘公司规模、行业分布等信息</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="glass-card p-5 overflow-visible relative z-30">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end overflow-visible">
        <div class="relative z-10" ref="categoryRef">
          <label class="block text-sm text-gray-400 mb-2">岗位类别</label>
          <div @click="categoryOpen = !categoryOpen" class="glass-input w-full cursor-pointer flex items-center justify-between">
            <span class="truncate" :class="selectedCategoryLabel ? 'text-gray-100' : 'text-gray-500'">
              {{ selectedCategoryLabel || '全部' }}
            </span>
            <svg class="w-4 h-4 text-gray-500 transition-transform flex-shrink-0" :class="{ 'rotate-180': categoryOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
          <div v-if="categoryOpen" class="absolute z-[100] mt-1 w-full glass-card p-2 max-h-48 overflow-y-auto shadow-2xl">
            <label class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
              <input type="checkbox" :checked="selectedCategories.length === 0" @change="clearCategoryFilter" class="rounded accent-primary-500" />
              <span class="text-sm text-gray-300">全部</span>
            </label>
            <label v-for="cat in categoryOptions" :key="cat" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
              <input type="checkbox" :value="cat" v-model="selectedCategories" class="rounded accent-primary-500" />
              <span class="text-sm text-gray-300">{{ cat }}</span>
            </label>
          </div>
        </div>

        <div class="relative z-10" ref="partitionRef">
          <label class="block text-sm text-gray-400 mb-2">地理分区</label>
          <div @click="partitionOpen = !partitionOpen" class="glass-input w-full cursor-pointer flex items-center justify-between">
            <span class="truncate" :class="selectedPartitionLabel ? 'text-gray-100' : 'text-gray-500'">
              {{ selectedPartitionLabel || '全部' }}
            </span>
            <svg class="w-4 h-4 text-gray-500 transition-transform flex-shrink-0" :class="{ 'rotate-180': partitionOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
          <div v-if="partitionOpen" class="absolute z-[100] mt-1 w-full glass-card p-2 max-h-48 overflow-y-auto shadow-2xl">
            <label class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
              <input type="checkbox" :checked="selectedPartitions.length === 0" @change="clearPartitionFilter" class="rounded accent-primary-500" />
              <span class="text-sm text-gray-300">全部</span>
            </label>
            <label v-for="p in partitionOptions" :key="p" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
              <input type="checkbox" :value="p" v-model="selectedPartitions" class="rounded accent-primary-500" />
              <span class="text-sm text-gray-300">{{ p }}</span>
            </label>
          </div>
        </div>

        <div class="flex items-end">
          <button @click="fetchData" class="btn-primary w-full">查询分析</button>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="stat-card">
        <p class="text-sm text-gray-500">公司总数</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ loading ? '-' : (stats.total_companies || '暂无') }}</p>
        <p class="text-xs text-gray-500 mt-2">符合筛选条件的招聘公司总量</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">覆盖行业总数</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ loading ? '-' : (stats.total_industries || '暂无') }}</p>
        <p class="text-xs text-gray-500 mt-2" v-if="stats.top_industry">{{ stats.top_industry.name }} 行业占比最高</p>
        <p class="text-xs text-gray-500 mt-2" v-else>暂无数据</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">平均规模</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ loading ? '-' : (stats.avg_scale ? stats.avg_scale + ' 人' : '暂无') }}</p>
        <p class="text-xs text-gray-500 mt-2">{{ stats.scale_type || '' }}</p>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">行业分布 Top 10</h3>
        <div v-if="loading" class="flex items-center justify-center h-80">
          <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else-if="industryDistribution.length === 0" class="flex items-center justify-center h-80 text-gray-500">暂无数据</div>
        <v-chart v-else :option="barOption" autoresize class="h-80" />
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">公司规模分布</h3>
        <div v-if="loading" class="flex items-center justify-center h-80">
          <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else-if="scaleDistribution.length === 0" class="flex items-center justify-center h-80 text-gray-500">暂无数据</div>
        <v-chart v-else :option="pieOption" autoresize class="h-80" />
      </div>
    </div>

    <!-- Word Cloud + Province Distribution -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">公司福利词云</h3>
        <div v-if="loading" class="flex items-center justify-center h-80">
          <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else-if="!wordCloudOption" class="flex items-center justify-center h-80 text-gray-500">暂无数据</div>
        <div v-else class="h-80">
          <v-chart :option="wordCloudOption" autoresize class="w-full h-full" />
        </div>
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">公司省份分布</h3>
        <div v-if="loading" class="flex items-center justify-center h-80">
          <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else-if="provinceDistribution.length === 0" class="flex items-center justify-center h-80 text-gray-500">暂无数据</div>
        <v-chart v-else :option="provinceOption" autoresize class="h-80" />
      </div>
    </div>

    <!-- Company Table -->
    <div class="glass-card">
      <div class="p-6 border-b border-dark-700/50">
        <h3 class="text-lg font-semibold text-gray-200">在招岗位 Top 10 公司</h3>
      </div>
      <div v-if="loading" class="flex items-center justify-center h-40">
        <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
      <div v-else-if="companyList.length === 0" class="flex items-center justify-center h-40 text-gray-500">暂无数据</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-dark-700/50">
              <th class="text-left p-4 text-sm text-gray-400 font-medium">公司名称</th>
              <th class="text-left p-4 text-sm text-gray-400 font-medium">公司行业</th>
              <th class="text-left p-4 text-sm text-gray-400 font-medium">公司规模</th>
              <th class="text-left p-4 text-sm text-gray-400 font-medium">所在城市</th>
              <th class="text-left p-4 text-sm text-gray-400 font-medium">岗位数量</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in companyList" :key="idx"
                class="border-b border-dark-700/30 hover:bg-dark-800/50 transition-colors">
              <td class="p-4 text-sm text-gray-200">{{ item.name }}</td>
              <td class="p-4 text-sm text-gray-400">{{ item.industry }}</td>
              <td class="p-4 text-sm text-gray-400">{{ item.scale }}</td>
              <td class="p-4 text-sm text-gray-400">{{ item.city }}</td>
              <td class="p-4 text-sm">
                <span class="px-2 py-1 rounded-lg bg-primary-500/10 text-primary-400 text-xs">{{ item.jobs }} 个</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { use } from 'echarts/core'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import 'echarts-wordcloud'
import VChart from 'vue-echarts'
import { analysisAPI } from '@/api'

use([BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const loading = ref(false)
const stats = reactive({ total_companies: null, total_industries: null, top_industry: null, avg_scale: null, scale_type: '' })
const industryDistribution = ref([])
const scaleDistribution = ref([])
const provinceDistribution = ref([])
const companyList = ref([])
const categoryOptions = ref([])
const partitionOptions = ref([])

const selectedCategories = ref([])
const selectedPartitions = ref([])
const categoryOpen = ref(false)
const partitionOpen = ref(false)
const categoryRef = ref(null)
const partitionRef = ref(null)

const selectedCategoryLabel = computed(() => {
  if (selectedCategories.value.length === 0) return ''
  if (selectedCategories.value.length <= 2) return selectedCategories.value.join(', ')
  return `已选 ${selectedCategories.value.length} 项`
})
const selectedPartitionLabel = computed(() => {
  if (selectedPartitions.value.length === 0) return ''
  if (selectedPartitions.value.length <= 2) return selectedPartitions.value.join(', ')
  return `已选 ${selectedPartitions.value.length} 项`
})

const colors = ['#6366f1', '#14b8a6', '#f59e0b', '#8b5cf6', '#ec4899', '#3b82f6', '#10b981', '#f97316', '#06b6d4', '#a855f7']

const barOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    backgroundColor: 'rgba(15, 15, 35, 0.9)',
    borderColor: 'rgba(99, 102, 241, 0.3)',
    textStyle: { color: '#e0e0e0', fontSize: 12 },
    formatter: (params) => {
      const d = params[0]
      return `<strong>${d.name}</strong><br/>公司数量: <span style="color:#818cf8">${d.value}</span>`
    },
  },
  grid: { left: 10, right: 20, top: 10, bottom: 10, containLabel: true },
  xAxis: {
    type: 'value',
    axisLabel: { color: '#606060' },
    splitLine: { lineStyle: { color: '#1a1a2e' } },
  },
  yAxis: {
    type: 'category',
    data: industryDistribution.value.map(i => i.name).reverse(),
    axisLabel: { color: '#a0a0a0', fontSize: 11 },
    axisLine: { show: false },
    axisTick: { show: false },
  },
  series: [{
    type: 'bar',
    data: industryDistribution.value.map((i, idx) => ({
      value: i.count,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: colors[idx % colors.length] + '80' },
          { offset: 1, color: colors[idx % colors.length] },
        ]),
        borderRadius: [0, 6, 6, 0],
      },
    })).reverse(),
    barWidth: 20,
    animationDuration: 800,
    animationEasing: 'cubicOut',
  }],
}))

const pieOption = computed(() => {
  const data = scaleDistribution.value
  const sorted = [...data].sort((a, b) => b.count - a.count)
  const top1Name = sorted.length > 0 ? sorted[0].name : ''
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 15, 35, 0.9)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#e0e0e0', fontSize: 12 },
      formatter: (p) => `<strong>${p.name}</strong><br/>公司数量: <span style="color:#818cf8">${p.value}</span>`,
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#a0a0a0', fontSize: 11 },
    },
    series: [{
      type: 'pie',
      radius: '65%',
      center: ['35%', '50%'],
      selectedOffset: 20,
      avoidLabelOverlap: true,
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#e0e0e0' },
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(99, 102, 241, 0.4)' },
      },
      data: data.map((d, idx) => ({
        name: d.name,
        value: d.count,
        itemStyle: { color: colors[idx % colors.length] },
        selected: d.name === top1Name,
      })),
      selectedMode: 'single',
      animationDuration: 600,
      animationEasing: 'cubicOut',
    }],
  }
})

const wordCloudOption = ref(null)

const provinceOption = computed(() => {
  const data = provinceDistribution.value
  const sorted = [...data].sort((a, b) => b.count - a.count)
  const top1Name = sorted.length > 0 ? sorted[0].name : ''
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 15, 35, 0.9)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#e0e0e0', fontSize: 12 },
      formatter: (p) => `<strong>${p.name}</strong><br/>公司数量: <span style="color:#818cf8">${p.value}</span>`,
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#a0a0a0', fontSize: 11 },
    },
    series: [{
      type: 'pie',
      radius: '65%',
      center: ['35%', '50%'],
      selectedOffset: 20,
      avoidLabelOverlap: true,
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#e0e0e0' },
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(99, 102, 241, 0.4)' },
      },
      data: data.map((d, idx) => ({
        name: d.name,
        value: d.count,
        itemStyle: { color: colors[idx % colors.length] },
        selected: d.name === top1Name,
      })),
      selectedMode: 'single',
      animationDuration: 600,
      animationEasing: 'cubicOut',
    }],
  }
})

function clearCategoryFilter() {
  selectedCategories.value = []
  categoryOpen.value = false
}
function clearPartitionFilter() {
  selectedPartitions.value = []
  partitionOpen.value = false
}

async function fetchData() {
  loading.value = true
  try {
    // 构建请求参数
    const params = {}
    if (selectedCategories.value.length > 0) params.category = selectedCategories.value.join(',')
    if (selectedPartitions.value.length > 0) params.partition = selectedPartitions.value.join(',')
    // 传入请求参数，调用后端接口获取公司分析数据
    const res = await analysisAPI.getCompanyAnalysis(params)
    const data = res.data

    // 将返回数据赋值给响应式变量
    Object.assign(stats, data.statistics || {})                     // 统计信息
    industryDistribution.value = data.industry_distribution || []   // 行业分布
    scaleDistribution.value = data.scale_distribution || []         // 规模分布
    provinceDistribution.value = data.province_distribution || []   // 省份分布
    companyList.value = data.companies || []                        // 公司列表
    const tags = data.company_tags_cloud || []                      // 公司标签云
    // 配置词云图
    wordCloudOption.value = {
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(15, 15, 35, 0.9)',
        borderColor: 'rgba(99, 102, 241, 0.3)',
        textStyle: { color: '#e0e0e0', fontSize: 12 },
        formatter: (p) => `<strong>${p.name}</strong><br/>出现次数: <span style="color:#818cf8">${p.value}</span>`,
      },
      series: [{
        type: 'wordCloud',
        gridSize: 4,
        sizeRange: [20, 72],
        rotationRange: [0, 0],
        shape: 'circle',
        width: '100%',
        height: '100%',
        drawOutOfBound: false,
        left: 'center',
        top: 'center',
        textStyle: {
          fontFamily: 'Inter, sans-serif',
          fontWeight: 600,
          color: () => colors[Math.floor(Math.random() * colors.length)],
        },
        data: tags,
      }],
    }
    if (categoryOptions.value.length === 0) {
      categoryOptions.value = data.category_options || []
    }
    if (partitionOptions.value.length === 0) {
      partitionOptions.value = data.partition_options || []
    }
  } catch {
    console.error('请求公司分析数据失败')
  } finally {
    loading.value = false
  }
}

function handleClickOutside(e) {
  if (categoryRef.value && !categoryRef.value.contains(e.target)) categoryOpen.value = false
  if (partitionRef.value && !partitionRef.value.contains(e.target)) partitionOpen.value = false
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchData()
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
</style>
