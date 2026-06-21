import { createClient } from '@metagptx/web-sdk';
import axios from 'axios';
import { getAPIBaseURL } from './config';

const client = createClient();

const api = axios.create({
  baseURL: getAPIBaseURL(),
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
    }
    return Promise.reject(error);
  }
);

export { client as default, api };
