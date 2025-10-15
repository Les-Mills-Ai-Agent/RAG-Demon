import { AxiosError } from "axios";
import axios from "axios";
import { ErrorResponse } from "../models/models";

const api = axios.create({
  baseURL: import.meta.env.API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: Infinity,
});

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError<ErrorResponse>) => {
    const status = err.response?.data?.status ?? 500;
    const error = err.response?.data?.error ?? "UNKNOWN_ERROR";
    const message = err.response?.data?.message ?? err.message;

    return Promise.reject({
      status,
      error,
      message,
    } as ErrorResponse);
  }
);

export default api;
