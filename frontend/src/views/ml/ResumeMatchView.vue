<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">简历匹配</h1>
        <p class="text-gray-500 mt-1">上传简历，智能匹配最适合您的岗位</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <!-- ===== 左侧：简历上传 + 筛选条件 ===== -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 简历上传卡片 -->
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
        </div>

        <!-- 筛选条件卡片 -->
        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">筛选条件</h3>
          <div class="space-y-4">

            <!-- 期望城市（多选，点击展开） -->
            <div class="relative" ref="cityRef">
              <label class="block text-sm text-gray-400 mb-2">期望城市</label>
              <div @click="cityOpen = !cityOpen" class="glass-input w-full cursor-pointer flex items-center justify-between">
                <span class="truncate" :class="selectedCityLabel ? 'text-gray-100' : 'text-gray-500'">
                  {{ selectedCityLabel || '不限城市' }}
                </span>
                <svg class="w-4 h-4 text-gray-500 transition-transform flex-shrink-0" :class="{ 'rotate-180': cityOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              <div v-if="cityOpen" class="absolute z-[100] mt-1 w-full glass-card p-2 max-h-56 overflow-y-auto shadow-2xl">
                <label class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer sticky top-0 bg-dark-800 z-10">
                  <input type="checkbox" :checked="selectedCities.length === 0" @change="clearCityFilter" class="rounded accent-primary-500" />
                  <span class="text-sm text-gray-300">不限城市</span>
                </label>
                <template v-for="([letter, citiesInGroup], gi) in groupedCities" :key="letter">
                  <div class="px-3 py-1 mt-1 text-xs font-semibold text-primary-400 bg-dark-800/50 sticky top-11">{{ letter }}</div>
                  <label v-for="city in citiesInGroup" :key="city" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
                    <input type="checkbox" :value="city" v-model="selectedCities" class="rounded accent-primary-500" />
                    <span class="text-sm text-gray-300">{{ city }}</span>
                  </label>
                </template>
              </div>
            </div>

            <!-- 期望薪资 -->
            <div>
              <label class="block text-sm text-gray-400 mb-2">期望薪资</label>
              <select v-model="selectedSalaryRange" class="glass-input w-full">
                <option value="">不限</option>
                <option value="0-10k">0-10k</option>
                <option value="10k-20k">10k-20k</option>
                <option value="20k-30k">20k-30k</option>
                <option value="30k-50k">30k-50k</option>
                <option value="50k+">50k+</option>
              </select>
            </div>

            <!-- 更多筛选（折叠面板） -->
            <div>
              <button @click="moreFilterOpen = !moreFilterOpen" class="flex items-center justify-between w-full text-sm text-gray-400 hover:text-gray-300 transition-colors py-1">
                <span>更多筛选</span>
                <svg class="w-4 h-4 transition-transform" :class="{ 'rotate-180': moreFilterOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div v-if="moreFilterOpen" class="mt-3 space-y-4 pl-1">
                <!-- 公司规模偏好 -->
                <div class="relative" ref="scaleRef">
                  <label class="block text-sm text-gray-400 mb-2">公司规模偏好</label>
                  <div @click="scaleOpen = !scaleOpen" class="glass-input w-full cursor-pointer flex items-center justify-between">
                    <span class="truncate text-sm" :class="selectedScaleLabel ? 'text-gray-100' : 'text-gray-500'">
                      {{ selectedScaleLabel || '不限' }}
                    </span>
                    <svg class="w-4 h-4 text-gray-500 transition-transform flex-shrink-0" :class="{ 'rotate-180': scaleOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                  <div v-if="scaleOpen" class="absolute z-[100] mt-1 w-full glass-card p-2 max-h-48 overflow-y-auto shadow-2xl">
                    <label class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
                      <input type="checkbox" :checked="selectedScales.length === 0" @change="clearScaleFilter" class="rounded accent-primary-500" />
                      <span class="text-sm text-gray-300">不限</span>
                    </label>
                    <label v-for="scale in sortedScales" :key="scale" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
                      <input type="checkbox" :value="scale" v-model="selectedScales" class="rounded accent-primary-500" />
                      <span class="text-sm text-gray-300">{{ scale }}</span>
                    </label>
                  </div>
                </div>

                <!-- 行业偏好 -->
                <div class="relative" ref="industryRef">
                  <label class="block text-sm text-gray-400 mb-2">公司行业偏好</label>
                  <div @click="industryOpen = !industryOpen" class="glass-input w-full cursor-pointer flex items-center justify-between">
                    <span class="truncate text-sm" :class="selectedIndustryLabel ? 'text-gray-100' : 'text-gray-500'">
                      {{ selectedIndustryLabel || '不限' }}
                    </span>
                    <svg class="w-4 h-4 text-gray-500 transition-transform flex-shrink-0" :class="{ 'rotate-180': industryOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                  <div v-if="industryOpen" class="absolute z-[100] mt-1 w-full glass-card p-2 max-h-48 overflow-y-auto shadow-2xl">
                    <label class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
                      <input type="checkbox" :checked="selectedIndustries.length === 0" @change="clearIndustryFilter" class="rounded accent-primary-500" />
                      <span class="text-sm text-gray-300">不限</span>
                    </label>
                    <label v-for="ind in options.company_industries" :key="ind" class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-dark-700 cursor-pointer">
                      <input type="checkbox" :value="ind" v-model="selectedIndustries" class="rounded accent-primary-500" />
                      <span class="text-sm text-gray-300">{{ ind }}</span>
                    </label>
                  </div>
                </div>

                <!-- 是否双休 -->
                <div>
                  <label class="block text-sm text-gray-400 mb-2">是否双休</label>
                  <select v-model="selectedWeekendOff" class="glass-input w-full text-sm">
                    <option value="">不限</option>
                    <option value="true">只看双休</option>
                  </select>
                </div>
              </div>
            </div>

            <button @click="startMatching" :disabled="!uploadedFile" class="btn-primary w-full">开始匹配</button>
          </div>
        </div>
      </div>

      <!-- ===== 右侧：匹配结果 / 岗位详情（内联切换） ===== -->
      <div class="lg:col-span-3">
        <!-- 匹配中 -->
        <div v-if="loading" class="glass-card p-6">
          <div class="flex flex-col items-center justify-center h-64 text-gray-500">
            <svg class="w-10 h-10 mb-3 text-primary-500 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p>正在匹配中，请稍候...</p>
          </div>
        </div>

        <!-- 列表视图 -->
        <template v-else-if="detailView === null">
          <JobList
            v-if="hasMatched"
            :jobs="matchResults"
            :total-count="matchResults.length"
            :total-pages="1"
            :current-page="1"
            :show-match-score="true"
            :show-remote-badge="true"
            @view-job="goJobDetail"
          />
          <div v-else class="glass-card p-6">
            <div class="flex flex-col items-center justify-center h-64 text-gray-500">
              <svg class="w-16 h-16 mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p>上传简历并开始匹配</p>
            </div>
          </div>
        </template>

        <!-- 岗位详情视图 -->
        <template v-else-if="detailView === 'detail' && selectedJob">
          <div>
            <button @click="backToResults" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-primary-400 transition-colors mb-4">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              返回匹配结果
            </button>
          </div>
          <JobDetail
            :job="selectedJob"
            :company-stats="jobDetailCompanyStats"
            :similar-jobs="similarJobs"
            :salary-analysis="salaryAnalysis"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { mlAPI, analysisAPI } from '@/api/index.js'
import JobDetail from '@/components/job/JobDetail.vue'
import JobList from '@/components/job/JobList.vue'

// ── 排序辅助 ──

/** 公司规模按大小排序 */
const SCALE_SORT_ORDER = [
  '1-49人', '50-99人', '100-499人', '500-999人',
  '1000-2000人', '2000-5000人', '5000-10000人', '10000人以上',
]

const sortedScales = computed(() => {
  return [...options.company_scales].sort((a, b) => {
    const ia = SCALE_SORT_ORDER.indexOf(a)
    const ib = SCALE_SORT_ORDER.indexOf(b)
    return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib)
  })
})

/** 获取汉字拼音首字母（A-Z），用于城市分组引导 */
function getPinyinInitial(char) {
  const map = {
    '阿': 'A', '埃': 'A', '安': 'A', '澳': 'A',
    '八': 'B', '巴': 'B', '白': 'B', '百': 'B', '蚌': 'B', '包': 'B', '宝': 'B', '保': 'B', '北': 'B', '本': 'B', '毕': 'B', '滨': 'B', '波': 'B', '博': 'B',
    '沧': 'C', '常': 'C', '长': 'C', '朝': 'C', '潮': 'C', '郴': 'C', '成': 'C', '承': 'C', '池': 'C', '赤': 'C', '滁': 'C', '楚': 'C', '川': 'C',
    '达': 'D', '大': 'D', '丹': 'D', '德': 'D', '登': 'D', '迪': 'D', '定': 'D', '东': 'D', '敦': 'D',
    '鄂': 'E', '恩': 'E',
    '法': 'F', '防': 'F', '佛': 'F', '福': 'F', '抚': 'F', '阜': 'F', '富': 'F',
    '甘': 'G', '赣': 'G', '高': 'G', '个': 'G', '巩': 'G', '广': 'G', '贵': 'G', '桂': 'G',
    '哈': 'H', '海': 'H', '邯': 'H', '汉': 'H', '杭': 'H', '合': 'H', '河': 'H', '菏': 'H', '衡': 'H', '红': 'H', '湖': 'H', '淮': 'H', '黄': 'H', '惠': 'H',
    '鸡': 'J', '吉': 'J', '济': 'J', '佳': 'J', '嘉': 'J', '江': 'J', '揭': 'J', '金': 'J', '锦': 'J', '晋': 'J', '荆': 'J', '景': 'J', '九': 'J', '酒': 'J',
    '喀': 'K', '开': 'K', '昆': 'K',
    '拉': 'L', '来': 'L', '兰': 'L', '廊': 'L', '乐': 'L', '雷': 'L', '丽': 'L', '连': 'L', '凉': 'L', '辽': 'L', '聊': 'L', '林': 'L', '临': 'L', '陵': 'L', '柳': 'L', '龙': 'L', '娄': 'L', '庐': 'L', '鲁': 'L', '泸': 'L', '洛': 'L', '漯': 'L',
    '马': 'M', '满': 'M', '眉': 'M', '梅': 'M', '绵': 'M', '牡': 'M',
    '南': 'N', '内': 'N', '宁': 'N', '牛': 'N',
    '攀': 'P', '盘': 'P', '平': 'P', '莆': 'P', '濮': 'P',
    '七': 'Q', '齐': 'Q', '迁': 'Q', '钦': 'Q', '青': 'Q', '清': 'Q', '庆': 'Q', '泉': 'Q', '曲': 'Q', '衢': 'Q', '全': 'Q',
    '日': 'R',
    '三': 'S', '厦': 'S', '汕': 'S', '上': 'S', '韶': 'S', '邵': 'S', '深': 'S', '沈': 'S', '十': 'S', '石': 'S', '双': 'S', '朔': 'S', '四': 'S', '松': 'S', '苏': 'S', '宿': 'S', '绥': 'S', '遂': 'S',
    '台': 'T', '太': 'T', '泰': 'T', '唐': 'T', '天': 'T', '铁': 'T', '通': 'T', '同': 'T', '铜': 'T',
    '外': 'W', '万': 'W', '威': 'W', '渭': 'W', '温': 'W', '乌': 'W', '芜': 'W', '武': 'W',
    '西': 'X', '咸': 'X', '襄': 'X', '孝': 'X', '新': 'X', '信': 'X', '邢': 'X', '徐': 'X', '许': 'X', '宣': 'X',
    '雅': 'Y', '烟': 'Y', '盐': 'Y', '扬': 'Y', '阳': 'Y', '宜': 'Y', '义': 'Y', '益': 'Y', '银': 'Y', '营': 'Y', '永': 'Y', '榆': 'Y', '玉': 'Y', '岳': 'Y', '云': 'Y',
    '枣': 'Z', '湛': 'Z', '张': 'Z', '漳': 'Z', '昭': 'Z', '肇': 'Z', '镇': 'Z', '郑': 'Z', '中': 'Z', '舟': 'Z', '周': 'Z', '珠': 'Z', '驻': 'Z', '庄': 'Z', '淄': 'Z', '自': 'Z', '遵': 'Z',
  }
  return map[char] || '#'
}

/** 城市按拼音首字母排序 + 分组 */
const sortedCities = computed(() => {
  return [...options.cities].sort((a, b) => a.localeCompare(b, 'zh-CN'))
})

const groupedCities = computed(() => {
  const groups = {}
  for (const city of sortedCities.value) {
    const initial = getPinyinInitial(city[0])
    if (!groups[initial]) groups[initial] = []
    groups[initial].push(city)
  }
  return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b))
})

// --- 文件上传 ---
const fileInput = ref(null)
const uploadedFile = ref(null)

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
  matchResults.value = []
}

// --- 下拉选项（从后端加载） ---
const options = reactive({
  cities: [],
  company_scales: [],
  company_industries: [],
})

async function fetchOptions() {
  try {
    const res = await mlAPI.getMatchOptions()
    options.cities = res.data.cities || []
    options.company_scales = res.data.company_scales || []
    options.company_industries = res.data.company_industries || []
  } catch (e) {
    console.error('加载筛选选项失败', e)
  }
}

onMounted(() => {
  fetchOptions()
})

// --- 筛选条件 ---
// 城市（多选）
const cityOpen = ref(false)
const cityRef = ref(null)
const selectedCities = ref([])
const selectedCityLabel = computed(() => {
  if (selectedCities.value.length === 0) return ''
  if (selectedCities.value.length <= 2) return selectedCities.value.join('、')
  return selectedCities.value.slice(0, 2).join('、') + ` 等${selectedCities.value.length}个城市`
})
function clearCityFilter() {
  selectedCities.value = []
  cityOpen.value = false
}

// 薪资
const selectedSalaryRange = ref('')

// 更多筛选折叠
const moreFilterOpen = ref(false)

// 公司规模（多选）
const scaleOpen = ref(false)
const scaleRef = ref(null)
const selectedScales = ref([])
const selectedScaleLabel = computed(() => {
  if (selectedScales.value.length === 0) return ''
  if (selectedScales.value.length <= 2) return selectedScales.value.join('、')
  return selectedScales.value.slice(0, 2).join('、') + ` 等${selectedScales.value.length}项`
})
function clearScaleFilter() {
  selectedScales.value = []
  scaleOpen.value = false
}

// 行业（多选）
const industryOpen = ref(false)
const industryRef = ref(null)
const selectedIndustries = ref([])
const selectedIndustryLabel = computed(() => {
  if (selectedIndustries.value.length === 0) return ''
  if (selectedIndustries.value.length <= 2) return selectedIndustries.value.join('、')
  return selectedIndustries.value.slice(0, 2).join('、') + ` 等${selectedIndustries.value.length}项`
})
function clearIndustryFilter() {
  selectedIndustries.value = []
  industryOpen.value = false
}

// 双休
const selectedWeekendOff = ref('')

// --- 匹配 ---
const hasMatched = ref(false)
const loading = ref(false)
const matchResults = ref([])

async function startMatching() {
  if (!uploadedFile.value) return

  loading.value = true
  hasMatched.value = true

  // 构造请求参数
  const params = {
    cities: selectedCities.value,
    salary_range: selectedSalaryRange.value,
    company_scales: selectedScales.value,
    company_industries: selectedIndustries.value,
    has_weekend_off: selectedWeekendOff.value === 'true' ? true : null,
    top_k: 20,
  }

  try {
    // 上传简历后再匹配（实际由后端完成解析+匹配）
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    // 将筛选条件以 JSON 字符串附上
    formData.append('filters', JSON.stringify(params))

    const res = await mlAPI.matchResume(formData)
    matchResults.value = res.data.results || []
  } catch (e) {
    console.error('匹配失败', e)
    matchResults.value = []
  } finally {
    loading.value = false
  }
}

// --- 岗位详情 ---
const detailView = ref(null)           // null=列表, 'detail'=详情
const selectedJob = ref(null)
const jobDetailCompanyStats = ref({ jobCount: 0, recruitTotal: 0, avgSalary: '--' })
const similarJobs = ref([])
const salaryAnalysis = ref({
  industryAvg: '--', abovePercentage: 0,
  rangeMin: '--', rangeMax: '--', positionPercentage: 50,
})

async function goJobDetail(match) {
  try {
    const res = await analysisAPI.getJobDetail(match.id)
    selectedJob.value = res.data
    jobDetailCompanyStats.value = res.data.company_stats || { jobCount: 0, recruitTotal: 0, avgSalary: '--' }
    similarJobs.value = res.data.similar_jobs || []
    salaryAnalysis.value = res.data.salary_analysis || {
      industryAvg: '--', abovePercentage: 0,
      rangeMin: '--', rangeMax: '--', positionPercentage: 50,
    }
    detailView.value = 'detail'
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (e) {
    console.error('加载岗位详情失败', e)
  }
}

function backToResults() {
  detailView.value = null
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// --- 点击外部关闭下拉面板 ---
function handleClickOutside(e) {
  if (cityRef.value && !cityRef.value.contains(e.target)) {
    cityOpen.value = false
  }
  if (scaleRef.value && !scaleRef.value.contains(e.target)) {
    scaleOpen.value = false
  }
  if (industryRef.value && !industryRef.value.contains(e.target)) {
    industryOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
</script>
