<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">薪资分析</h1>
        <p class="text-gray-500 mt-1">薪资分布统计与趋势分析</p>
      </div>
    </div>

    <!-- ===== 第一行：搜索/筛选栏（复用 CompanyAnalysisView 的搜索框） ===== -->
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

    <!-- ===== 第二行：3 张统计卡片（平均薪资 / 最高薪资 / 薪资中位数） ===== -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="stat-card">
        <p class="text-sm text-gray-500">平均薪资</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ formatSalary(currentStats.avg_salary) }}</p>
        <p class="text-xs text-gray-500 mt-2">所有职位的平均月薪</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">最高薪资</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ formatSalary(currentStats.max_salary) }}</p>
        <p class="text-xs text-gray-500 mt-2">最高月薪职位</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">薪资中位数</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ formatSalary(currentStats.median_salary) }}</p>
        <p class="text-xs text-gray-500 mt-2">薪资中位数</p>
      </div>
    </div>

    <!-- ===== 第三行：城市薪资排名 + 行业薪资排名（横向条形图） ===== -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 城市薪资排名-横向条形图（复用 LocationDistributionView 的城市岗位数量分布代码） -->
      <div class="glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-200">城市薪资排名</h3>
          <div class="relative">
            <select v-model="topN" class="glass-input text-sm text-gray-200 px-3 py-1.5 rounded-lg border border-dark-600 focus:border-primary-500/50 focus:outline-none cursor-pointer appearance-none bg-dark-800 pr-8">
              <option :value="5" class="bg-dark-800">Top 5</option>
              <option :value="10" class="bg-dark-800">Top 10</option>
              <option :value="20" class="bg-dark-800" selected>Top 20</option>
            </select>
            <svg class="w-4 h-4 text-gray-500 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        <!-- 高度改为 1.25倍（h-80 = 20rem → 25rem = 400px），适配更多城市/行业数据展示 -->
        <div class="h-[25rem]">
          <v-chart :option="citySalaryOption" autoresize class="w-full h-full" />
        </div>
      </div>

      <!-- 行业薪资排名-横向条形图（复用城市薪资排名卡片代码样式） -->
      <div class="glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-200">行业薪资排名</h3>
          <div class="relative">
            <select v-model="industryTopN" class="glass-input text-sm text-gray-200 px-3 py-1.5 rounded-lg border border-dark-600 focus:border-primary-500/50 focus:outline-none cursor-pointer appearance-none bg-dark-800 pr-8">
              <option :value="5" class="bg-dark-800">Top 5</option>
              <option :value="10" class="bg-dark-800" selected>Top 10</option>
              <option :value="20" class="bg-dark-800">Top 20</option>
            </select>
            <svg class="w-4 h-4 text-gray-500 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        <!-- 高度改为 1.25倍（h-80 = 20rem → 25rem = 400px），适配更多行业数据展示 -->
        <div class="h-[25rem]">
          <v-chart :option="industrySalaryOption" autoresize class="w-full h-full" />
        </div>
      </div>
    </div>

    <!-- ===== 第四行：薪资区间分布（环形图）+ 公司规模与薪资关系（柱状图） ===== -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 薪资区间分布-环形图 -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">薪资区间分布</h3>
        <div class="h-80">
          <v-chart :option="salaryRangeOption" autoresize class="w-full h-full" />
        </div>
      </div>

      <!-- 公司规模与薪资关系-柱状图 -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">公司规模与薪资关系</h3>
        <div class="h-80">
          <v-chart :option="scaleSalaryOption" autoresize class="w-full h-full" />
        </div>
      </div>
    </div>

    <!-- ===== 第五行：学历与薪资关系 + 经验与薪资关系（柱状图） ===== -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">学历与薪资关系</h3>
        <div class="h-80">
          <v-chart :option="educationSalaryOption" autoresize class="w-full h-full" />
        </div>
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">经验与薪资关系</h3>
        <div class="h-80">
          <v-chart :option="experienceSalaryOption" autoresize class="w-full h-full" />
        </div>
      </div>
    </div>

    <!-- ===== 第六行：周末双休与薪资关系 + 外语要求与薪资关系（后端 seaborn 生成的图片） ===== -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">周末双休与薪资关系</h3>
        <div class="h-80 flex items-center justify-center">
          <img v-if="weekendOffImage" :src="weekendOffImage" alt="周末双休与薪资关系" class="max-w-full max-h-full object-contain" />
          <p v-else class="text-gray-500">暂无数据</p>
        </div>
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">外语要求与薪资关系</h3>
        <div class="h-80 flex items-center justify-center">
          <img v-if="languageRequirementImage" :src="languageRequirementImage" alt="外语要求与薪资关系" class="max-w-full max-h-full object-contain" />
          <p v-else class="text-gray-500">暂无数据</p>
        </div>
      </div>
    </div>

    <!-- ===== 第七行：岗位类别与薪资关系（箱线图，不受筛选框影响） ===== -->
    <div class="glass-card p-6">
      <h3 class="text-lg font-semibold text-gray-200 mb-4">岗位类别与薪资关系</h3>
      <div class="h-96">
        <v-chart :option="boxPlotOption" autoresize class="w-full h-full" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { use } from 'echarts/core'
import * as echarts from 'echarts/core'
import { BarChart, PieChart, BoxplotChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { analysisAPI } from '@/api'

// 注册所需 ECharts 组件
use([BarChart, PieChart, BoxplotChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

// 颜色调色板
const colors = ['#6366f1', '#14b8a6', '#f59e0b', '#8b5cf6', '#ec4899', '#3b82f6', '#10b981', '#f97316', '#06b6d4', '#a855f7']

// ===== 搜索/筛选状态 =====
// 岗位类别选项（也作为底部箱线图的 category 字段唯一值来源）
const categoryOptions = ref(['算法工程师', 'Go开发', 'C++开发', 'Java开发', 'Python开发', '前端开发', '数据分析', '测试开发'])
const partitionOptions = ref(['华东地区', '华北地区', '华南地区', '西南地区', '华中地区', '西北地区', '东北地区'])
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

function clearCategoryFilter() {
  selectedCategories.value = []
  categoryOpen.value = false
}
function clearPartitionFilter() {
  selectedPartitions.value = []
  partitionOpen.value = false
}

// 城市薪资排名 TopN 控制
const topN = ref(10)
// 行业薪资排名 TopN 控制
const industryTopN = ref(10)

// ===== API 响应数据存储 =====
const responseData = ref({
  stats: { avg_salary: 0, max_salary: 0, median_salary: 0 },
  salary_range_distribution: [],
  city_salary_ranking: [],
  industry_salary_ranking: [],
  scale_salary: [],
  education_salary: [],
  experience_salary: [],
  weekend_off_boxplot: '',
  language_boxplot: '',
  category_boxplot: [],
})

// ===== 图片数据（为模板中的 v-if 暴露 computed） =====
const weekendOffImage = computed(() => responseData.value.weekend_off_boxplot)
const languageRequirementImage = computed(() => responseData.value.language_boxplot)

// ===== 加载状态 =====
const loading = ref(false)

/** 格式化薪资为 "XX.XK" 格式 */
function formatSalary(val) {
  if (val == null || val === 0) return '--'
  return (val / 1000).toFixed(1) + 'K'
}

// ===== 统计卡片（直接从 API 返回的 stats 读取） =====
const currentStats = computed(() => responseData.value.stats)

// ===== 薪资区间分布（环形图） =====
const salaryRangeMockData = computed(() =>
  (responseData.value.salary_range_distribution || []).map(d => ({
    name: d.range,
    value: d.count,
  }))
)

// 薪资区间分布环形图配置
const salaryRangeOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(15, 15, 35, 0.9)',
    borderColor: 'rgba(99, 102, 241, 0.3)',
    textStyle: { color: '#e0e0e0', fontSize: 12 },
    formatter: (p) => `<strong>${p.name}</strong><br/>岗位数: <span style="color:#818cf8">${p.value}</span> (${p.percent}%)`,
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center',
    textStyle: { color: '#a0a0a0', fontSize: 11 },
  },
  series: [{
    type: 'pie',
    radius: ['35%', '70%'],  // 内圈半径缩小至外圈一半（35% / 70%）
    center: ['35%', '50%'],
    avoidLabelOverlap: true,
    itemStyle: {
      borderRadius: 4,
      borderColor: 'rgba(15, 15, 35, 0.6)',
      borderWidth: 2,
    },
    label: {
      show: false,
    },
    emphasis: {
      label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#e0e0e0' },
      itemStyle: { shadowBlur: 10, shadowColor: 'rgba(99, 102, 241, 0.4)' },
    },
    data: salaryRangeMockData.value.map((d, idx) => ({
      name: d.name,
      value: d.value,
      itemStyle: { color: colors[idx % colors.length] },
    })),
    animationDuration: 800,
    animationEasing: 'cubicOut',
  }],
}))

// ===== 城市薪资排名（横向条形图） =====
// 后端返回的是 { city, avg_salary }（单位为元），前端转成 K 单位
const citySalaryMockData = computed(() =>
  (responseData.value.city_salary_ranking || []).map(d => ({
    name: d.city,
    value: +(d.avg_salary / 1000).toFixed(1),
  }))
)

// 根据 topN 截取排序后的城市数据（去掉城市标签，仅展示城市名和薪资）
const sortedCityData = computed(() => {
  return [...citySalaryMockData.value].sort((a, b) => b.value - a.value).slice(0, topN.value)
})

// 城市薪资排名条形图配置（复用 LocationDistributionView 的 style）
const citySalaryOption = computed(() => {
  const data = sortedCityData.value
  const maxValue = data.length > 0 ? data[0].value : 100
  return {
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 15, 35, 0.9)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#e0e0e0', fontSize: 12 },
      formatter: (params) => {
        const d = params[0]
        return `<strong>${d.name}</strong><br/>平均薪资: <span style="color:#818cf8">${d.value}K</span>`
      },
    },
    grid: { left: 100, right: 30, top: 10, bottom: 4, containLabel: true },
    xAxis: {
      type: 'value', max: maxValue * 1.15,
      axisLabel: {
        color: '#adb5bd', fontSize: 11,
        formatter: (v) => v + 'K',
      },
      splitLine: { lineStyle: { color: '#2a2a4a' } },
    },
    yAxis: {
      type: 'category',
      data: data.map(i => i.name).reverse(),
      axisLabel: {
        color: '#333', fontSize: 12, fontWeight: 500,  // 城市名颜色调亮（#333），去掉标签
        width: 80, overflow: 'truncate',
      },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [{
      type: 'bar',
      data: data.map((i, idx) => ({
        value: i.value,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: colors[idx % colors.length] + '60' },
            { offset: 1, color: colors[idx % colors.length] },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
      })).reverse(),
      barWidth: '55%',
      animationDuration: 800,
      label: {
        show: true,
        position: 'right',
        color: '#a0a0a0',
        fontSize: 11,
        formatter: (p) => p.value + 'K',
      },
    }],
  }
})

// ===== 学历与薪资关系（柱状图） =====
const educationSalaryMockData = computed(() =>
  (responseData.value.education_salary || []).map(d => ({
    name: d.education,
    value: +(d.avg_salary / 1000).toFixed(1),
  }))
)

const educationSalaryOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    backgroundColor: 'rgba(15, 15, 35, 0.9)',
    borderColor: 'rgba(99, 102, 241, 0.3)',
    textStyle: { color: '#e0e0e0', fontSize: 12 },
    formatter: (params) => {
      const d = params[0]
      return `<strong>${d.name}</strong><br/>平均薪资: <span style="color:#818cf8">${d.value}K</span>`
    },
  },
  grid: { left: 55, right: 20, top: 10, bottom: 30, containLabel: true },
  xAxis: {
    type: 'category',
    data: educationSalaryMockData.value.map(i => i.name),
    axisLabel: { color: '#a0a0a0', fontSize: 11, interval: 0 },
    axisLine: { lineStyle: { color: '#2a2a4a' } },
  },
  yAxis: {
    type: 'value',
    name: '平均薪资(K)',
    nameTextStyle: { fontSize: 11, color: '#a0a0a0' },
    axisLabel: {
      color: '#a0a0a0', fontSize: 11,
      formatter: (v) => v + 'K',
    },
    splitLine: { lineStyle: { color: '#2a2a4a' } },
  },
  series: [{
    type: 'bar',
    barWidth: '45%',
    data: educationSalaryMockData.value.map((d, idx) => ({
      value: d.value,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: colors[idx % colors.length] },
          { offset: 1, color: colors[idx % colors.length] + '60' },
        ]),
        borderRadius: [4, 4, 0, 0],
      },
    })),
    label: {
      show: true,
      position: 'top',
      color: '#a0a0a0',
      fontSize: 11,
      formatter: (p) => p.value + 'K',
    },
    animationDuration: 800,
    animationEasing: 'cubicOut',
  }],
}))

// ===== 经验与薪资关系（柱状图） =====
const experienceSalaryMockData = computed(() =>
  (responseData.value.experience_salary || []).map(d => ({
    name: d.experience_level,
    value: +(d.avg_salary / 1000).toFixed(1),
  }))
)

const experienceSalaryOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    backgroundColor: 'rgba(15, 15, 35, 0.9)',
    borderColor: 'rgba(99, 102, 241, 0.3)',
    textStyle: { color: '#e0e0e0', fontSize: 12 },
    formatter: (params) => {
      const d = params[0]
      return `<strong>${d.name}</strong><br/>平均薪资: <span style="color:#818cf8">${d.value}K</span>`
    },
  },
  grid: { left: 55, right: 20, top: 10, bottom: 30, containLabel: true },
  xAxis: {
    type: 'category',
    data: experienceSalaryMockData.value.map(i => i.name),
    axisLabel: { color: '#a0a0a0', fontSize: 11, interval: 0 },
    axisLine: { lineStyle: { color: '#2a2a4a' } },
  },
  yAxis: {
    type: 'value',
    name: '平均薪资(K)',
    nameTextStyle: { fontSize: 11, color: '#a0a0a0' },
    axisLabel: {
      color: '#a0a0a0', fontSize: 11,
      formatter: (v) => v + 'K',
    },
    splitLine: { lineStyle: { color: '#2a2a4a' } },
  },
  series: [{
    type: 'bar',
    barWidth: '45%',
    data: experienceSalaryMockData.value.map((d, idx) => ({
      value: d.value,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: colors[(idx + 2) % colors.length] },
          { offset: 1, color: colors[(idx + 2) % colors.length] + '60' },
        ]),
        borderRadius: [4, 4, 0, 0],
      },
    })),
    label: {
      show: true,
      position: 'top',
      color: '#a0a0a0',
      fontSize: 11,
      formatter: (p) => p.value + 'K',
    },
    animationDuration: 800,
    animationEasing: 'cubicOut',
  }],
}))

// ===== 行业薪资排名（横向条形图，复用城市薪资排名代码样式） =====
const industrySalaryMockData = computed(() =>
  (responseData.value.industry_salary_ranking || []).map(d => ({
    name: d.industry,
    value: +(d.avg_salary / 1000).toFixed(1),
  }))
)

// 根据 industryTopN 截取排序后的行业数据
const sortedIndustryData = computed(() => {
  return [...industrySalaryMockData.value].sort((a, b) => b.value - a.value).slice(0, industryTopN.value)
})

// 行业薪资排名横向条形图配置（复用城市薪资排名卡片的样式）
const industrySalaryOption = computed(() => {
  const data = sortedIndustryData.value
  const maxValue = data.length > 0 ? data[0].value : 100
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 15, 35, 0.9)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#e0e0e0', fontSize: 12 },
      formatter: (params) => {
        const d = params[0]
        return `<strong>${d.name}</strong><br/>平均薪资: <span style="color:#818cf8">${d.value}K</span>`
      },
    },
    grid: { left: 100, right: 30, top: 10, bottom: 4, containLabel: true },
    xAxis: {
      type: 'value',
      max: maxValue * 1.15,
      axisLabel: {
        color: '#adb5bd', fontSize: 11,
        formatter: (v) => v + 'K',
      },
      splitLine: { lineStyle: { color: '#2a2a4a' } },
    },
    yAxis: {
      type: 'category',
      data: data.map(i => i.name).reverse(),
      axisLabel: {
        color: '#333', fontSize: 12, fontWeight: 500,  // 行业名颜色与城市名保持一致（#333）
        width: 80, overflow: 'truncate',
      },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [{
      type: 'bar',
      data: data.map((i, idx) => ({
        value: i.value,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: colors[(idx + 4) % colors.length] + '60' },
            { offset: 1, color: colors[(idx + 4) % colors.length] },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
      })).reverse(),
      barWidth: '55%',
      animationDuration: 800,
      label: {
        show: true,
        position: 'right',
        color: '#a0a0a0',
        fontSize: 11,
        formatter: (p) => p.value + 'K',
      },
    }],
  }
})

// ===== 公司规模与薪资关系（柱状图） =====
const scaleSalaryMockData = computed(() =>
  (responseData.value.scale_salary || []).map(d => ({
    name: d.scale,
    value: +(d.avg_salary / 1000).toFixed(1),
  }))
)

const scaleSalaryOption = computed(() => {
  const data = scaleSalaryMockData.value
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 15, 35, 0.9)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#e0e0e0', fontSize: 12 },
      formatter: (params) => {
        const d = params[0]
        return `<strong>${d.name}</strong><br/>平均薪资: <span style="color:#818cf8">${d.value}K</span>`
      },
    },
    grid: { left: 10, right: 20, top: 10, bottom: 30, containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(i => i.name),
      axisLabel: { color: '#a0a0a0', fontSize: 10, interval: 0 },
      axisLine: { lineStyle: { color: '#2a2a4a' } },
    },
    yAxis: {
      type: 'value',
      name: '平均薪资(K)',
      nameTextStyle: { fontSize: 11, color: '#a0a0a0' },
      axisLabel: {
        color: '#a0a0a0', fontSize: 11,
        formatter: (v) => v + 'K',
      },
      splitLine: { lineStyle: { color: '#2a2a4a' } },
    },
    series: [{
      type: 'bar',
      barWidth: '45%',
      data: data.map((d, idx) => ({
        value: d.value,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: colors[(idx + 3) % colors.length] },
            { offset: 1, color: colors[(idx + 3) % colors.length] + '60' },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
      })),
      label: {
        show: true,
        position: 'top',
        color: '#a0a0a0',
        fontSize: 11,
        formatter: (p) => p.value + 'K',
      },
      animationDuration: 800,
      animationEasing: 'cubicOut',
    }],
  }
})

// ===== 岗位类别与薪资关系（箱线图，不受筛选框影响） =====
// 后端 category_boxplot 格式：{ category, min, q1, median, q3, max }（单位 K）
const boxPlotMockData = computed(() =>
  (responseData.value.category_boxplot || []).map(d => ({
    name: d.category,
    data: [d.min, d.q1, d.median, d.q3, d.max],
  }))
)

const boxPlotOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(15, 15, 35, 0.9)',
    borderColor: 'rgba(99, 102, 241, 0.3)',
    textStyle: { color: '#e0e0e0', fontSize: 12 },
    formatter: (params) => {
      const d = params.data
      return `<strong>${params.name}</strong><br/>
        最小值: <span style="color:#818cf8">${d[0]}K</span><br/>
        Q1: <span style="color:#818cf8">${d[1]}K</span><br/>
        中位数: <span style="color:#818cf8">${d[2]}K</span><br/>
        Q3: <span style="color:#818cf8">${d[3]}K</span><br/>
        最大值: <span style="color:#818cf8">${d[4]}K</span>`
    },
  },
  grid: { left: 55, right: 30, top: 10, bottom: 30, containLabel: true },
  xAxis: {
    type: 'category',
    data: boxPlotMockData.value.map(i => i.name),
    axisLabel: { color: '#a0a0a0', fontSize: 11, interval: 0 },
    axisLine: { lineStyle: { color: '#2a2a4a' } },
  },
  yAxis: {
    type: 'value',
    name: '薪资(K)',
    nameTextStyle: { fontSize: 11, color: '#a0a0a0' },
    axisLabel: {
      color: '#a0a0a0', fontSize: 11,
      formatter: (v) => v + 'K',
    },
    splitLine: { lineStyle: { color: '#2a2a4a' } },
  },
  series: [{
    type: 'boxplot',
    data: boxPlotMockData.value.map(i => i.data),
    itemStyle: {
      color: '#6366f1',
      borderColor: '#818cf8',
      borderWidth: 2,
    },
    emphasis: {
      itemStyle: {
        color: '#818cf8',
        borderColor: '#a5b4fc',
      },
    },
    animationDuration: 800,
  }],
}))

// ===== 从 API 获取数据 =====
async function fetchData() {
  loading.value = true
  try {
    const params = {}
    // 构造筛选参数：逗号分隔的多值传给后端
    if (selectedCategories.value.length > 0) {
      params.category = selectedCategories.value.join(',')
    }
    if (selectedPartitions.value.length > 0) {
      params.location_partition = selectedPartitions.value.join(',')
    }
    const res = await analysisAPI.getSalaryAnalysis(params)
    responseData.value = res.data
  } catch (err) {
    console.error('获取薪资分析数据失败:', err)
  } finally {
    loading.value = false
  }
}

// ===== 点击外部关闭下拉框 =====
function handleClickOutside(e) {
  if (categoryRef.value && !categoryRef.value.contains(e.target)) categoryOpen.value = false
  if (partitionRef.value && !partitionRef.value.contains(e.target)) partitionOpen.value = false
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchData()  // 页面加载时自动请求数据
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
</style>