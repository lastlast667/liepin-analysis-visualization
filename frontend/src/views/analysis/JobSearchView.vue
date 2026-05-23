<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">岗位搜索</h1>
        <p class="text-gray-500 mt-1">多条件精准搜索招聘岗位</p>
      </div>
      <div class="text-sm text-gray-500">
        共找到 <span class="text-primary-400 font-semibold">{{ totalResults }}</span> 个岗位
      </div>
    </div>

    <div class="glass-card p-5">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm text-gray-400 mb-2">关键词</label>
          <input v-model="filters.keyword" type="text" class="glass-input w-full" placeholder="岗位名称/技能" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">城市</label>
          <input v-model="filters.city" type="text" class="glass-input w-full" placeholder="城市" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">薪资范围</label>
          <select v-model="filters.salary" class="glass-input w-full">
            <option value="">不限</option>
            <option value="0-10K">10K以下</option>
            <option value="10-20K">10K-20K</option>
            <option value="20-30K">20K-30K</option>
            <option value="30-50K">30K-50K</option>
            <option value="50K+">50K以上</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">经验要求</label>
          <select v-model="filters.experience" class="glass-input w-full">
            <option value="">不限</option>
            <option value="应届">应届</option>
            <option value="1-3年">1-3年</option>
            <option value="3-5年">3-5年</option>
            <option value="5-10年">5-10年</option>
            <option value="10年+">10年以上</option>
          </select>
        </div>
        <div class="flex items-end gap-2">
          <button @click="searchJobs" class="btn-primary flex-1">搜索</button>
          <button @click="resetFilters" class="btn-secondary px-4">重置</button>
        </div>
      </div>
    </div>

    <div class="glass-card">
      <div class="p-4 border-b border-dark-700/50 flex items-center justify-between">
        <div class="flex gap-1">
          <button v-for="tab in tabs" :key="tab"
                  @click="activeTab = tab"
                  class="px-4 py-2 rounded-lg text-sm transition-all duration-300"
                  :class="activeTab === tab ? 'bg-primary-600/20 text-primary-400' : 'text-gray-500 hover:text-gray-300'">
            {{ tab }}
          </button>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">排序：</span>
          <select v-model="sortBy" class="glass-input text-sm py-1.5">
            <option value="default">默认</option>
            <option value="salary">薪资</option>
            <option value="time">更新时间</option>
          </select>
        </div>
      </div>

      <div class="divide-y divide-dark-700/30">
        <div v-for="(job, idx) in jobList" :key="idx"
             class="p-5 hover:bg-dark-800/30 transition-colors cursor-pointer group">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-1">
                <h3 class="text-base font-semibold text-gray-200 group-hover:text-primary-400 transition-colors">{{ job.title }}</h3>
                <span class="px-2 py-0.5 rounded text-xs bg-dark-700 text-gray-400">{{ job.category }}</span>
              </div>
              <p class="text-sm text-gray-500 mb-2">{{ job.company }} · {{ job.location }}</p>
              <div class="flex items-center gap-3 text-xs text-gray-500">
                <span class="flex items-center gap-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ job.salary }}
                </span>
                <span>{{ job.experience }}</span>
                <span>{{ job.education }}</span>
                <span>{{ job.updateTime }}</span>
              </div>
            </div>
            <button class="p-2 rounded-lg hover:bg-dark-700 text-gray-500 hover:text-primary-400 opacity-0 group-hover:opacity-100 transition-all">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const filters = reactive({
  keyword: '',
  city: '',
  salary: '',
  experience: '',
})
const activeTab = ref('全部')
const sortBy = ref('default')
const totalResults = ref(12847)

const tabs = ['全部', 'Java开发', 'Python开发', 'Go开发', 'C++开发', '前端']

const jobList = ref([
  { title: '高级Java开发工程师', company: '字节跳动', location: '北京', salary: '35K-60K', experience: '5-10年', education: '本科', category: 'Java开发', updateTime: '2小时前' },
  { title: 'Python后端开发', company: '阿里巴巴', location: '杭州', salary: '25K-45K', experience: '3-5年', education: '本科', category: 'Python开发', updateTime: '3小时前' },
  { title: 'Go开发工程师', company: '腾讯科技', location: '深圳', salary: '30K-50K', experience: '3-5年', education: '本科', category: 'Go开发', updateTime: '5小时前' },
  { title: 'C++开发工程师（搜索方向）', company: '百度', location: '北京', salary: '28K-45K', experience: '3-5年', education: '硕士', category: 'C++开发', updateTime: '6小时前' },
  { title: '前端架构师', company: '美团', location: '北京', salary: '40K-65K', experience: '5-10年', education: '本科', category: '前端', updateTime: '8小时前' },
  { title: 'Python数据分析师', company: '蚂蚁集团', location: '杭州', salary: '20K-35K', experience: '1-3年', education: '本科', category: 'Python开发', updateTime: '10小时前' },
  { title: 'Java开发（中间件方向）', company: '华为', location: '深圳', salary: '30K-55K', experience: '5-10年', education: '本科', category: 'Java开发', updateTime: '12小时前' },
  { title: 'Go开发（微服务方向）', company: '字节跳动', location: '上海', salary: '35K-60K', experience: '3-5年', education: '本科', category: 'Go开发', updateTime: '1天前' },
])

function searchJobs() {
  console.log('Search with:', filters)
}

function resetFilters() {
  filters.keyword = ''
  filters.city = ''
  filters.salary = ''
  filters.experience = ''
}
</script>
