export const API_URL: string = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(
  /\/$/,
  '',
);

export const APP_VERSION: string = __APP_VERSION__;
