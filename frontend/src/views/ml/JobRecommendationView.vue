<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">岗位推荐</h1>
        <p class="text-gray-500 mt-1">基于您的技能和偏好，智能推荐最适合的岗位</p>
      </div>
    </div>

    <div class="glass-card p-5">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm text-gray-400 mb-2">技能关键词</label>
          <input v-model="preferences.skills" type="text" class="glass-input w-full" placeholder="例：Java, Python" />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">期望城市</label>
          <select v-model="preferences.city" class="glass-input w-full">
            <option value="">不限</option>
            <option>北京</option>
            <option>上海</option>
            <option>深圳</option>
            <option>杭州</option>
            <option>广州</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">薪资要求</label>
          <select v-model="preferences.salary" class="glass-input w-full">
            <option value="">不限</option>
            <option>10K-20K</option>
            <option>20K-30K</option>
            <option>30K-50K</option>
            <option>50K+</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-2">推荐数量</label>
          <select v-model="preferences.count" class="glass-input w-full">
            <option :value="5">5 条</option>
            <option :value="10">10 条</option>
            <option :value="20">20 条</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="getRecommendations" class="btn-primary w-full">获取推荐</button>
        </div>
      </div>
    </div>

    <div class="space-y-4">
      <div v-for="(job, idx) in recommendations" :key="idx"
           class="glass-card p-5 hover:border-primary-500/40 transition-all group animate-slide-up"
           :style="{ animationDelay: idx * 0.1 + 's' }">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-1">
              <h3 class="text-base font-semibold text-gray-200 group-hover:text-primary-400 transition-colors">{{ job.title }}</h3>
              <span class="px-2 py-0.5 rounded text-xs"
                    :class="job.matchScore >= 90 ? 'bg-green-500/10 text-green-400' : job.matchScore >= 80 ? 'bg-accent-500/10 text-accent-400' : 'bg-blue-500/10 text-blue-400'">
                {{ job.matchScore }}% 匹配
              </span>
            </div>
            <p class="text-sm text-gray-500 mb-2">{{ job.company }} · {{ job.location }}</p>
            <div class="flex items-center gap-4 text-xs text-gray-500">
              <span class="flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ job.salary }}
              </span>
              <span>{{ job.experience }}</span>
              <span>{{ job.education }}</span>
            </div>
            <div class="mt-3 flex items-center gap-2 flex-wrap">
              <span v-for="tag in job.tags" :key="tag"
                    class="px-2 py-0.5 rounded text-xs bg-dark-700 text-gray-400">{{ tag }}</span>
            </div>
            <div class="mt-3 flex items-center gap-2 text-xs">
              <span class="flex items-center gap-1 text-gray-500">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                距离 {{ job.distance }}
              </span>
            </div>
          </div>
          <div class="flex flex-col items-center gap-2 ml-4">
            <div class="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/20">
              <span class="text-lg font-bold text-white">{{ job.matchScore }}</span>
            </div>
            <button class="btn-secondary text-xs py-1 px-3">查看详情</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="recommendations.length === 0" class="glass-card p-12">
      <div class="text-center text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <p class="text-gray-400 text-lg mb-2">暂无推荐结果</p>
        <p class="text-sm">请设置偏好条件后获取推荐</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const preferences = reactive({
  skills: '',
  city: '',
  salary: '',
  count: 10,
})

const recommendations = ref([])

const sampleJobs = [
  { title: 'Java开发工程师', company: '字节跳动', location: '北京', salary: '30K-50K', experience: '3-5年', education: '本科', matchScore: 95, tags: ['Java', 'Spring Boot', '微服务', 'Redis'], distance: '3.2km' },
  { title: 'Python后端开发', company: '阿里巴巴', location: '杭州', salary: '25K-45K', experience: '3-5年', education: '本科', matchScore: 92, tags: ['Python', 'Django', 'Flask', 'PostgreSQL'], distance: '5.8km' },
  { title: 'Go开发工程师', company: '腾讯科技', location: '深圳', salary: '30K-55K', experience: '3-5年', education: '本科', matchScore: 88, tags: ['Go', '微服务', 'Docker', 'K8s'], distance: '2.1km' },
  { title: '高级Java架构师', company: '蚂蚁集团', location: '杭州', salary: '50K-80K', experience: '8年以上', education: '硕士', matchScore: 85, tags: ['Java', '分布式', '高并发', '架构设计'], distance: '4.5km' },
  { title: '全栈开发工程师', company: '美团', location: '北京', salary: '28K-45K', experience: '3-5年', education: '本科', matchScore: 82, tags: ['Vue', 'React', 'Node.js', 'MongoDB'], distance: '1.5km' },
  { title: 'C++开发工程师', company: '百度', location: '北京', salary: '28K-50K', experience: '3-5年', education: '本科', matchScore: 78, tags: ['C++', 'Linux', '网络编程', '多线程'], distance: '6.3km' },
  { title: 'Python数据分析师', company: '滴滴出行', location: '北京', salary: '20K-35K', experience: '1-3年', education: '本科', matchScore: 76, tags: ['Python', 'SQL', 'Pandas', '机器学习'], distance: '4.8km' },
]

function getRecommendations() {
  recommendations.value = sampleJobs
}
</script>
