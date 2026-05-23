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
        <p class="text-2xl font-bold text-gray-100 mt-1">32</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">一线城市占比</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">58.3%</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">新一线城市占比</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">28.7%</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">其他城市占比</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">13.0%</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">城市岗位数量分布</h3>
        <div class="space-y-3">
          <div v-for="(city, idx) in cityData" :key="idx" class="flex items-center gap-4">
            <span class="text-sm text-gray-500 w-8">{{ idx + 1 }}</span>
            <div class="flex items-center gap-2 w-24">
              <span class="text-sm font-medium text-gray-200">{{ city.name }}</span>
              <span v-if="city.tag" class="px-1.5 py-0.5 rounded text-xs" :class="city.tag === '一线' ? 'bg-primary-500/10 text-primary-400' : 'bg-accent-500/10 text-accent-400'">{{ city.tag }}</span>
            </div>
            <div class="flex-1 h-3 bg-dark-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full" :class="city.barColor" :style="{ width: city.percentage + '%' }" />
            </div>
            <span class="text-sm text-gray-400 w-20 text-right">{{ city.count }}</span>
          </div>
        </div>
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">区域分布</h3>
        <div class="space-y-6 pt-4">
          <div v-for="region in regionData" :key="region.name" class="text-center">
            <div class="relative w-24 h-24 mx-auto mb-3">
              <svg class="w-24 h-24 -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.5" fill="none" class="stroke-dark-700" stroke-width="3" />
                <circle cx="18" cy="18" r="15.5" fill="none"
                        :stroke="region.color" stroke-width="3"
                        :stroke-dasharray="region.percentage * 0.97 + ' 100'"
                        stroke-linecap="round" />
              </svg>
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-lg font-bold text-gray-200">{{ region.percentage }}%</span>
              </div>
            </div>
            <p class="text-sm text-gray-400">{{ region.name }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="glass-card p-6">
      <h3 class="text-lg font-semibold text-gray-200 mb-4">省份分布</h3>
      <div class="flex items-center justify-center h-64">
        <div class="text-center text-gray-500">
          <svg class="w-16 h-16 mx-auto mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <p>中国地图加载区域</p>
          <p class="text-xs mt-1">将使用 ECharts 地图渲染</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const cityData = [
  { name: '北京', tag: '一线', percentage: 100, count: '3,245', barColor: 'bg-gradient-to-r from-primary-500 to-primary-400' },
  { name: '上海', tag: '一线', percentage: 92, count: '2,986', barColor: 'bg-gradient-to-r from-primary-500 to-primary-400' },
  { name: '深圳', tag: '一线', percentage: 85, count: '2,758', barColor: 'bg-gradient-to-r from-primary-500 to-primary-400' },
  { name: '杭州', tag: '新一线', percentage: 65, count: '2,109', barColor: 'bg-gradient-to-r from-accent-500 to-accent-400' },
  { name: '广州', tag: '一线', percentage: 60, count: '1,947', barColor: 'bg-gradient-to-r from-primary-500 to-primary-400' },
  { name: '成都', tag: '新一线', percentage: 48, count: '1,558', barColor: 'bg-gradient-to-r from-accent-500 to-accent-400' },
  { name: '武汉', tag: '新一线', percentage: 35, count: '1,136', barColor: 'bg-gradient-to-r from-accent-500 to-accent-400' },
  { name: '南京', tag: '新一线', percentage: 30, count: '973', barColor: 'bg-gradient-to-r from-accent-500 to-accent-400' },
  { name: '西安', tag: '新一线', percentage: 22, count: '714', barColor: 'bg-gradient-to-r from-accent-500 to-accent-400' },
  { name: '长沙', tag: '新一线', percentage: 15, count: '487', barColor: 'bg-gradient-to-r from-accent-500 to-accent-400' },
]

const regionData = [
  { name: '华东地区', percentage: 38, color: '#6366f1' },
  { name: '华北地区', percentage: 28, color: '#14b8a6' },
  { name: '华南地区', percentage: 20, color: '#f59e0b' },
  { name: '西南地区', percentage: 8, color: '#8b5cf6' },
  { name: '其他地区', percentage: 6, color: '#ec4899' },
]
</script>
