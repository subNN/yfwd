const { reactive, watch } = Vue;

const getApiBaseUrl = () => {
  const { hostname, origin } = window.location;
  // 开发环境（localhost）：用同源地址
  // 生产环境：用同源地址（由 nginx/SamWAF 把 /api/* 反代到后端 5000）
  return origin;
};

export const API_BASE_URL = getApiBaseUrl();

export const store = reactive({
  menus: JSON.parse(localStorage.getItem('menus') || '[]'),
  history: JSON.parse(localStorage.getItem('history') || '[]'),
  user: JSON.parse(localStorage.getItem('userInfo') || 'null'),
  token: localStorage.getItem('token') || ''
});

watch(() => store.menus, (val) => {
  localStorage.setItem('menus', JSON.stringify(val));
}, { deep: true });

watch(() => store.history, (val) => {
  localStorage.setItem('history', JSON.stringify(val));
}, { deep: true });

watch(() => store.user, (val) => {
  if (val) {
    localStorage.setItem('userInfo', JSON.stringify(val));
  } else {
    localStorage.removeItem('userInfo');
  }
}, { deep: true });

watch(() => store.token, (val) => {
  if (val) {
    localStorage.setItem('token', val);
  } else {
    localStorage.removeItem('token');
  }
});