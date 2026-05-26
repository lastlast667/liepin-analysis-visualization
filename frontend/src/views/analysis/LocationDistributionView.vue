<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">地区分布</h1>
        <p class="text-gray-500 mt-1">岗位地域分布情况可视化分析</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="stat-card">
        <p class="text-sm text-gray-500">覆盖城市</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ stats.totalCities }}</p>
        <p class="text-xs text-gray-500 mt-2">{{ stats.cityType }}</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">一线城市占比</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ stats.firstTierPercentage }}%</p>
        <p class="text-xs text-gray-500 mt-2">{{ stats.firstTierTopCity }}岗位最多</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">新一线城市占比</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ stats.newFirstTierPercentage }}%</p>
        <p class="text-xs text-gray-500 mt-2">{{ stats.newFirstTierTopCity }}岗位最多</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">其他城市占比</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">{{ stats.otherPercentage }}%</p>
        <p class="text-xs text-gray-500 mt-2">{{ stats.otherTopCity }}岗位最多</p>
      </div>
    </div>

    <!-- Province & City Heatmaps -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 省份热力图卡片高度 600px，如需调整可改此值 -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">省份热力图</h3>
        <div v-if="provinceMapLoading" class="flex items-center justify-center" style="height:600px">
          <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else style="height:600px">
          <v-chart :option="provinceHeatmapOption" autoresize class="w-full h-full" @click="onProvinceClick" />
        </div>
      </div>

      <!-- 城市热力图卡片高度 600px，如需调整可改此值 -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">城市热力图 - {{ selectedProvince }}</h3>
        <div v-if="cityMapLoading" class="flex items-center justify-center" style="height:600px">
          <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else style="height:600px">
          <v-chart :option="cityHeatmapOption" autoresize class="w-full h-full" />
        </div>
      </div>
    </div>

    <!-- City Distribution + Region Distribution -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-200">城市岗位数量分布</h3>
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
        <div v-if="loading" class="flex items-center justify-center" style="height:480px">
          <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else style="height:480px">
          <v-chart :option="cityRankBarOption" autoresize class="w-full h-full" />
        </div>
      </div>

      <div class="glass-card p-6 flex flex-col" style="min-height:528px">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">区域分布</h3>
        <div class="flex-1 flex items-center justify-center gap-16">
          <!-- 左侧 4 个区域，圆圈尺寸 w-20/h-20，如需调整可改 w-* h-* -->
          <div class="flex flex-col gap-6 items-center">
            <div v-for="region in leftColumnRegions" :key="region.name" class="text-center">
              <div class="relative w-20 h-20 mx-auto mb-1">
                <svg class="w-20 h-20 -rotate-90" viewBox="0 0 44 44">
                  <circle cx="22" cy="22" r="19" fill="none" class="stroke-dark-700" stroke-width="3.5" />
                  <circle cx="22" cy="22" r="19" fill="none"
                          :stroke="region.color" stroke-width="3.5"
                          :stroke-dasharray="region.percentage * 1.19 + ' 200'"
                          stroke-linecap="round" />
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-sm font-bold text-gray-200">{{ region.percentage }}%</span>
                </div>
              </div>
              <p class="text-xs text-gray-400">{{ region.name }}</p>
            </div>
          </div>
          <!-- 右侧 3 个区域居中，圆圈尺寸同上 -->
          <div class="flex flex-col gap-6 justify-center">
            <div v-for="region in rightColumnRegions" :key="region.name" class="text-center">
              <div class="relative w-20 h-20 mx-auto mb-1">
                <svg class="w-20 h-20 -rotate-90" viewBox="0 0 44 44">
                  <circle cx="22" cy="22" r="19" fill="none" class="stroke-dark-700" stroke-width="3.5" />
                  <circle cx="22" cy="22" r="19" fill="none"
                          :stroke="region.color" stroke-width="3.5"
                          :stroke-dasharray="region.percentage * 1.19 + ' 200'"
                          stroke-linecap="round" />
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-sm font-bold text-gray-200">{{ region.percentage }}%</span>
                </div>
              </div>
              <p class="text-xs text-gray-400">{{ region.name }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Education + Experience Distribution -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-200">主要城市学历要求分布</h3>
          <!-- 下拉框宽度 w-48，若文字溢出可改 w-56 -->
          <div class="relative" ref="cityFilterRef">
            <div @click="cityFilterOpen = !cityFilterOpen" class="glass-input cursor-pointer flex items-center justify-between px-3 py-1.5 text-sm w-48">
              <span :class="selectedCities.length > 0 ? 'text-gray-100' : 'text-gray-500'">
                {{ selectedCities.length > 0 ? selectedCities.join(', ') : '选择城市' }}
              </span>
              <svg class="w-4 h-4 text-gray-500 transition-transform flex-shrink-0" :class="{ 'rotate-180': cityFilterOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
            <div v-if="cityFilterOpen" class="absolute z-[100] mt-1 w-48 glass-card p-2 max-h-48 overflow-y-auto shadow-2xl">
              <div class="px-3 py-2 text-xs text-gray-500 border-b border-dark-600">全国（默认勾选）</div>
              <label v-for="city in cityOptions" :key="city" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
                <input type="checkbox" :value="city" :checked="selectedCities.includes(city)"
                       @change="toggleCityFilter(city)" :disabled="selectedCities.length >= 4 && !selectedCities.includes(city)"
                       class="rounded accent-primary-500" />
                <span class="text-sm text-gray-300">{{ city }}</span>
              </label>
            </div>
          </div>
        </div>
        <div v-if="loading" class="flex items-center justify-center" style="height:400px">
          <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else style="height:400px">
          <v-chart :key="'edu-' + chartKey" :option="educationBarOption" autoresize class="w-full h-full" />
        </div>
      </div>

      <div class="glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-200">主要城市经验要求分布</h3>
          <!-- 下拉框宽度 w-48，若文字溢出可改 w-56 -->
          <div class="relative" ref="expCityFilterRef">
            <div @click="expCityFilterOpen = !expCityFilterOpen" class="glass-input cursor-pointer flex items-center justify-between px-3 py-1.5 text-sm w-48">
              <span :class="selectedExpCities.length > 0 ? 'text-gray-100' : 'text-gray-500'">
                {{ selectedExpCities.length > 0 ? selectedExpCities.join(', ') : '选择城市' }}
              </span>
              <svg class="w-4 h-4 text-gray-500 transition-transform flex-shrink-0" :class="{ 'rotate-180': expCityFilterOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
            <div v-if="expCityFilterOpen" class="absolute z-[100] mt-1 w-48 glass-card p-2 max-h-48 overflow-y-auto shadow-2xl">
              <div class="px-3 py-2 text-xs text-gray-500 border-b border-dark-600">全国（默认勾选）</div>
              <label v-for="city in cityOptions" :key="city" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
                <input type="checkbox" :value="city" :checked="selectedExpCities.includes(city)"
                       @change="toggleExpCityFilter(city)" :disabled="selectedExpCities.length >= 4 && !selectedExpCities.includes(city)"
                       class="rounded accent-primary-500" />
                <span class="text-sm text-gray-300">{{ city }}</span>
              </label>
            </div>
          </div>
        </div>
        <div v-if="loading" class="flex items-center justify-center" style="height:400px">
          <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <div v-else style="height:400px">
          <v-chart :key="'exp-' + chartKey" :option="experienceBarOption" autoresize class="w-full h-full" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { use } from 'echarts/core'
import * as echarts from 'echarts/core'
import { BarChart, MapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, VisualMapComponent, GeoComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { analysisAPI } from '@/api'

use([BarChart, MapChart, GridComponent, TooltipComponent, LegendComponent, VisualMapComponent, GeoComponent, CanvasRenderer])

const loading = ref(false)
const provinceMapLoading = ref(true)
const cityMapLoading = ref(false)

const stats = reactive({
  totalCities: '--',
  cityType: '--',
  firstTierPercentage: '--',
  firstTierTopCity: '--',
  newFirstTierPercentage: '--',
  newFirstTierTopCity: '--',
  otherPercentage: '--',
  otherTopCity: '--'
})

const selectedProvince = ref('广东省')
const topN = ref(20)

const regionColors = {
  '华东地区': '#6366f1',
  '华北地区': '#14b8a6',
  '华南地区': '#f59e0b',
  '西南地区': '#8b5cf6',
  '华中地区': '#ec4899',
  '西北地区': '#3b82f6',
  '东北地区': '#10b981',
}
const regionData = ref([])
const leftColumnRegions = computed(() => regionData.value.slice(0, 4))
const rightColumnRegions = computed(() => regionData.value.slice(4, 7))

const cityOptions = ref([])
const selectedCities = ref(['北京', '上海', '广州', '深圳'])
const selectedExpCities = ref(['北京', '上海', '广州', '深圳'])
const cityFilterOpen = ref(false)
const expCityFilterOpen = ref(false)
const cityFilterRef = ref(null)
const expCityFilterRef = ref(null)

const colors = ['#6366f1', '#14b8a6', '#f59e0b', '#8b5cf6', '#ec4899', '#3b82f6', '#10b981', '#f97316']

// Single region entities: 直辖市(4) + 特别行政区(2) - no internal city map needed
const singleRegions = ['北京市', '上海市', '天津市', '重庆市', '香港特别行政区', '澳门特别行政区']

const provinceAdcode = {
  '北京市': 110000, '天津市': 120000, '河北省': 130000, '山西省': 140000,
  '内蒙古自治区': 150000, '辽宁省': 210000, '吉林省': 220000, '黑龙江省': 230000,
  '上海市': 310000, '江苏省': 320000, '浙江省': 330000, '安徽省': 340000,
  '福建省': 350000, '江西省': 360000, '山东省': 370000, '河南省': 410000,
  '湖北省': 420000, '湖南省': 430000, '广东省': 440000, '广西壮族自治区': 450000,
  '海南省': 460000, '重庆市': 500000, '四川省': 510000, '贵州省': 520000,
  '云南省': 530000, '西藏自治区': 540000, '陕西省': 610000, '甘肃省': 620000,
  '青海省': 630000, '宁夏回族自治区': 640000, '新疆维吾尔自治区': 650000,
  '香港特别行政区': 810000, '澳门特别行政区': 820000, '台湾省': 710000,
}

const provinceData = ref([])

const cityByProvince = ref({})

const cityTier = {
  '北京': '一线', '上海': '一线', '广州': '一线', '深圳': '一线',
  '成都': '新一线', '杭州': '新一线', '武汉': '新一线', '南京': '新一线',
  '重庆': '新一线', '苏州': '新一线', '西安': '新一线', '长沙': '新一线',
  '天津': '新一线', '郑州': '新一线', '东莞': '新一线', '青岛': '新一线',
  '合肥': '新一线', '佛山': '新一线', '宁波': '新一线', '昆明': '新一线',
  '沈阳': '新一线', '无锡': '新一线',
}

const tierColor = { '一线': '#6366f1', '新一线': '#10b981', '其他': '#f59e0b' }

const cityTopAllData = ref([])

const sortedCityData = computed(() => {
  return [...cityTopAllData.value].sort((a, b) => b.value - a.value).slice(0, topN.value)
})

const educationData = ref({})
const experienceData = ref({})
const maxProvinceValue = ref(5000)
const chartKey = ref(0)

const loadedProvinceMaps = new Set()

async function loadChinaMap() {
  try {
    const res = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    const geoJson = await res.json()
    echarts.registerMap('china', geoJson)
  } catch {
    console.warn('中国地图加载失败')
  }
  provinceMapLoading.value = false
}

async function loadProvinceMap(provinceName) {
  if (loadedProvinceMaps.has(provinceName)) return
  const adcode = provinceAdcode[provinceName]
  if (!adcode) return
  cityMapLoading.value = true
  const isSingle = singleRegions.includes(provinceName)
  // 直辖市/特别行政区用无区级地图（不含 _full），台湾省也无区级数据
  // 省份用 _full 含区级地图，若加载失败则降级为无区级
  const urls = isSingle
    ? [`https://geo.datav.aliyun.com/areas_v3/bound/${adcode}.json`]
    : [
        `https://geo.datav.aliyun.com/areas_v3/bound/${adcode}_full.json`,
        `https://geo.datav.aliyun.com/areas_v3/bound/${adcode}.json`,
      ]
  let success = false
  for (const url of urls) {
    try {
      const res = await fetch(url)
      if (!res.ok) continue
      const geoJson = await res.json()
      echarts.registerMap(`province_${adcode}`, geoJson)
      loadedProvinceMaps.add(provinceName)
      success = true
      break
    } catch { /* try next url */ }
  }
  if (!success) console.warn(`${provinceName}地图加载失败`)
  cityMapLoading.value = false
}

function onProvinceClick(params) {
  if (params.name && provinceAdcode[params.name]) {
    selectedProvince.value = params.name
  }
}

async function fetchLocationData() {
  loading.value = true
  try {
    const res = await analysisAPI.getLocationDistribution()
    const data = res.data

    // stats
    const s = data.statistics
    stats.totalCities = s.total_cities
    stats.firstTierPercentage = s.first_tier_ratio
    stats.firstTierTopCity = s.first_tier_top_city
    stats.newFirstTierPercentage = s.new_first_tier_ratio
    stats.newFirstTierTopCity = s.new_first_tier_top_city
    stats.otherPercentage = s.other_ratio
    stats.otherTopCity = s.other_top_city

    const ratios = [
      { name: s.first_tier_ratio, label: '一线' },
      { name: s.new_first_tier_ratio, label: '新一线' },
      { name: s.other_ratio, label: '其他' },
    ]
    ratios.sort((a, b) => b.name - a.name)
    stats.cityType = `以${ratios[0].label}城市为主`

    // regionData
    const partitionRatio = data.partition_distribution || s.location_partition_ratio || {}
    regionData.value = Object.entries(partitionRatio).map(([name, percentage]) => ({
      name,
      percentage,
      color: regionColors[name] || '#6c757d',
    }))

    // provinceData
    provinceData.value = data.province_distribution || []
    if (provinceData.value.length > 0) {
      maxProvinceValue.value = Math.max(...provinceData.value.map(p => p.value))
    }

    // cityByProvince
    cityByProvince.value = data.province_city_distribution || {}

    // cityTopAllData
    cityTopAllData.value = data.city_jobs_distribution || []

    // cityOptions for filters
    const eduCities = Object.keys(data.city_education_distribution || {}).filter(c => c !== '全国')
    cityOptions.value = eduCities

    // educationData
    educationData.value = data.city_education_distribution || {}

    // experienceData
    experienceData.value = data.city_experience_distribution || {}

    chartKey.value++
  } catch (e) {
    console.error('获取地区分布数据失败:', e)
  } finally {
    loading.value = false
  }
}

const provinceHeatmapOption = computed(() => {
  const maxVal = maxProvinceValue.value
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#343a40', fontSize: 13 },
      formatter: (p) => `<strong>${p.name}</strong><br/>岗位数量: <span style="color:#6366f1">${p.value}</span>`,
    },
    visualMap: {
      min: 0, max: maxVal, left: 15, top: 15,
      text: [String(maxVal), '0'],
      textStyle: { color: '#6c757d', fontSize: 11 },
      inRange: { color: ['#e8e8ff', '#c7d2fe', '#a5b4fc', '#818cf8', '#6366f1', '#4f46e5'] },
      calculable: true, itemWidth: 15, itemHeight: 120,
    },
    series: [{
      type: 'map', map: 'china', roam: true,
      itemStyle: { areaColor: '#f1f3f5', borderColor: '#dee2e6', borderWidth: 1 },
      emphasis: {
        itemStyle: { areaColor: '#818cf8' },
        label: { color: '#ffffff', fontSize: 13, fontWeight: 'bold' },
      },
      label: { show: true, fontSize: 10, color: '#6c757d' },
      data: provinceData.value,
      animationDuration: 1000,
    }],
  }
})

const cityHeatmapOption = computed(() => {
  const adcode = provinceAdcode[selectedProvince.value]
  const mapName = `province_${adcode}`
  const isSingle = singleRegions.includes(selectedProvince.value)
  const cities = isSingle
    ? [{ name: selectedProvince.value, value: provinceData.value.find(p => p.name === selectedProvince.value)?.value || 0 }]
    : cityByProvince.value[selectedProvince.value] || []
  const values = cities.map(c => c.value)
  const rawMin = values.length > 0 ? Math.min(...values) : 0
  const rawMax = values.length > 0 ? Math.max(...values) : 100
  const minVal = rawMin
  const maxVal = rawMin === rawMax ? rawMax + 10 : rawMax
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#343a40', fontSize: 13 },
      formatter: (p) => `<strong>${p.name}</strong><br/>岗位数量: <span style="color:#6366f1">${p.value}</span>`,
    },
    visualMap: {
      min: minVal, max: maxVal, left: 15, top: 15,
      text: [String(maxVal), String(minVal)],
      textStyle: { color: '#6c757d', fontSize: 11 },
      inRange: { color: ['#e6f7f0', '#a7f3d0', '#6ee7b7', '#34d399', '#10b981', '#059669'] },
      calculable: true, itemWidth: 15, itemHeight: 120,
    },
    series: [{
      type: 'map', map: mapName, roam: true,
      itemStyle: { areaColor: '#f1f3f5', borderColor: '#dee2e6', borderWidth: 1 },
      emphasis: {
        itemStyle: { areaColor: '#10b981' },
        label: { color: '#ffffff', fontSize: 13, fontWeight: 'bold' },
      },
      label: { show: true, fontSize: 10, color: '#6c757d' },
      data: cities,
      animationDuration: 800,
    }],
  }
})

const nameFontSize = computed(() => topN.value === 5 ? 15 : topN.value === 10 ? 14 : 12)
const tagFontSize = computed(() => topN.value === 5 ? 12 : topN.value === 10 ? 11 : 10)
const valueFontSize = computed(() => topN.value === 5 ? 13 : topN.value === 10 ? 12 : 11)

const cityRankBarOption = computed(() => {
  const data = sortedCityData.value
  const maxValue = data.length > 0 ? data[0].value : 100
  const nf = nameFontSize.value
  const tf = tagFontSize.value
  const vf = valueFontSize.value
  return {
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#343a40', fontSize: 13 },
      formatter: (params) => {
        const d = params[0]
        return `<strong>${d.name}</strong><br/>岗位数量: <span style="color:#6366f1">${d.value}</span>`
      },
    },
    grid: { left: 120, right: 30, top: 10, bottom: 4, containLabel: true },
    xAxis: {
      type: 'value', max: maxValue * 1.12,
      axisLabel: { color: '#adb5bd', fontSize: 11 },
      splitLine: { lineStyle: { color: '#e9ecef' } },
    },
    yAxis: {
      type: 'category',
      data: data.map(i => i.name).reverse(),
      axisLabel: {
         color: '#343a40', fontSize: nf, fontWeight: 500,
         width: 100, overflow: 'truncate',
         formatter: (name) => {
           const tier = cityTier[name] || '其他'
           if (tier === '一线') return `{name|${name}}  {tag1|一线}`
           if (tier === '新一线') return `{name|${name}}  {tag2|新一线}`
           return `{name|${name}}  {tag3|其他}`
         },
         rich: {
           name: { color: '#343a40', fontSize: nf, fontWeight: 500 },
           tag1: { color: '#ffffff', fontSize: tf, padding: [3.5, 6], borderRadius: 4, backgroundColor: '#6366f1' },  /* 标签方框 padding=[垂直,水平]，不够包字可调大 */
           tag2: { color: '#ffffff', fontSize: tf, padding: [3.5, 6], borderRadius: 4, backgroundColor: '#10b981' },
           tag3: { color: '#ffffff', fontSize: tf, padding: [3.5, 6], borderRadius: 4, backgroundColor: '#f59e0b' },
         },
       },
      axisLine: { show: false }, axisTick: { show: false },
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
      barWidth: '55%', animationDuration: 800,
      label: {
        show: true, position: 'right', color: '#6c757d', fontSize: vf,
        formatter: (p) => p.value,
      },
    }],
  }
})

const educationBarOption = computed(() => {
  const xData = ['学历不限', '大专', '本科', '统招本科', '硕士', '博士']
  const cities = ['全国', ...selectedCities.value]
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#343a40', fontSize: 12 },
      axisPointer: { type: 'shadow' },
    },
    legend: {
      data: cities, bottom: 0,
      textStyle: { color: '#6c757d', fontSize: 11 },
      icon: 'roundRect',
    },
    grid: { left: 55, right: 20, top: 45, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category', data: xData,
      axisLabel: { color: '#6c757d', fontSize: 11, interval: 0 },
      axisLine: { lineStyle: { color: '#dee2e6' } },
    },
    yAxis: {
      type: 'value', max: 100,
      name: '比例(%)', nameLocation: 'end', nameGap: 15,
       nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#6c757d', padding: [0, 0, 0, -30] },
       axisLabel: { color: '#adb5bd', fontSize: 11 },
       splitLine: { lineStyle: { color: '#e9ecef' } },
     },
     series: cities.map((city, idx) => ({
       name: city, type: 'bar', barWidth: 14,
       data: xData.map(item => (educationData.value[city]?.[item] ?? 0)),
      itemStyle: { color: colors[idx % colors.length], borderRadius: [2, 2, 0, 0] },
    })),
  }
})

const experienceBarOption = computed(() => {
  const xData = ['经验不限', '实习生', '应届生', '1-3年', '3-5年', '5-10年']
  const cities = ['全国', ...selectedExpCities.value]
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      textStyle: { color: '#343a40', fontSize: 12 },
      axisPointer: { type: 'shadow' },
    },
    legend: {
      data: cities, bottom: 0,
      textStyle: { color: '#6c757d', fontSize: 11 },
      icon: 'roundRect',
    },
    grid: { left: 55, right: 20, top: 45, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category', data: xData,
      axisLabel: { color: '#6c757d', fontSize: 11, interval: 0 },
      axisLine: { lineStyle: { color: '#dee2e6' } },
    },
    yAxis: {
      type: 'value', max: 100,
      name: '比例(%)', nameLocation: 'end', nameGap: 15,
      nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#6c757d', padding: [0, 0, 0, -30] },
      axisLabel: { color: '#adb5bd', fontSize: 11 },
      splitLine: { lineStyle: { color: '#e9ecef' } },
    },
    series: cities.map((city, idx) => ({
      name: city, type: 'bar', barWidth: 14,
      data: xData.map(item => (experienceData.value[city]?.[item] ?? 0)),
      itemStyle: { color: colors[idx % colors.length], borderRadius: [2, 2, 0, 0] },
    })),
  }
})

function toggleCityFilter(city) {
  const idx = selectedCities.value.indexOf(city)
  if (idx > -1) selectedCities.value.splice(idx, 1)
  else if (selectedCities.value.length < 4) selectedCities.value.push(city)
}

function toggleExpCityFilter(city) {
  const idx = selectedExpCities.value.indexOf(city)
  if (idx > -1) selectedExpCities.value.splice(idx, 1)
  else if (selectedExpCities.value.length < 4) selectedExpCities.value.push(city)
}

function handleClickOutside(e) {
  if (cityFilterRef.value && !cityFilterRef.value.contains(e.target)) cityFilterOpen.value = false
  if (expCityFilterRef.value && !expCityFilterRef.value.contains(e.target)) expCityFilterOpen.value = false
}

watch(selectedProvince, (newVal) => {
  if (newVal) loadProvinceMap(newVal)
})

onMounted(async () => {
  await fetchLocationData()
  loadChinaMap()
  loadProvinceMap('广东省')
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>