<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">AI 助手</h1>
        <p class="text-gray-500 mt-1">职业规划与模拟面试助手</p>
      </div>
    </div>

    <div class="glass-card p-6 flex flex-col" style="height: calc(100vh - 240px);">
      <!-- 消息列表 -->
      <div ref="msgContainer" class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        <div v-for="(msg, idx) in messages" :key="idx"
             class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
          <div class="max-w-[75%] p-3 rounded-xl"
               :class="msg.role === 'user'
                 ? 'bg-primary-600/20 text-gray-200 border border-primary-500/20'
                 : 'bg-dark-800/50 text-gray-300 border border-dark-700/50'">
            <p class="text-sm whitespace-pre-wrap">{{ msg.content }}</p>
          </div>
        </div>
        <!-- 加载中 -->
        <div v-if="loading" class="flex justify-start">
          <div class="max-w-[75%] p-3 rounded-xl bg-dark-800/50 text-gray-500 border border-dark-700/50">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>思考中...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="flex items-center gap-3 pt-4 border-t border-dark-700/50">
        <input v-model="inputText" type="text" class="glass-input flex-1" placeholder="输入您的问题，如：如何规划 Java 后端开发职业路线？"
               @keyup.enter="sendMessage" :disabled="loading" />
        <button @click="sendMessage" :disabled="!inputText.trim() || loading" class="btn-primary shrink-0">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { aiAPI } from '@/api'

const inputText = ref('')
const loading = ref(false)
const msgContainer = ref(null)

const messages = ref([
  { role: 'assistant', content: '您好！我是 AI 职业助手。您可以问我关于职业规划、面试技巧、行业趋势等问题，我会尽力为您提供专业建议。' },
])

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true

  try {
    const res = await aiAPI.chat({ messages: messages.value })
    messages.value.push({
      role: 'assistant',
      content: res.data.reply,
    })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '抱歉，请求失败，请稍后重试。' })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  }
}

onMounted(scrollToBottom)
</script>
