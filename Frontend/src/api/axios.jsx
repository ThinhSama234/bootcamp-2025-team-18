import axios from "axios";

const api = axios.create({
  baseURL: 'http://137.184.249.25:3000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add Authorization token if it exists
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => Promise.reject(error)
);

// // Handle 401 Unauthorized
// api.interceptors.response.use(
//   (response) => response,
//   async (error) => {
//     if (error.response?.status === 401) {
//       localStorage.removeItem('token');
//       localStorage.removeItem('user');
//       delete api.defaults.headers.common['Authorization'];
//       window.location.href = '/login';
//     }
//     return Promise.reject(error);
//   }
// );

export default api;
