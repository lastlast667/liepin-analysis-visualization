<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">薪资预测</h1>
        <p class="text-gray-500 mt-1">基于机器学习模型，根据岗位特征预测薪资范围</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">预测参数</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm text-gray-400 mb-2">岗位类别</label>
              <select v-model="form.category" class="glass-input w-full">
                <option value="">请选择</option>
                <option>Java开发</option>
                <option>Python开发</option>
                <option>Go开发</option>
                <option>C++开发</option>
                <option>前端开发</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">经验年限</label>
              <div class="flex items-center gap-3">
                <input v-model.number="form.experience" type="range" min="0" max="20" step="1"
                       class="flex-1 accent-primary-500" />
                <span class="text-sm text-gray-200 w-12 text-center">{{ form.experience }} 年</span>
              </div>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">学历</label>
              <select v-model="form.education" class="glass-input w-full">
                <option value="">请选择</option>
                <option>大专</option>
                <option>本科</option>
                <option>硕士</option>
                <option>博士</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">城市</label>
              <select v-model="form.city" class="glass-input w-full">
                <option value="">请选择</option>
                <option>北京</option>
                <option>上海</option>
                <option>深圳</option>
                <option>杭州</option>
                <option>广州</option>
                <option>成都</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-2">技能关键词（逗号分隔）</label>
              <input v-model="form.skills" type="text" class="glass-input w-full" placeholder="例：Spring Boot, Redis, Docker" />
            </div>
            <button @click="predictSalary" :disabled="!form.category" class="btn-primary w-full">开始预测</button>
          </div>
        </div>

        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">模型信息</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">模型类型</span>
              <span class="text-gray-300">随机森林回归</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">训练数据</span>
              <span class="text-gray-300">12,847 条</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">R² 得分</span>
              <span class="text-accent-400">0.875</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">MAE</span>
              <span class="text-gray-300">¥1,850</span>
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-3 space-y-6">
        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">预测结果</h3>
          <div v-if="!predicted" class="flex flex-col items-center justify-center h-64 text-gray-500">
            <svg class="w-16 h-16 mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <p>填写参数并开始预测</p>
          </div>
          <div v-else class="space-y-6">
            <div class="text-center p-6">
              <p class="text-sm text-gray-500 mb-2">预测月薪范围</p>
              <div class="text-4xl font-bold text-gradient mb-2">{{ predictedResult.range }}</div>
              <p class="text-sm text-gray-500">均值 <span class="text-gray-300 font-semibold">{{ predictedResult.average }}</span></p>
            </div>
            <div class="h-4 bg-dark-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full bg-gradient-to-r from-primary-500 to-accent-500"
                   :style="{ width: predictedResult.confidence + '%' }" />
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-500">置信度</span>
              <span class="text-accent-400">{{ predictedResult.confidence }}%</span>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-4">影响因子分析</h3>
          <div class="space-y-3">
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
import { reactive, ref } from 'vue'

const form = reactive({
  category: '',
  experience: 3,
  education: '',
  city: '',
  skills: '',
})
const predicted = ref(false)

const predictedResult = ref({
  range: '¥22,000 - ¥32,000',
  average: '¥27,000',
  confidence: 87,
})

const factors = [
  { name: '城市因素', weight: 35, color: 'bg-primary-500' },
  { name: '经验年限', weight: 28, color: 'bg-accent-500' },
  { name: '技能匹配', weight: 20, color: 'bg-blue-500' },
  { name: '学历因素', weight: 12, color: 'bg-purple-500' },
  { name: '公司规模', weight: 5, color: 'bg-orange-500' },
]

function predictSalary() {
  predicted.value = true
}
</script>
