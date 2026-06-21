<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-100">管理后台</h1>
        <p class="text-gray-500 mt-1">管理用户数据与岗位信息</p>
      </div>
      <span class="text-xs px-2.5 py-1 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">管理员</span>
    </div>

    <!-- 顶部标签切换 -->
    <div class="flex gap-1 rounded-xl bg-dark-800/50 p-1 w-fit">
      <button v-for="tab in tabs" :key="tab.key"
              @click="activeTab = tab.key"
              class="px-5 py-2 rounded-lg text-sm font-medium transition-all duration-300"
              :class="activeTab === tab.key ? 'bg-dark-700 text-gray-200 shadow-sm' : 'text-gray-500 hover:text-gray-300'">
        {{ tab.label }}
      </button>
    </div>

    <!-- ===== 用户管理 ===== -->
    <div v-if="activeTab === 'users'">
      <div class="glass-card p-5">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <input v-model="userSearch" type="text" class="glass-input" placeholder="搜索用户名/邮箱..." @input="loadUsers" />
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-500">共 {{ users.length }} 个用户</span>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-gray-500 border-b border-dark-700/50">
                <th class="text-left py-3 px-2 w-16">ID</th>
                <th class="text-left py-3 px-2">用户名</th>
                <th class="text-left py-3 px-2">邮箱</th>
                <th class="text-left py-3 px-2">手机号</th>
                <th class="text-left py-3 px-2">管理员</th>
                <th class="text-left py-3 px-2">活跃</th>
                <th class="text-right py-3 px-2 w-40">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id"
                   class="border-b border-dark-700/30 hover:bg-dark-800/30 transition-colors">
                <td class="py-3 px-2 text-gray-400">{{ user.id }}</td>
                <td class="py-3 px-2 text-gray-200">{{ user.username }}</td>
                <td class="py-3 px-2 text-gray-400">{{ user.email || '--' }}</td>
                <td class="py-3 px-2 text-gray-400">{{ user.phone || '--' }}</td>
                <td class="py-3 px-2">
                  <span class="px-2 py-0.5 rounded text-xs" :class="user.isStaff ? 'bg-red-500/10 text-red-400' : 'bg-dark-700 text-gray-500'">
                    {{ user.isStaff ? '是' : '否' }}
                  </span>
                </td>
                <td class="py-3 px-2">
                  <span class="px-2 py-0.5 rounded text-xs" :class="user.isActive ? 'bg-green-500/10 text-green-400' : 'bg-dark-700 text-gray-500'">
                    {{ user.isActive ? '是' : '否' }}
                  </span>
                </td>
                <td class="py-3 px-2 text-right">
                  <button class="px-3 py-1 rounded-lg text-xs bg-primary-500/10 text-primary-400 hover:bg-primary-500/20 transition-colors mr-1">编辑</button>
                  <button @click="deleteUser(user)" class="px-3 py-1 rounded-lg text-xs bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===== 岗位管理 ===== -->
    <div v-if="activeTab === 'jobs'">
      <div class="glass-card p-5">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <input v-model="jobSearch" type="text" class="glass-input" placeholder="搜索岗位名称/公司..." @input="loadJobs" />
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-500">共 {{ jobs.length }} 个岗位</span>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-gray-500 border-b border-dark-700/50">
                <th class="text-left py-3 px-2 w-16">ID</th>
                <th class="text-left py-3 px-2">岗位名称</th>
                <th class="text-left py-3 px-2">公司</th>
                <th class="text-left py-3 px-2">城市</th>
                <th class="text-left py-3 px-2">类别</th>
                <th class="text-left py-3 px-2">薪资</th>
                <th class="text-right py-3 px-2 w-40">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="job in jobs" :key="job.id"
                   class="border-b border-dark-700/30 hover:bg-dark-800/30 transition-colors">
                <td class="py-3 px-2 text-gray-400">{{ job.id }}</td>
                <td class="py-3 px-2 text-gray-200 max-w-[200px] truncate">{{ job.title }}</td>
                <td class="py-3 px-2 text-gray-400">{{ job.companyName }}</td>
                <td class="py-3 px-2 text-gray-400">{{ job.locationCity }}</td>
                <td class="py-3 px-2"><span class="px-2 py-0.5 rounded text-xs bg-dark-700 text-gray-400">{{ job.category }}</span></td>
                <td class="py-3 px-2 text-primary-400">{{ job.salary }}</td>
                <td class="py-3 px-2 text-right">
                  <button class="px-3 py-1 rounded-lg text-xs bg-primary-500/10 text-primary-400 hover:bg-primary-500/20 transition-colors mr-1">编辑</button>
                  <button @click="deleteJob(job)" class="px-3 py-1 rounded-lg text-xs bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api/index.js'

const activeTab = ref('users')

const tabs = [
  { key: 'users', label: '用户中心' },
  { key: 'jobs', label: '岗位数据' },
]

const users = ref([])
const jobs = ref([])
const userSearch = ref('')
const jobSearch = ref('')

async function loadUsers() {
  try {
    const res = await adminAPI.getUsers({ search: userSearch.value })
    users.value = res.data || []
  } catch (e) { console.error('加载用户列表失败', e) }
}

async function loadJobs() {
  try {
    const res = await adminAPI.getJobs({ search: jobSearch.value })
    jobs.value = res.data || []
  } catch (e) { console.error('加载岗位列表失败', e) }
}

async function deleteUser(user) {
  if (!confirm(`确认删除用户「${user.username}」？此操作不可撤销。`)) return
  try {
    await adminAPI.deleteUser(user.id)
    users.value = users.value.filter(u => u.id !== user.id)
  } catch (e) { alert('删除失败：' + (e.response?.data?.detail || '未知错误')) }
}

async function deleteJob(job) {
  if (!confirm(`确认删除岗位「${job.title}」？此操作不可撤销。`)) return
  try {
    await adminAPI.deleteJob(job.id)
    jobs.value = jobs.value.filter(j => j.id !== job.id)
  } catch (e) { alert('删除失败：' + (e.response?.data?.detail || '未知错误')) }
}

onMounted(() => {
  loadUsers()
  loadJobs()
})
</script>
