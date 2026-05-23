<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">简历匹配</h1>
        <p class="text-gray-500 mt-1">上传简历，智能匹配最适合您的岗位</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <div class="lg:col-span-2">
        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">简历上传</h3>
          <div class="border-2 border-dashed border-dark-600 rounded-xl p-8 text-center hover:border-primary-500/50 transition-colors cursor-pointer group"
               @click="triggerUpload">
            <svg class="w-12 h-12 mx-auto mb-4 text-gray-600 group-hover:text-primary-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p class="text-gray-400 group-hover:text-gray-300">点击上传简历</p>
            <p class="text-xs text-gray-600 mt-2">支持 PDF、Word 格式</p>
            <input ref="fileInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="handleFileUpload" />
          </div>

          <div v-if="uploadedFile" class="mt-4 p-3 rounded-xl bg-dark-800/50 flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-300 truncate">{{ uploadedFile.name }}</p>
              <p class="text-xs text-gray-500">{{ (uploadedFile.size / 1024).toFixed(1) }} KB</p>
            </div>
            <button @click="removeFile" class="p-1 hover:text-red-400 text-gray-500">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="mt-6 space-y-4">
            <div>
              <label class="block text-sm text-gray-400 mb-2">期望岗位</label>
              <input v-model="matchForm.targetPosition" type="text" class="glass-input w-full" placeholder="例：Java开发工程师" />
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">期望城市</label>
              <input v-model="matchForm.targetCity" type="text" class="glass-input w-full" placeholder="例：北京" />
            </div>
            <button @click="startMatching" :disabled="!uploadedFile" class="btn-primary w-full">开始匹配</button>
          </div>
        </div>
      </div>

      <div class="lg:col-span-3">
        <div class="glass-card p-6 mb-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">匹配结果</h3>
          <div v-if="!hasMatched" class="flex flex-col items-center justify-center h-64 text-gray-500">
            <svg class="w-16 h-16 mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>上传简历并开始匹配</p>
          </div>
          <div v-else class="space-y-4">
            <div v-for="(match, idx) in matchResults" :key="idx"
                 class="p-4 rounded-xl bg-dark-800/50 border border-dark-700/50 hover:border-accent-500/30 transition-all">
              <div class="flex items-start justify-between mb-2">
                <div>
                  <h4 class="text-base font-semibold text-gray-200">{{ match.title }}</h4>
                  <p class="text-sm text-gray-500">{{ match.company }} · {{ match.location }}</p>
                </div>
                <div class="text-center">
                  <div class="w-14 h-14 rounded-full bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center">
                    <span class="text-lg font-bold text-white">{{ match.score }}%</span>
                  </div>
                  <span class="text-xs text-gray-500 mt-1 block">匹配度</span>
                </div>
              </div>
              <div class="flex items-center gap-4 text-xs text-gray-500">
                <span class="flex items-center gap-1">
                  <svg class="w-3.5 h-3.5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ match.salary }}
                </span>
                <span>{{ match.experience }}</span>
                <span>{{ match.education }}</span>
              </div>
              <div class="mt-3 flex items-center gap-2">
                <span v-for="tag in match.tags" :key="tag"
                      class="px-2 py-0.5 rounded text-xs bg-dark-700 text-gray-400">{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fileInput = ref(null)
const uploadedFile = ref(null)
const hasMatched = ref(false)

const matchForm = ref({
  targetPosition: '',
  targetCity: '',
})

const matchResults = ref([
  { title: 'Java开发工程师', company: '字节跳动', location: '北京', salary: '30K-50K', experience: '3-5年', education: '本科', score: 92, tags: ['Java', 'Spring Boot', '微服务', 'MySQL'] },
  { title: '高级Java开发', company: '阿里巴巴', location: '杭州', salary: '35K-55K', experience: '5-10年', education: '本科', score: 85, tags: ['Java', '分布式', '高并发', 'Redis'] },
  { title: 'Java后端工程师', company: '美团', location: '北京', salary: '28K-45K', experience: '3-5年', education: '本科', score: 78, tags: ['Java', 'Spring', 'MyBatis'] },
])

function triggerUpload() {
  fileInput.value.click()
}

function handleFileUpload(e) {
  const file = e.target.files[0]
  if (file) {
    uploadedFile.value = file
  }
}

function removeFile() {
  uploadedFile.value = null
  hasMatched.value = false
}

function startMatching() {
  hasMatched.value = true
}
</script>
