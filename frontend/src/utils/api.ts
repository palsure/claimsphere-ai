/**
 * API utility for ClaimSphere AI
 */
import axios, { AxiosError, AxiosInstance } from 'axios';

// Get API URL from environment
const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  console.warn(
    'NEXT_PUBLIC_API_URL environment variable is not set. ' +
    'Please create a .env.local file with NEXT_PUBLIC_API_URL=http://localhost:8000'
  );
}

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token: newRefreshToken } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefreshToken);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, clear tokens
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// ============ Auth API ============

export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },
  
  register: async (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
  }) => {
    const response = await api.post('/api/auth/register', data);
    return response.data;
  },
  
  refresh: async (refreshToken: string) => {
    const response = await api.post('/api/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  
  updateProfile: async (data: { first_name?: string; last_name?: string; phone?: string }) => {
    const response = await api.put('/api/auth/me', data);
    return response.data;
  },
  
  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await api.post('/api/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

// ============ Claims API ============

export const claimsAPI = {
  list: async (params?: {
    status?: string;
    category?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await api.get('/api/claims', { params });
    return response.data;
  },
  
  get: async (claimId: string) => {
    const response = await api.get(`/api/claims/${claimId}`);
    return response.data;
  },
  
  getAnalytics: async () => {
    const response = await api.get('/api/claims/analytics');
    return response.data;
  },
  
  create: async (data: {
    plan_id?: string;
    category?: string;
    total_amount: number;
    currency?: string;
    service_date?: string;
    provider_name?: string;
    description?: string;
  }) => {
    const response = await api.post('/api/claims', data);
    return response.data;
  },
  
  update: async (claimId: string, data: any) => {
    const response = await api.put(`/api/claims/${claimId}`, data);
    return response.data;
  },
  
  delete: async (claimId: string) => {
    await api.delete(`/api/claims/${claimId}`);
  },
  
  submit: async (claimId: string) => {
    const response = await api.post(`/api/claims/${claimId}/submit`);
    return response.data;
  },
  
  updateStatus: async (claimId: string, status: string) => {
    // Use the decide endpoint for status updates
    const response = await api.post(`/api/claims/${claimId}/decide`, {
      decision: status,
      reason_description: `Status updated to ${status}`,
    });
    return response.data;
  },
  
  // Upload and create claim from document
  upload: async (file: File, processWithAI: boolean = true) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/api/claims/upload?process_with_ai=${processWithAI}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  // Upload document to existing claim
  uploadDocument: async (claimId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/api/claims/${claimId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  correctField: async (claimId: string, fieldName: string, value: string) => {
    const response = await api.post(`/api/claims/${claimId}/correct-field`, {
      field_name: fieldName,
      value,
    });
    return response.data;
  },
  
  // Agent endpoints
  getQueue: async () => {
    const response = await api.get('/api/claims/queue/pending');
    return response.data;
  },
  
  assign: async (claimId: string, agentId?: string) => {
    const response = await api.post(`/api/claims/${claimId}/assign`, null, {
      params: { agent_id: agentId },
    });
    return response.data;
  },
  
  decide: async (claimId: string, decision: {
    decision: 'approved' | 'denied' | 'pended';
    reason_code?: string;
    reason_description?: string;
    notes?: string;
    approved_amount?: number;
  }) => {
    const response = await api.post(`/api/claims/${claimId}/decide`, decision);
    return response.data;
  },
  
  // Alias for decide
  makeDecision: async (claimId: string, decision: {
    decision: 'approved' | 'denied' | 'pended';
    reason_code?: string;
    reason_description?: string;
    notes?: string;
    approved_amount?: number;
  }) => {
    const response = await api.post(`/api/claims/${claimId}/decide`, decision);
    return response.data;
  },
  
  requestInfo: async (claimId: string, message: string) => {
    const response = await api.post(`/api/claims/${claimId}/request-info`, null, {
      params: { message },
    });
    return response.data;
  },
  
  // List all claims (for admin/agent)
  listAllClaims: async (params?: {
    status?: string;
    category?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await api.get('/api/claims', { params });
    return response.data;
  },
  
  getDuplicates: async (claimId: string) => {
    const response = await api.get(`/api/claims/${claimId}/duplicates`);
    return response.data;
  },
};

// ============ Plans API ============

export const plansAPI = {
  listCompanies: async (isActive?: boolean) => {
    const response = await api.get('/api/plans/companies', {
      params: { is_active: isActive },
    });
    return response.data;
  },
  
  createCompany: async (data: any) => {
    const response = await api.post('/api/plans/companies', data);
    return response.data;
  },
  
  updateCompany: async (companyId: string, data: any) => {
    const response = await api.put(`/api/plans/companies/${companyId}`, data);
    return response.data;
  },
  
  list: async (companyId?: string, isActive?: boolean) => {
    const response = await api.get('/api/plans', {
      params: { company_id: companyId, is_active: isActive },
    });
    return response.data;
  },
  
  get: async (planId: string) => {
    const response = await api.get(`/api/plans/${planId}`);
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await api.post('/api/plans', data);
    return response.data;
  },
  
  update: async (planId: string, data: any) => {
    const response = await api.put(`/api/plans/${planId}`, data);
    return response.data;
  },
  
  deactivate: async (planId: string) => {
    const response = await api.delete(`/api/plans/${planId}`);
    return response.data;
  },
  
  getMyPolicies: async () => {
    const response = await api.get('/api/plans/policies/my');
    return response.data;
  },
};

// ============ Users API ============

export const usersAPI = {
  list: async (params?: {
    role?: string;
    is_active?: boolean;
    search?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await api.get('/api/users', { params });
    return response.data;
  },
  
  get: async (userId: string) => {
    const response = await api.get(`/api/users/${userId}`);
    return response.data;
  },
  
  create: async (data: any) => {
    const response = await api.post('/api/users', data);
    return response.data;
  },
  
  update: async (userId: string, data: any) => {
    const response = await api.put(`/api/users/${userId}`, data);
    return response.data;
  },
  
  deactivate: async (userId: string) => {
    const response = await api.delete(`/api/users/${userId}`);
    return response.data;
  },
  
  assignRole: async (userId: string, role: string) => {
    const response = await api.post(`/api/users/${userId}/roles`, null, {
      params: { role },
    });
    return response.data;
  },
  
  removeRole: async (userId: string, role: string) => {
    const response = await api.delete(`/api/users/${userId}/roles/${role}`);
    return response.data;
  },
};

// ============ Validation API ============

export const validationAPI = {
  listRules: async (planId?: string, ruleType?: string, isActive?: boolean) => {
    const response = await api.get('/api/validation/rules', {
      params: { plan_id: planId, rule_type: ruleType, is_active: isActive },
    });
    return response.data;
  },
  
  getRule: async (ruleId: string) => {
    const response = await api.get(`/api/validation/rules/${ruleId}`);
    return response.data;
  },
  
  createRule: async (data: any) => {
    const response = await api.post('/api/validation/rules', data);
    return response.data;
  },
  
  updateRule: async (ruleId: string, data: any) => {
    const response = await api.put(`/api/validation/rules/${ruleId}`, data);
    return response.data;
  },
  
  deleteRule: async (ruleId: string) => {
    const response = await api.delete(`/api/validation/rules/${ruleId}`);
    return response.data;
  },
  
  getRuleTypes: async () => {
    const response = await api.get('/api/validation/rule-types');
    return response.data;
  },
};

// ============ Query API ============

export const queryAPI = {
  ask: async (query: string, filters?: {
    date_from?: string;
    date_to?: string;
    claim_type?: string;
    status?: string;
  }) => {
    const response = await api.post('/api/query', {
      query,
      ...filters,
    });
    return response.data;
  },
};

// ============ Admin API ============

export const adminAPI = {
  getAnalytics: async (dateFrom?: string, dateTo?: string) => {
    const response = await api.get('/api/admin/analytics', {
      params: { date_from: dateFrom, date_to: dateTo },
    });
    return response.data;
  },
  
  getAuditLogs: async (params?: {
    entity_type?: string;
    entity_id?: string;
    action?: string;
    actor_user_id?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await api.get('/api/admin/audit-logs', { params });
    return response.data;
  },
  
  getDashboardStats: async () => {
    const response = await api.get('/api/admin/dashboard-stats');
    return response.data;
  },
};

export default api;
