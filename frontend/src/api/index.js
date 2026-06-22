import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (data) => api.post('/auth/login/', data),
  register: (data) => api.post('/auth/register/', data),
  logout: () => api.post('/auth/logout/'),
  getUser: () => api.get('/auth/user/'),
  getFavorites: () => api.get('/auth/favorites/'),
  addFavorite: (data) => api.post('/auth/favorites/', data),
  removeFavorite: (id) => api.delete(`/auth/favorites/${id}/`),
  getBrowseHistory: () => api.get('/auth/browse-history/'),
  recordBrowseHistory: (data) => api.post('/auth/browse-history/', data),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.put('/auth/profile/', data),
  updateUser: (data) => api.put('/auth/user/', data),
  changePassword: (data) => api.put('/auth/password/', data),
}

export const analysisAPI = {
  getCompanyAnalysis: (params) => api.get('/analysis/company/', { params }),
  getLocationDistribution: (params) => api.get('/analysis/location/', { params }),
  getSalaryAnalysis: (params) => api.get('/analysis/salary/', { params }),
  searchJobs: (params) => api.get('/analysis/jobs/', { params }),
  getJobDetail: (id) => api.get(`/analysis/jobs/${id}/`),
  getDashboard: () => api.get('/analysis/dashboard/'),
}

export const mlAPI = {
  getMatchOptions: () => api.get('/ml/resume-match/options/'),
  matchResume: (formData) => api.post('/ml/resume-match/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getSalaryPredictOptions: () => api.get('/ml/salary-predict/options/'),
  predictSalary: (data) => api.post('/ml/salary-predict/', data),
  getRecommendations: (params) => api.get('/ml/recommend/', { params }),
  getModelStatus: () => api.get('/ml/ml-models/'),
}

export const adminAPI = {
  getStats: () => api.get('/auth/admin/stats/'),
  getUsers: (params) => api.get('/auth/admin/users/', { params }),
  deleteUser: (id) => api.delete(`/auth/admin/users/${id}/`),
  getJobs: (params) => api.get('/auth/admin/jobs/', { params }),
  deleteJob: (id) => api.delete(`/auth/admin/jobs/${id}/`),
}

export const aiAPI = {
  chat: (data) => api.post('/chat/chat/', data),
}

export default api
