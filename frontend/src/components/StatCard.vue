<template>
  <div class="stat-card group">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm text-gray-500 mb-1">{{ label }}</p>
        <p class="text-2xl font-bold text-gray-100">{{ value }}</p>
        <p v-if="subtext" class="text-xs mt-1" :class="subtextColor">{{ subtext }}</p>
      </div>
      <div class="w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110"
           :class="iconBg">
        <component :is="iconComponent" class="w-6 h-6" :class="iconColor" />
      </div>
    </div>
    <div v-if="progress" class="mt-4">
      <div class="flex justify-between text-xs text-gray-500 mb-1">
        <span>完成度</span>
        <span>{{ progress }}%</span>
      </div>
      <div class="h-1.5 bg-dark-700 rounded-full overflow-hidden">
        <div class="h-full rounded-full transition-all duration-500" :style="{ width: progress + '%' }"
             :class="progressColor" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, h } from 'vue'

const props = defineProps({
  label: { type: String, default: '' },
  value: { type: [String, Number], default: '' },
  subtext: { type: String, default: '' },
  subtextColor: { type: String, default: 'text-green-400' },
  icon: { type: String, default: 'chart' },
  color: { type: String, default: 'primary' },
  progress: { type: Number, default: null },
})

const iconMap = {
  chart: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  users: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z',
  briefcase: 'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  currency: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  location: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z',
}

const colorMap = {
  primary: { bg: 'bg-primary-500/10', icon: 'text-primary-400', progress: 'bg-primary-500' },
  accent: { bg: 'bg-accent-500/10', icon: 'text-accent-400', progress: 'bg-accent-500' },
  orange: { bg: 'bg-orange-500/10', icon: 'text-orange-400', progress: 'bg-orange-500' },
  purple: { bg: 'bg-purple-500/10', icon: 'text-purple-400', progress: 'bg-purple-500' },
  pink: { bg: 'bg-pink-500/10', icon: 'text-pink-400', progress: 'bg-pink-500' },
}

const iconComponent = computed(() => {
  const path = iconMap[props.icon] || iconMap.chart
  return {
    render() {
      return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-6 h-6' }, [
        h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': 2, d: path })
      ])
    }
  }
})

const colors = computed(() => colorMap[props.color] || colorMap.primary)
const iconBg = computed(() => colors.value.bg)
const iconColor = computed(() => colors.value.icon)
const progressColor = computed(() => colors.value.progress)
</script>
