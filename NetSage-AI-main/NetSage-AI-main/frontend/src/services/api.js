import axios from 'axios';

const API_BASE_URL = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://localhost:8000/api' 
  : '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getCases = async (params = {}) => {
  const res = await api.get('/cases', { params });
  return res.data;
};

export const getCaseById = async (id) => {
  const res = await api.get(`/cases/${id}`);
  return res.data;
};

export const createCase = async (caseData) => {
  const res = await api.post('/cases', caseData);
  return res.data;
};

export const diagnoseCase = async (id) => {
  const res = await api.post(`/cases/${id}/diagnose`);
  return res.data;
};

export const runRuleCheck = async (id) => {
  const res = await api.post(`/cases/${id}/rule-check`);
  return res.data;
};

export const runRuleCheckSandbox = async (data) => {
  const res = await api.post('/cases/rule-check/sandbox', data);
  return res.data;
};

export const submitHumanReview = async (id, reviewData) => {
  const res = await api.post(`/cases/${id}/review`, reviewData);
  return res.data;
};

export const verifyCaseFix = async (id, verificationData) => {
  const res = await api.post(`/cases/${id}/verify`, verificationData);
  return res.data;
};

export const getCaseHistory = async (id) => {
  const res = await api.get(`/cases/${id}/history`);
  return res.data;
};

export const getDashboardStats = async () => {
  const res = await api.get('/dashboard/stats');
  return res.data;
};

export const getResponsibleAILogs = async () => {
  const res = await api.get('/responsible-ai');
  return res.data;
};

export const getSystemStatus = async () => {
  const res = await axios.get('http://localhost:8000/');
  return res.data;
};

export default api;
