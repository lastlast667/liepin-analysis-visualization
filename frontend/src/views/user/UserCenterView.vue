<template>
  <div class="space-y-6 animate-fade-in">
    <!-- ==================== 非详情视图：原有内容 ==================== -->
    <template v-if="!detailView">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-100">用户中心</h1>
          <p class="text-gray-500 mt-1">管理您的收藏、浏览记录和个人信息</p>
        </div>
      </div>

      <!-- 顶部标签切换 -->
      <div class="flex gap-1 rounded-xl bg-dark-800/50 p-1 w-fit">
        <button v-for="tab in tabs" :key="tab.key"
                @click="activeTab = tab.key"
                class="px-5 py-2 rounded-lg text-sm font-medium transition-all duration-300"
                :class="activeTab.key === tab.key ? 'bg-dark-700 text-gray-200 shadow-sm' : 'text-gray-500 hover:text-gray-300'">
          {{ tab.label }}
        </button>
      </div>

      <!-- ===== 我的收藏 ===== -->
      <div v-if="activeTab === 'favorites'">
        <JobList
          v-if="favorites.length > 0"
          :jobs="favorites"
          :total-count="favorites.length"
          :total-pages="1"
          :current-page="1"
          :favorite-ids="favoriteIdSet"
          @view-job="goJobDetail"
          @toggle-favorite="removeFavorite"
        />
        <div v-else class="glass-card p-6">
          <div class="flex flex-col items-center justify-center h-48 text-gray-500">
            <svg class="w-12 h-12 mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
            <p>还没有收藏任何岗位</p>
            <router-link to="/analysis/jobs" class="text-sm text-primary-400 mt-2 hover:underline">去搜索岗位</router-link>
          </div>
        </div>
      </div>

      <!-- ===== 浏览历史 ===== -->
      <div v-if="activeTab === 'history'">
        <JobList
          v-if="browseHistory.length > 0"
          :jobs="browseHistory"
          :total-count="browseHistory.length"
          :total-pages="1"
          :current-page="1"
          :favorite-ids="favoriteIdSet"
          @view-job="goJobDetail"
          @toggle-favorite="toggleFavorite"
        />
        <div v-else class="glass-card p-6">
          <div class="flex flex-col items-center justify-center h-48 text-gray-500">
            <svg class="w-12 h-12 mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>还没有浏览过岗位</p>
            <router-link to="/analysis/jobs" class="text-sm text-primary-400 mt-2 hover:underline">去搜索岗位</router-link>
          </div>
        </div>
      </div>

      <!-- ===== 个人资料 ===== -->
      <div v-if="activeTab === 'profile'" class="max-w-2xl">
        <div v-if="saveSuccess" class="mb-4 px-4 py-3 rounded-xl bg-green-500/10 text-green-400 text-sm border border-green-500/20">
          个人资料已更新
        </div>

        <div class="glass-card p-6">
          <template v-if="!isEditing">
            <div class="flex items-start justify-between mb-6">
              <div class="flex items-center gap-4">
                <div class="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-2xl font-bold text-white">
                  {{ profile.username.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <h2 class="text-xl font-semibold text-gray-100">{{ profile.username }}</h2>
                  <p class="text-sm text-gray-500">{{ profile.email || '未设置邮箱' }}</p>
                </div>
              </div>
            </div>

            <div class="space-y-5">
              <div>
                <p class="text-sm text-gray-500 mb-2">目标城市</p>
                <div v-if="profile.target_city_list && profile.target_city_list.length > 0" class="flex flex-wrap gap-2">
                  <span v-for="city in profile.target_city_list" :key="city"
                        class="px-3 py-1 rounded-lg text-sm bg-primary-500/10 text-primary-400 border border-primary-500/20">
                    {{ city }}
                  </span>
                </div>
                <p v-else class="text-sm text-gray-600">暂未设置</p>
              </div>

              <div>
                <p class="text-sm text-gray-500 mb-2">目标岗位类别</p>
                <div v-if="profile.target_category_list && profile.target_category_list.length > 0" class="flex flex-wrap gap-2">
                  <span v-for="cat in profile.target_category_list" :key="cat"
                        class="px-3 py-1 rounded-lg text-sm bg-accent-500/10 text-accent-400 border border-accent-500/20">
                    {{ cat }}
                  </span>
                </div>
                <p v-else class="text-sm text-gray-600">暂未设置</p>
              </div>
            </div>

            <div class="flex justify-end mt-6 pt-4 border-t border-dark-700/50">
              <button @click="isEditing = true" class="px-5 py-2 rounded-xl bg-primary-600 text-white hover:bg-primary-500 transition-all text-sm font-medium">
                编辑个人信息
              </button>
            </div>
          </template>

          <template v-else>
            <h3 class="text-lg font-semibold text-gray-200 mb-6">编辑个人信息</h3>
            <div class="space-y-5">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm text-gray-400 mb-2">用户名</label>
                  <input v-model="editForm.username" type="text" class="glass-input w-full" />
                </div>
                <div>
                  <label class="block text-sm text-gray-400 mb-2">邮箱</label>
                  <input v-model="editForm.email" type="email" class="glass-input w-full" />
                </div>
              </div>

              <div>
                <label class="block text-sm text-gray-400 mb-2">目标城市（可多选）</label>
                <div class="relative" ref="citySelectRef">
                  <div @click="cityOpen = !cityOpen" class="glass-input w-full cursor-pointer flex items-center justify-between">
                    <span class="truncate text-sm" :class="editForm.target_city.length > 0 ? 'text-gray-100' : 'text-gray-500'">
                      {{ editForm.target_city.length > 0 ? editForm.target_city.join('、') : '请选择城市' }}
                    </span>
                    <svg class="w-4 h-4 text-gray-500 transition-transform" :class="{ 'rotate-180': cityOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                  <div v-if="cityOpen" class="absolute z-[100] mt-1 w-full glass-card p-2 max-h-48 overflow-y-auto shadow-2xl">
                    <label v-for="c in options.cities" :key="c" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
                      <input type="checkbox" :value="c" v-model="editForm.target_city" class="rounded accent-primary-500" />
                      <span class="text-sm text-gray-300">{{ c }}</span>
                    </label>
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-sm text-gray-400 mb-2">目标岗位类别（可多选）</label>
                <div class="relative" ref="catSelectRef">
                  <div @click="catOpen = !catOpen" class="glass-input w-full cursor-pointer flex items-center justify-between">
                    <span class="truncate text-sm" :class="editForm.target_category.length > 0 ? 'text-gray-100' : 'text-gray-500'">
                      {{ editForm.target_category.length > 0 ? editForm.target_category.join('、') : '请选择岗位类别' }}
                    </span>
                    <svg class="w-4 h-4 text-gray-500 transition-transform" :class="{ 'rotate-180': catOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                  <div v-if="catOpen" class="absolute z-[100] mt-1 w-full glass-card p-2 max-h-48 overflow-y-auto shadow-2xl">
                    <label v-for="cat in options.categories" :key="cat" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
                      <input type="checkbox" :value="cat" v-model="editForm.target_category" class="rounded accent-primary-500" />
                      <span class="text-sm text-gray-300">{{ cat }}</span>
                    </label>
                  </div>
                </div>
              </div>

              <hr class="border-dark-700/50" />
              <h3 class="text-base font-semibold text-gray-200">修改密码</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm text-gray-400 mb-2">当前密码</label>
                  <input v-model="passwordForm.old_password" type="password" class="glass-input w-full" />
                </div>
                <div>
                  <label class="block text-sm text-gray-400 mb-2">新密码</label>
                  <input v-model="passwordForm.new_password" type="password" class="glass-input w-full" />
                </div>
                <div>
                  <label class="block text-sm text-gray-400 mb-2">确认新密码</label>
                  <input v-model="passwordForm.confirm_password" type="password" class="glass-input w-full" />
                </div>
              </div>
              <p v-if="passwordError" class="text-sm text-red-400">{{ passwordError }}</p>

              <div class="flex justify-end gap-3 pt-2">
                <button @click="cancelEdit" class="px-5 py-2.5 rounded-xl bg-dark-700 text-gray-300 hover:bg-dark-600 transition-all text-sm font-medium">取消</button>
                <button @click="changePassword" class="px-5 py-2.5 rounded-xl bg-dark-700 text-gray-300 hover:bg-dark-600 transition-all text-sm font-medium">修改密码</button>
                <button @click="saveProfile" class="px-5 py-2.5 rounded-xl bg-primary-600 text-white hover:bg-primary-500 transition-all text-sm font-medium">保存修改</button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </template>

    <!-- ==================== 详情视图 ==================== -->
    <template v-else-if="detailView === 'detail' && selectedJob">
      <div>
        <button @click="backToResults" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-primary-400 transition-colors mb-4">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ detailReturnLabel }}
        </button>
      </div>
      <JobDetail
        :job="selectedJob"
        :company-stats="jobDetailCompanyStats"
        :similar-jobs="similarJobs"
        :salary-analysis="salaryAnalysis"
        :is-favorited="isFavorited(selectedJob.id)"
        @toggle-favorite="toggleFavorite"
        @view-company="goCompanyDetail"
        @view-job="goJobDetail"
      />
    </template>

    <!-- ==================== 公司详情视图 ==================== -->
    <template v-else-if="detailView === 'company' && selectedCompany">
      <div>
        <button @click="backToResults" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-primary-400 transition-colors mb-4">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回岗位详情
        </button>
      </div>
      <CompanyDetail
        :company-name="selectedCompany"
        :company-jobs="companyJobs"
        :company-stats="companyDetailStats"
        @view-job="goJobDetail"
        @back="backToResults"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { authAPI, mlAPI, analysisAPI } from '@/api/index.js'
import JobList from '@/components/job/JobList.vue'
import JobDetail from '@/components/job/JobDetail.vue'
import CompanyDetail from '@/components/job/CompanyDetail.vue'

const activeTab = ref('favorites')
const isEditing = ref(false)
const saveSuccess = ref(false)

const tabs = [
  { key: 'favorites', label: '我的收藏' },
  { key: 'history', label: '浏览历史' },
  { key: 'profile', label: '个人资料' },
]

// ── 收藏 / 浏览历史 ──
const favorites = ref([])
const browseHistory = ref([])
const favoriteMap = ref({})  // { jobId: favoriteRecordId }
const favoriteIdSet = computed(() => new Set(Object.keys(favoriteMap.value).map(Number)))

function isFavorited(jobId) {
  return jobId in favoriteMap.value
}

// ── 详情视图 ──
const detailView = ref(null)           // null=列表, 'detail'=详情, 'company'=公司详情
const detailReturnLabel = ref('返回收藏列表')
const selectedCompany = ref('')
const companyJobs = ref([])
const companyDetailStats = ref({ jobCount: 0, recruitTotal: 0, avgSalary: '--' })
const selectedJob = ref(null)
const jobDetailCompanyStats = ref({ jobCount: 0, recruitTotal: 0, avgSalary: '--' })
const similarJobs = ref([])
const salaryAnalysis = ref({
  industryAvg: '--', abovePercentage: 0,
  rangeMin: '--', rangeMax: '--', positionPercentage: 50,
})

// ── 个人资料（视图模式） ──
const profile = reactive({
  username: '',
  email: '',
  target_city_list: [],
  target_category_list: [],
})

// ── 编辑表单 ──
const editForm = reactive({
  username: '',
  email: '',
  target_city: [],
  target_category: [],
})

// ── 密码 ──
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})
const passwordError = ref('')

// ── 下拉选项 ──
const options = reactive({
  cities: [],
  categories: [],
})

// ── 下拉面板状态 ──
const cityOpen = ref(false)
const catOpen = ref(false)
const citySelectRef = ref(null)
const catSelectRef = ref(null)

// ── 数据加载 ──
async function fetchFavorites() {
  try {
    const res = await authAPI.getFavorites()
    const map = {}
    favorites.value = (res.data || []).map(f => {
      map[f.job.id] = f.id
      return {
        ...f.job,
        _favorite_record_id: f.id,
        is_favorited: true,
        _display_time: f.createdAt,
      }
    })
    favoriteMap.value = { ...favoriteMap.value, ...map }
  } catch (e) { console.error('加载收藏失败', e) }
}

async function fetchBrowseHistory() {
  try {
    const res = await authAPI.getBrowseHistory()
    browseHistory.value = (res.data || []).map(h => ({
      ...h.job,
      _display_time: h.browseTime,
    }))
  } catch (e) { console.error('加载浏览历史失败', e) }
}

async function fetchProfile() {
  try {
    const res = await authAPI.getProfile()
    const d = res.data
    profile.username = d.username || ''
    profile.email = d.email || ''
    profile.target_city_list = (d.expectedCity || '').split(',').filter(Boolean)
    profile.target_category_list = (d.expectedCategory || '').split(',').filter(Boolean)

    editForm.username = d.username || ''
    editForm.email = d.email || ''
    editForm.target_city = [...profile.target_city_list]
    editForm.target_category = [...profile.target_category_list]
  } catch (e) { console.error('加载资料失败', e) }
}

async function fetchOptions() {
  try {
    const res = await mlAPI.getMatchOptions()
    options.cities = res.data.cities || []
    options.categories = res.data.categories || []
  } catch (e) { console.error('加载选项失败', e) }
}

// ── 收藏操作 ──
async function removeFavorite(job) {
  try {
    const recordId = job._favorite_record_id || favoriteMap.value[job.id]
    if (recordId) await authAPI.removeFavorite(recordId)
    favorites.value = favorites.value.filter(f => f.id !== job.id)
    const newMap = { ...favoriteMap.value }
    delete newMap[job.id]
    favoriteMap.value = newMap
  } catch (e) { console.error('取消收藏失败', e) }
}

async function toggleFavorite(job) {
  if (isFavorited(job.id)) {
    const recordId = favoriteMap.value[job.id]
    await authAPI.removeFavorite(recordId)
    const newMap = { ...favoriteMap.value }
    delete newMap[job.id]
    favoriteMap.value = newMap
    // 同步更新浏览历史列表中的 is_favorited 状态
    const bhItem = browseHistory.value.find(h => h.id === job.id)
    if (bhItem) bhItem.is_favorited = false
  } else {
    const res = await authAPI.addFavorite({ job_id: job.id })
    favoriteMap.value = { ...favoriteMap.value, [job.id]: res.data.id }
    const bhItem = browseHistory.value.find(h => h.id === job.id)
    if (bhItem) bhItem.is_favorited = true
  }
}

// ── 岗位详情 ──
async function goJobDetail(job) {
  try {
    const res = await analysisAPI.getJobDetail(job.id)
    const data = res.data

    selectedJob.value = data

    /* 公司统计 —— snake_case → camelCase + 单位转换 */
    jobDetailCompanyStats.value = {
      jobCount: data.companyStats?.jobCount || 0,
      recruitTotal: data.companyStats?.recruitTotal || 0,
      avgSalary: data.companyStats?.avgSalary
        ? (data.companyStats.avgSalary / 1000).toFixed(1) + 'k'
        : '--',
    }

    similarJobs.value = data.similarJobs || []

    /* 薪资分析 —— snake_case → camelCase + 单位转换 + 计算位置百分比 */
    const sa = data.salaryAnalysis || {}
    const rangeMin = sa.rangeMin || 0
    const rangeMax = sa.rangeMax || 0
    const currentSalary = data.monthSalaryAvg || 0
    const position = rangeMax > rangeMin
      ? ((currentSalary - rangeMin) / (rangeMax - rangeMin)) * 100
      : 50

    salaryAnalysis.value = {
      industryAvg: sa.industryAvg ? (sa.industryAvg / 1000).toFixed(1) + 'k' : '--',
      abovePercentage: sa.abovePercentage ?? 0,
      rangeMin: rangeMin ? (rangeMin / 1000).toFixed(0) + 'k' : '--',
      rangeMax: rangeMax ? (rangeMax / 1000).toFixed(0) + 'k' : '--',
      positionPercentage: Math.min(100, Math.max(0, position)),
    }

    detailReturnLabel.value = activeTab.value === 'favorites' ? '返回收藏列表' : '返回浏览历史'
    detailView.value = 'detail'
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (e) {
    console.error('加载岗位详情失败', e)
  }
}

async function goCompanyDetail(companyName) {
  selectedCompany.value = companyName
  await loadCompanyJobs(companyName)
  detailView.value = 'company'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function loadCompanyJobs(companyName) {
  try {
    const res = await analysisAPI.searchJobs({
      company_name: companyName,
      page: 1,
      page_size: 200,
    })
    const jobs = res.data.results || []
    companyJobs.value = jobs

    const jc = jobs.length
    const rt = jobs.reduce((s, j) => s + (j.recruitCountParsed || 1), 0)
    const salaries = jobs.map(j => j.monthSalaryAvg).filter(Boolean)
    const avg = salaries.length > 0
      ? salaries.reduce((s, v) => s + v, 0) / salaries.length
      : 0
    companyDetailStats.value = {
      jobCount: jc,
      recruitTotal: rt,
      avgSalary: avg > 0 ? (avg / 1000).toFixed(1) + 'k' : '--',
    }
  } catch (e) {
    console.error('加载公司岗位列表失败', e)
  }
}

function backToResults() {
  if (detailView.value === 'company') {
    detailView.value = 'detail'
  } else {
    detailView.value = null
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// ── 个人资料操作 ──
async function saveProfile() {
  saveSuccess.value = false
  try {
    await authAPI.updateUser({ username: editForm.username, email: editForm.email })
    await authAPI.updateProfile({
      expectedCity: editForm.target_city.join(','),
      expectedCategory: editForm.target_category.join(','),
    })
    profile.username = editForm.username
    profile.email = editForm.email
    profile.target_city_list = [...editForm.target_city]
    profile.target_category_list = [...editForm.target_category]
    isEditing.value = false
    saveSuccess.value = true
    setTimeout(() => { saveSuccess.value = false }, 3000)
  } catch (e) { console.error('保存失败', e) }
}

function cancelEdit() {
  editForm.username = profile.username
  editForm.email = profile.email
  editForm.target_city = [...profile.target_city_list]
  editForm.target_category = [...profile.target_category_list]
  isEditing.value = false
}

async function changePassword() {
  passwordError.value = ''
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = '两次密码不一致'
    return
  }
  try {
    await authAPI.changePassword({
      oldPassword: passwordForm.old_password,
      newPassword: passwordForm.new_password,
    })
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    alert('密码修改成功')
  } catch (e) {
    passwordError.value = '密码修改失败：' + (e.response?.data?.detail || '请检查当前密码是否正确')
  }
}

// ── 点击外部关闭下拉 ──
function handleClickOutside(e) {
  if (citySelectRef.value && !citySelectRef.value.contains(e.target)) cityOpen.value = false
  if (catSelectRef.value && !catSelectRef.value.contains(e.target)) catOpen.value = false
}

onMounted(() => {
  fetchFavorites()
  fetchBrowseHistory()
  fetchProfile()
  fetchOptions()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>