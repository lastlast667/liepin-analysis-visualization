import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/views/LayoutView.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'analysis/company',
        name: 'CompanyAnalysis',
        component: () => import('@/views/analysis/CompanyAnalysisView.vue'),
        meta: { title: '公司分析' },
      },
      {
        path: 'analysis/location',
        name: 'LocationDistribution',
        component: () => import('@/views/analysis/LocationDistributionView.vue'),
        meta: { title: '地区分布' },
      },
      {
        path: 'analysis/jobs',
        name: 'JobSearch',
        component: () => import('@/views/analysis/JobSearchView.vue'),
        meta: { title: '岗位搜索' },
      },
      {
        path: 'analysis/salary',
        name: 'SalaryAnalysis',
        component: () => import('@/views/analysis/SalaryAnalysisView.vue'),
        meta: { title: '薪资分析' },
      },
      {
        path: 'ml/resume-match',
        name: 'ResumeMatch',
        component: () => import('@/views/ml/ResumeMatchView.vue'),
        meta: { title: '简历匹配' },
      },
      {
        path: 'ml/salary-predict',
        name: 'SalaryPrediction',
        component: () => import('@/views/ml/SalaryPredictionView.vue'),
        meta: { title: '薪资预测' },
      },
      {
        path: 'ml/recommend',
        name: 'JobRecommendation',
        component: () => import('@/views/ml/JobRecommendationView.vue'),
        meta: { title: '岗位推荐' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (!to.meta.requiresAuth && authStore.isLoggedIn && to.path !== '/login' && to.path !== '/register') {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
