<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">薪资分析</h1>
        <p class="text-gray-500 mt-1">薪资分布统计与趋势分析</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="stat-card">
        <p class="text-sm text-gray-500">平均月薪</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">¥18,500</p>
        <p class="text-xs text-green-400 mt-2">↑ 同比增长 12.5%</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">薪资中位数</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">¥15,800</p>
        <p class="text-xs text-gray-500 mt-2">50% 岗位在此之上</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">最高薪资</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">¥120,000</p>
        <p class="text-xs text-accent-400 mt-2">AI 算法岗</p>
      </div>
      <div class="stat-card">
        <p class="text-sm text-gray-500">薪资方差</p>
        <p class="text-2xl font-bold text-gray-100 mt-1">0.42</p>
        <p class="text-xs text-orange-400 mt-2">行业分化明显</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">各岗位平均薪资对比</h3>
        <div class="space-y-4">
          <div v-for="(item, idx) in salaryByCategory" :key="idx">
            <div class="flex items-center justify-between text-sm mb-1">
              <span class="text-gray-300">{{ item.name }}</span>
              <span class="text-gray-400">{{ item.salary }}</span>
            </div>
            <div class="h-2 bg-dark-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full" :class="item.color" :style="{ width: item.percentage + '%' }" />
            </div>
          </div>
        </div>
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">经验-薪资分布矩阵</h3>
        <div class="space-y-4">
          <div v-for="(exp, idx) in salaryByExperience" :key="idx"
               class="flex items-center justify-between p-3 rounded-xl bg-dark-800/50">
            <span class="text-sm text-gray-300 w-20">{{ exp.level }}</span>
            <div class="flex-1 mx-4">
              <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
                <span>{{ exp.min }}</span>
                <span class="text-gray-400 font-medium">{{ exp.avg }}</span>
                <span>{{ exp.max }}</span>
              </div>
              <div class="h-1.5 bg-dark-700 rounded-full overflow-hidden">
                <div class="h-full rounded-full bg-gradient-to-r from-primary-500 to-accent-500"
                     :style="{ width: exp.range + '%' }" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">学历对薪资影响</h3>
        <div class="space-y-3">
          <div v-for="edu in salaryByEducation" :key="edu.name"
               class="flex items-center justify-between p-2">
            <span class="text-sm text-gray-300">{{ edu.name }}</span>
            <div class="flex items-center gap-2">
              <div class="w-24 h-2 bg-dark-700 rounded-full overflow-hidden">
                <div class="h-full rounded-full bg-primary-500" :style="{ width: edu.ratio + '%' }" />
              </div>
              <span class="text-sm text-gray-400 w-16 text-right">{{ edu.salary }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">城市薪资排行 Top 5</h3>
        <div class="space-y-3">
          <div v-for="(city, idx) in topCities" :key="city.name"
               class="flex items-center justify-between p-2">
            <div class="flex items-center gap-3">
              <span class="text-xs text-gray-500 w-4">{{ idx + 1 }}</span>
              <span class="text-sm text-gray-300">{{ city.name }}</span>
            </div>
            <span class="text-sm font-medium text-gray-200">{{ city.salary }}</span>
          </div>
        </div>
      </div>

      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-gray-200 mb-4">行业薪资排行 Top 5</h3>
        <div class="space-y-3">
          <div v-for="(industry, idx) in topIndustries" :key="industry.name"
               class="flex items-center justify-between p-2">
            <div class="flex items-center gap-3">
              <span class="text-xs text-gray-500 w-4">{{ idx + 1 }}</span>
              <span class="text-sm text-gray-300">{{ industry.name }}</span>
            </div>
            <span class="text-sm font-medium text-gray-200">{{ industry.salary }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const salaryByCategory = [
  { name: '算法工程师', salary: '¥45,000', percentage: 100, color: 'bg-gradient-to-r from-primary-500 to-primary-400' },
  { name: 'Go开发', salary: '¥32,000', percentage: 71, color: 'bg-gradient-to-r from-accent-500 to-accent-400' },
  { name: 'C++开发', salary: '¥28,000', percentage: 62, color: 'bg-gradient-to-r from-blue-500 to-blue-400' },
  { name: 'Java开发', salary: '¥25,000', percentage: 56, color: 'bg-gradient-to-r from-purple-500 to-purple-400' },
  { name: 'Python开发', salary: '¥23,000', percentage: 51, color: 'bg-gradient-to-r from-orange-500 to-orange-400' },
  { name: '前端开发', salary: '¥20,000', percentage: 44, color: 'bg-gradient-to-r from-pink-500 to-pink-400' },
]

const salaryByExperience = [
  { level: '应届', min: '8K', avg: '12K', max: '18K', range: 30 },
  { level: '1-3年', min: '12K', avg: '18K', max: '28K', range: 50 },
  { level: '3-5年', min: '20K', avg: '30K', max: '45K', range: 70 },
  { level: '5-10年', min: '30K', avg: '45K', max: '70K', range: 85 },
  { level: '10年+', min: '45K', avg: '65K', max: '100K+', range: 100 },
]

const salaryByEducation = [
  { name: '博士', salary: '¥45,000', ratio: 100 },
  { name: '硕士', salary: '¥35,000', ratio: 78 },
  { name: '本科', salary: '¥22,000', ratio: 49 },
  { name: '大专', salary: '¥15,000', ratio: 33 },
  { name: '学历不限', salary: '¥12,000', ratio: 27 },
]

const topCities = [
  { name: '北京', salary: '¥26,000' },
  { name: '上海', salary: '¥25,000' },
  { name: '深圳', salary: '¥24,500' },
  { name: '杭州', salary: '¥22,000' },
  { name: '广州', salary: '¥19,000' },
]

const topIndustries = [
  { name: '人工智能', salary: '¥45,000' },
  { name: '金融科技', salary: '¥38,000' },
  { name: '互联网/IT', salary: '¥28,000' },
  { name: '游戏开发', salary: '¥26,000' },
  { name: '信息安全', salary: '¥25,000' },
]
</script>
