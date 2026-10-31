import axios from "axios";
import type { ResearchRequest, ResearchResponse } from "../types/research";

/**
 * Axios instance.
 * baseURL is always read from VITE_API_BASE_URL — never hardcoded.
 * Locally: set in frontend/.env (VITE_API_BASE_URL=http://localhost:8000)
 * Production: set in Vercel environment variables.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 120_000, // pipeline can genuinely take 60-90 seconds
  headers: {
    "Content-Type": "application/json",
  },
});

// Global response interceptor — normalise error shape
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error)) {
      const message =
        error.response?.data?.message ||
        error.response?.data?.detail ||
        error.message ||
        "Unknown error";
      return Promise.reject(new Error(message));
    }
    return Promise.reject(error);
  }
);

export async function generateReport(
  topic: string,
  mode: string
): Promise<ResearchResponse> {
  const payload: ResearchRequest = { topic, mode: mode as ResearchRequest["mode"] };
  const { data } = await api.post<ResearchResponse>("/research", payload);
  return data;
}

export default api;
