import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Alumni API endpoints
export const alumniAPI = {
  // Get alumni profile
  getAlumni: (alumniId) => apiClient.get(`/alumni/${alumniId}`),

  // Add new alumni
  addAlumni: (data) => apiClient.post('/alumni/add', data),

  // Record engagement
  recordEngagement: (data) => apiClient.post('/alumni/engagement', data),

  // Record donation
  recordDonation: (data) => apiClient.post('/alumni/donation', data),

  // Get engagement history
  getEngagementHistory: (alumniId) => apiClient.get(`/alumni/engagement/${alumniId}`),

  // Get donation history
  getDonationHistory: (alumniId) => apiClient.get(`/alumni/donation/${alumniId}`),

  // Get forecast
  getForecast: (data) => apiClient.post('/alumni/forecast', data),

  // Get insights (supports both GET and POST)
  getInsights: (question) => apiClient.post('/alumni/insights', { question }),

  // Get all alumni (if available)
  getAllAlumni: (params) => apiClient.get('/alumni', { params }),

  // Search alumni
  searchAlumni: (filters) => apiClient.post('/alumni/search', filters),
};

// Auth API endpoints
export const authAPI = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  logout: () => apiClient.post('/auth/logout'),
  refreshToken: () => apiClient.post('/auth/refresh'),
};

export default apiClient;
