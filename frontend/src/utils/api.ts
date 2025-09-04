import { AxiosError } from "axios";
import axios from "axios";
import { ErrorResponse } from "../models/models";

const api = axios.create({
  baseURL: "https://gc6p3xa5c7.execute-api.us-east-1.amazonaws.com/Prod",
  headers: {
    "Content-Type": "application/json",
    Authorization:
      "eyJraWQiOiJUeEFJdFpkNElhd09FREpCWVFGRm14SmpVTCtGWFwvcVFzbFp2VXpRcmwzWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI0NDE4YzRlOC00MDQxLTcwNTctYTE5YS1mMWRlZjMzZGU0N2EiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfbmQ3MUc2WWdIIiwiY29nbml0bzp1c2VybmFtZSI6IjQ0MThjNGU4LTQwNDEtNzA1Ny1hMTlhLWYxZGVmMzNkZTQ3YSIsIm9yaWdpbl9qdGkiOiJmYTVkOTE0Ny01NDAxLTRkNGMtODgyZi05NjNhYTYzODRmOTUiLCJhdWQiOiI0Ym43djk3OGxzazI0dTN1dWFpM21ybHNmcCIsImV2ZW50X2lkIjoiMDE4NDkxZTgtZGQwOS00Y2EzLWFkZmQtNWYxZWZjNzhhZTNkIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NTY5Mzg4NDEsImV4cCI6MTc1Njk0MjQ0MSwiaWF0IjoxNzU2OTM4ODQxLCJqdGkiOiIwNzYxNDNmNy04YzcwLTRhNjEtOTM1Mi0xYmZkNzYyYWRhZGMiLCJlbWFpbCI6Im14aGVubGV5QGdtYWlsLmNvbSJ9.Ck3DalHXgEybztQsz7_6naMlXLPP5LlAsdtTrqcVZ60rBFwHppr6iRByL2cBoFZqW3LxRyw0_g6lrRZr0lzQaAxYVkA-MCDn245mtOEeUKJL4NdB1zn7Zwmgs_1Qbsz-8iuyS2ORltadXtG7L4m8uFcSKWAtQ1kzxb6Urhertpwf2hdYrd0l2IGOp3U3uw7sso6fEKAMN_yDF0Tac8VJ1s7dN6TTeNWIEjWbYrWbrXgo1Xh_egPnTtTg5CFBkaC1RBbasO91fL7ODwrirIMHSj-KujjesLj-W55a8JkX-gLAORDvnZ8EL1u93K4AJYXns32udqOU2PKy63w6FXj7cA",
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
