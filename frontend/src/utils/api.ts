import { AxiosError } from "axios";
import axios from "axios";
import { ErrorResponse } from "../models/models";

const api = axios.create({
  baseURL: "https://gc6p3xa5c7.execute-api.us-east-1.amazonaws.com/Prod",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
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
