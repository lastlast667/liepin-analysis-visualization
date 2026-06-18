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
}

export const analysisAPI = {
  getCompanyAnalysis: (params) => api.get('/analysis/company/', { params }),
  getLocationDistribution: (params) => api.get('/analysis/location/', { params }),
  getSalaryAnalysis: (params) => api.get('/analysis/salary/', { params }),
  searchJobs: (params) => api.get('/analysis/jobs/', { params }),
  getJobDetail: (id) => api.get(`/analysis/jobs/${id}/`),
}

export const mlAPI = {
  getMatchOptions: () => api.get('/ml/resume-match/options/'),
  matchResume: (formData) => api.post('/ml/resume-match/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getSalaryPredictOptions: () => api.get('/ml/salary-predict/options/'),
  predictSalary: (data) => api.post('/ml/salary-predict/', data),
}

export default api
