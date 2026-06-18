<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">薪资预测</h1>
        <p class="text-gray-500 mt-1">基于机器学习模型，根据岗位特征预测月薪</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <!-- ===== 左侧：预测参数 ===== -->
      <div class="lg:col-span-2 space-y-6">
        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">预测参数</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm text-gray-400 mb-2">城市</label>
              <select v-model="form.location_city" class="glass-input w-full">
                <option value="">请选择城市</option>
                <option v-for="c in options.cities" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">岗位类别</label>
              <select v-model="form.category" class="glass-input w-full">
                <option value="">请选择岗位类别</option>
                <option v-for="c in options.categories" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">工作经验</label>
              <select v-model="form.experience_level" class="glass-input w-full">
                <option value="">请选择经验</option>
                <option v-for="e in sortedExpLevels" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">学历要求</label>
              <select v-model="form.education" class="glass-input w-full">
                <option value="">请选择学历</option>
                <option v-for="e in sortedEducations" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">公司规模</label>
              <select v-model="form.company_scale" class="glass-input w-full">
                <option value="">请选择规模</option>
                <option v-for="s in sortedScales" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">公司行业</label>
              <select v-model="form.company_industry" class="glass-input w-full">
                <option value="">请选择行业</option>
                <option v-for="ind in options.company_industries" :key="ind" :value="ind">{{ ind }}</option>
              </select>
            </div>
            <button @click="predictSalary" :disabled="!canPredict" class="btn-primary w-full">开始预测</button>
          </div>
        </div>

        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">模型信息</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">模型类型</span>
              <span class="text-gray-300">{{ predictedResult.model_used || '随机森林 / CatBoost' }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">训练数据</span>
              <span class="text-gray-300">{{ modelInfo.data_count }} 条</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">R² 得分</span>
              <span class="text-accent-400">{{ modelInfo.r2 }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">MAE</span>
              <span class="text-gray-300">{{ modelInfo.mae }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 右侧：预测结果 ===== -->
      <div class="lg:col-span-3 space-y-6">
        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">预测结果</h3>

          <!-- 空状态 -->
          <div v-if="!predicted" class="flex flex-col items-center justify-center h-64 text-gray-500">
            <svg class="w-16 h-16 mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <p>填写参数并开始预测</p>
          </div>

          <!-- 加载中 -->
          <div v-else-if="loading" class="flex flex-col items-center justify-center h-64 text-gray-500">
            <svg class="w-10 h-10 mb-3 text-primary-500 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p>正在预测中，请稍候...</p>
          </div>

          <!-- 结果 -->
          <div v-else class="space-y-6">
            <div class="text-center p-6">
              <p class="text-sm text-gray-500 mb-2">预测月薪</p>
              <div class="text-4xl font-bold text-gradient mb-2">{{ formatSalary(predictedResult.predicted_salary) }}</div>
              <p class="text-xs text-gray-500 mt-1">基于 {{ form.location_city }} · {{ form.category }} · {{ form.experience_level }}</p>
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div class="text-center p-4 rounded-xl bg-dark-800/50">
                <p class="text-xs text-gray-500 mb-1">最低估计</p>
                <p class="text-lg font-semibold text-gray-300">{{ formatSalary(predictedResult.predicted_min) }}</p>
              </div>
              <div class="text-center p-4 rounded-xl bg-dark-800/50">
                <p class="text-xs text-gray-500 mb-1">预计月薪</p>
                <p class="text-lg font-semibold text-accent-400">{{ formatSalary(predictedResult.predicted_salary) }}</p>
              </div>
              <div class="text-center p-4 rounded-xl bg-dark-800/50">
                <p class="text-xs text-gray-500 mb-1">最高估计</p>
                <p class="text-lg font-semibold text-gray-300">{{ formatSalary(predictedResult.predicted_max) }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">影响因子分析</h3>
          <div v-if="factors.length === 0" class="text-center py-8 text-gray-500">
            <p>暂无影响因子数据</p>
          </div>
          <div v-else class="space-y-3">
            <div v-for="(factor, idx) in factors" :key="idx"
                 class="flex items-center justify-between p-3 rounded-xl bg-dark-800/50">
              <div class="flex items-center gap-2">
                <div class="w-1.5 h-8 rounded-full" :class="factor.color" />
                <span class="text-sm text-gray-300">{{ factor.name }}</span>
              </div>
              <div class="flex items-center gap-4">
                <div class="w-24 h-2 bg-dark-700 rounded-full overflow-hidden">
                  <div class="h-full rounded-full" :class="factor.color" :style="{ width: factor.weight + '%' }" />
                </div>
                <span class="text-sm text-gray-400 w-12 text-right">{{ factor.weight }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { mlAPI } from '@/api/index.js'

// ── 选项数据 ──
const options = reactive({
  cities: [],
  categories: [],
  experience_levels: [],
  educations: [],
  company_scales: [],
  company_industries: [],
})

const modelInfo = reactive({
  data_count: '--',
  r2: '--',
  mae: '--',
})

async function fetchOptions() {
  try {
    const res = await mlAPI.getSalaryPredictOptions()
    options.cities = res.data.cities || []
    options.categories = res.data.categories || []
    options.experience_levels = res.data.experience_levels || []
    options.educations = res.data.educations || []
    options.company_scales = res.data.company_scales || []
    options.company_industries = res.data.company_industries || []
    if (res.data.model_info) {
      modelInfo.data_count = res.data.model_info.data_count ?? '--'
      modelInfo.r2 = res.data.model_info.r2 ?? '--'
      modelInfo.mae = res.data.model_info.mae ?? '--'
    }
  } catch (e) {
    console.error('加载预测选项失败', e)
  }
}

onMounted(() => {
  fetchOptions()
})

// ── 排序辅助 ──

const EXP_ORDER = ['经验不限', '实习生', '应届生', '1-3年', '3-5年', '5-10年']
const EDU_ORDER = ['学历不限', '大专', '本科', '统招本科', '硕士', '博士']
const SCALE_ORDER = [
  '1-49人', '50-99人', '100-499人', '500-999人',
  '1000-2000人', '2000-5000人', '5000-10000人', '10000人以上',
]

function _sortByOrder(list, order) {
  return [...list].sort((a, b) => {
    const ia = order.indexOf(a)
    const ib = order.indexOf(b)
    return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib)
  })
}

const sortedExpLevels = computed(() => _sortByOrder(options.experience_levels, EXP_ORDER))
const sortedEducations = computed(() => _sortByOrder(options.educations, EDU_ORDER))
const sortedScales = computed(() => _sortByOrder(options.company_scales, SCALE_ORDER))

// ── 表单 ──
const form = reactive({
  location_city: '',
  category: '',
  experience_level: '',
  education: '',
  company_scale: '',
  company_industry: '',
})

const canPredict = computed(() => {
  return form.location_city && form.category && form.experience_level && form.education
})

// ── 预测 ──
const predicted = ref(false)
const loading = ref(false)
const predictedResult = ref({ predicted_salary: null })
const factors = ref([])

/** 特征列名 → 中文映射 */
const FEATURE_NAME_MAP = {
  category: '岗位类别',
  location_city: '城市',
  company_industry: '公司行业',
  exp_numeric: '经验年限',
  edu_numeric: '学历',
  company_scale_min: '公司规模',
  company_scale_max: '公司规模',
  has_weekend_off: '是否双休',
}

/** 格式化薪资：27000 → "¥27,000" */
function formatSalary(val) {
  if (val == null) return '--'
  return '¥' + Number(val).toLocaleString('zh-CN')
}

async function predictSalary() {
  if (!canPredict.value) return
  loading.value = true
  predicted.value = true

  try {
    const res = await mlAPI.predictSalary({ ...form })
    predictedResult.value = res.data

    // 处理特征重要性：归一化到 100% + 中文映射
    const raw = res.data.feature_importance || []
    const totalWeight = raw.reduce((sum, f) => sum + (f.weight || 0), 0)
    const colors = ['bg-primary-500', 'bg-accent-500', 'bg-blue-500', 'bg-purple-500', 'bg-orange-500', 'bg-green-500']
    factors.value = raw.map((f, i) => ({
      name: FEATURE_NAME_MAP[f.name] || f.name,
      weight: totalWeight > 0 ? Math.round((f.weight / totalWeight) * 100) : 0,
      color: colors[i % colors.length],
    }))
    // 按权重降序排列
    factors.value.sort((a, b) => b.weight - a.weight)
  } catch (e) {
    console.error('预测失败', e)
    predictedResult.value = { predicted_salary: null }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.text-gradient {
  background: linear-gradient(135deg, #8b5cf6, #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
