import { store, API_BASE_URL } from './store.js';

const { ref, computed, onMounted } = Vue;
const { useRouter, useRoute } = VueRouter;

// --- Icons ---
const Icons = {
  home: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>`,
  menu: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>`,
  history: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
  user: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>`,
  refresh: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>`,
  chevronRight: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>`,
  back: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>`,
  plus: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>`,
  minus: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>`,
  close: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`,
  edit: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>`,
  trash: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>`,
  download: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>`,
  upload: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>`,
  cloudUpload: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>`,
  cloudDownload: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3 3m0 0l-3 3m3-3v12"/></svg>` // Reusing for simplicity
};

// --- Home Component ---
export const Home = {
  template: `
    <div class="animate-fade-up">
      <div class="mb-8 md:mb-10">
        <h1 class="text-3xl md:text-4xl font-bold tracking-tight text-zinc-900 mb-3">今天想吃点什么？</h1>
        <p class="text-zinc-500 font-medium">挑选一个菜单，开启美味的一餐</p>
      </div>

      <div class="flex gap-3 overflow-x-auto no-scrollbar pb-2 -mx-2 px-2 mb-8">
        <button v-for="meal in meals" :key="meal" 
                @click="selectedMeal = meal"
                :class="['flex-shrink-0 px-6 py-3 rounded-2xl text-sm font-medium border shadow-sm transition-all duration-300', 
                         selectedMeal === meal ? 'bg-zinc-900 text-white border-zinc-900 scale-105' : 'bg-white/80 backdrop-blur-md text-zinc-500 border-zinc-200/60 hover:bg-white']">
          {{ meal }}
        </button>
        <button @click="router.push('/ai')" type="button" class="ai-button flex-shrink-0">
          <span class="fold"></span>
          <div class="points-wrapper">
            <i class="point"></i>
            <i class="point"></i>
            <i class="point"></i>
            <i class="point"></i>
            <i class="point"></i>
            <i class="point"></i>
            <i class="point"></i>
            <i class="point"></i>
            <i class="point"></i>
            <i class="point"></i>
          </div>
          <span class="inner">
            <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5">
              <polyline points="13.18 1.37 13.18 9.64 21.45 9.64 10.82 22.63 10.82 14.36 2.55 14.36 13.18 1.37"></polyline>
            </svg>
            AI 助手
          </span>
        </button>
      </div>

      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-zinc-900 tracking-tight">我的菜单</h2>
        <button @click="refresh" :class="['flex items-center gap-1.5 text-zinc-400 text-sm hover:text-zinc-900 transition-all duration-500', isRefreshing ? 'rotate-180' : '']">
          <span v-html="Icons.refresh"></span>
        </button>
      </div>

      <transition name="fade">
        <div v-if="loading" class="text-center py-12 text-zinc-400">正在加载云端菜单...</div>
      </transition>

      <transition-group name="list" tag="div" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 relative">
        <div v-if="!loading && menus.length === 0" key="empty" class="col-span-full text-center py-20 bg-white/50 backdrop-blur-sm rounded-3xl border border-zinc-200/50 border-dashed">
          <div class="w-20 h-20 bg-zinc-100 rounded-full flex items-center justify-center mx-auto mb-5 text-3xl">🍽️</div>
          <h3 class="text-zinc-900 font-medium mb-1">暂无菜单</h3>
          <p class="text-zinc-400 text-sm mb-6">去创建一个属于你的专属菜单吧</p>
          <button @click="router.push('/menu')" class="px-8 py-3 bg-zinc-900 text-white rounded-2xl text-sm font-medium hover:bg-zinc-800 transition-colors shadow-lg shadow-zinc-900/20">
            创建菜单
          </button>
        </div>

        <div v-for="(menu, index) in menus" :key="menu.id" 
             @click="useMenu(menu)"
             class="bg-white/80 backdrop-blur-md rounded-3xl p-6 shadow-sm border border-zinc-200/50 cursor-pointer hover:shadow-md hover:bg-white hover:-translate-y-1 transition-all duration-300 active:scale-[0.98] group flex flex-col h-full">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-zinc-900 text-lg tracking-tight">{{ menu.name }}</h3>
            <span class="px-3 py-1 bg-zinc-100 text-zinc-600 rounded-full text-xs font-medium">{{ menu.dishes?.length || 0 }} 道菜</span>
          </div>
          <p class="text-sm text-zinc-500 line-clamp-2 leading-relaxed mb-6 flex-1">
            <span v-for="(dish, i) in (menu.dishes || []).slice(0, 4)" :key="i">
              {{ dish.name }}<span v-if="i < Math.min((menu.dishes || []).length, 4) - 1" class="text-zinc-300 mx-1">•</span>
            </span>
            <span v-if="(menu.dishes || []).length > 4" class="text-zinc-300 mx-1">• ...</span>
          </p>
          <div class="flex items-center text-sm font-medium text-zinc-900 mt-auto pt-4 border-t border-zinc-100">
            <span>使用此菜单</span>
            <span class="ml-1 transform transition-transform group-hover:translate-x-1" v-html="Icons.chevronRight"></span>
          </div>
        </div>
      </transition-group>
    </div>
  `,
  setup() {
    const router = useRouter();
    const meals = ['早餐', '午餐', '晚餐', '加餐'];
    const selectedMeal = ref('午餐');
    const isRefreshing = ref(false);
    const menus = ref([]);
    const loading = ref(false);

    const getAuthHeaders = () => {
      const token = localStorage.getItem('token');
      return { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token, 'token': token };
    };

    const loadMenus = async () => {
      loading.value = true;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/menus', { headers: getAuthHeaders() });
        const data = await res.json();
        if (data && data.success && Array.isArray(data.menus)) {
          menus.value = data.menus;
        } else {
          menus.value = [];
        }
      } catch (err) {
        menus.value = [];
      } finally {
        loading.value = false;
      }
    };

    const refresh = async () => {
      isRefreshing.value = true;
      await loadMenus();
      setTimeout(() => isRefreshing.value = false, 500);
    };

    const useMenu = (menu) => {
      localStorage.setItem('orderMenu', JSON.stringify(menu));
      router.push({ path: '/order-dish', query: { meal: selectedMeal.value } });
    };

    onMounted(loadMenus);

    return { meals, selectedMeal, isRefreshing, menus, loading, refresh, useMenu, router, Icons };
  }
};

// --- MenuList Component ---
export const MenuList = {
  template: `
    <div class="animate-fade-up">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold tracking-tight text-zinc-900">菜单管理</h1>
        <div class="flex items-center gap-3">
          <button @click="loadMenus" class="text-zinc-500 text-sm font-medium hover:text-zinc-900 transition-colors flex items-center gap-1">
            <span v-html="Icons.refresh"></span>
            刷新
          </button>
          <button @click="router.push('/ai')" class="text-zinc-900 text-sm font-medium hover:opacity-70 transition-opacity">AI 生成</button>
        </div>
      </div>

      <div class="flex gap-3 mb-6">
        <button @click="router.push('/edit-menu')" class="flex-1 py-3 bg-zinc-900 text-white rounded-2xl font-medium hover:bg-zinc-800 transition-colors shadow-md shadow-zinc-900/10">
          + 创建菜单
        </button>
      </div>

      <transition name="fade">
        <div v-if="loading" class="text-center py-12 text-zinc-400">正在加载...</div>
      </transition>

      <transition-group name="list" tag="div" class="grid grid-cols-1 md:grid-cols-2 gap-4 relative">
        <div v-if="!loading && menus.length === 0" key="empty" class="col-span-full text-center py-20 bg-white/50 backdrop-blur-sm rounded-3xl border border-zinc-200/50 border-dashed">
          <div class="w-20 h-20 bg-zinc-100 rounded-full flex items-center justify-center mx-auto mb-5 text-3xl">📋</div>
          <h3 class="text-zinc-900 font-medium mb-1">暂无菜单</h3>
          <p class="text-zinc-400 text-sm mb-6">点击上方按钮或用 AI 生成你的第一个菜单</p>
        </div>

        <div v-for="menu in menus" :key="menu.id"
             :class="['bg-white/80 backdrop-blur-md rounded-3xl p-5 shadow-sm border transition-all hover:shadow-md', 'border-zinc-200/50']">
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <h3 class="font-semibold text-zinc-900 tracking-tight">{{ menu.name }}</h3>
              <p class="text-xs text-zinc-400 mt-1 font-medium">{{ menu.dishes?.length || 0 }} 道菜</p>
            </div>
            <div class="flex gap-2">
              <button @click="openOrder(menu)" class="px-3 py-1.5 bg-zinc-900 text-white rounded-xl text-xs font-medium hover:bg-zinc-800 transition-colors">点菜</button>
              <button @click="openEdit(menu)" class="px-3 py-1.5 bg-white text-zinc-700 border border-zinc-200 rounded-xl text-xs font-medium hover:bg-zinc-50 transition-colors">编辑</button>
              <button @click="deleteMenu(menu)" class="p-1.5 text-zinc-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors" v-html="Icons.trash"></button>
            </div>
          </div>
          <div class="space-y-1">
            <div v-for="(dish, di) in menu.dishes" :key="di" class="flex items-center justify-between text-xs bg-zinc-50 rounded-xl px-3 py-1.5">
              <span class="text-zinc-700">{{ dish.name }}</span>
              <span v-if="dish.price" class="text-zinc-400">¥{{ dish.price }}</span>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
  `,
  setup() {
    const router = useRouter();
    const menus = ref([]);
    const loading = ref(false);

    const getAuthHeaders = () => {
      const token = localStorage.getItem('token');
      return { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token, 'token': token };
    };

    const loadMenus = async () => {
      loading.value = true;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/menus', {
          method: 'GET',
          headers: getAuthHeaders()
        });
        const data = await res.json();
        if (data && data.success && Array.isArray(data.menus)) {
          menus.value = data.menus;
        } else {
          menus.value = [];
        }
      } catch (err) {
        console.error('[菜单] 加载错误:', err);
        menus.value = [];
      } finally {
        loading.value = false;
      }
    };

    const deleteMenu = async (menu) => {
      if (!confirm(`确定要删除菜单「${menu.name}」吗？`)) return;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/menus/' + menu.id, {
          method: 'DELETE',
          headers: getAuthHeaders()
        });
        const data = await res.json();
        if (data && data.success) {
          menus.value = menus.value.filter(m => m.id !== menu.id);
        } else {
          alert('删除失败：' + (data.error || data.message || '未知错误'));
        }
      } catch (err) {
        console.error('[菜单] 删除错误:', err);
        alert('网络连接失败');
      }
    };

    const openOrder = (menu) => {
      localStorage.setItem('orderMenu', JSON.stringify(menu));
      router.push({ path: '/order-dish', query: { meal: '午餐' } });
    };

    const openEdit = (menu) => {
      router.push({ path: '/edit-menu', query: { id: menu.id } });
    };

    onMounted(loadMenus);

    return { router, Icons, menus, loading, loadMenus, deleteMenu, openOrder, openEdit };
  }
};

// --- History Component ---
export const History = {
  template: `
    <div class="animate-fade-up">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold tracking-tight text-zinc-900">历史记录</h1>
        <button @click="loadOrders" class="text-zinc-500 text-sm font-medium hover:text-zinc-900 transition-colors flex items-center gap-1">
          <span v-html="Icons.refresh"></span>
          刷新
        </button>
      </div>

      <div class="bg-zinc-900 rounded-3xl p-6 text-white shadow-lg shadow-zinc-900/20 mb-8">
        <div class="grid grid-cols-3 gap-4 divide-x divide-zinc-800">
          <div class="text-center">
            <div class="text-2xl font-bold tracking-tight">{{ stats.totalOrders }}</div>
            <div class="text-[10px] text-zinc-400 mt-1 uppercase tracking-wider font-medium">总订单</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold tracking-tight">¥{{ stats.totalAmount }}</div>
            <div class="text-[10px] text-zinc-400 mt-1 uppercase tracking-wider font-medium">总消费</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold tracking-tight">¥{{ stats.avgAmount }}</div>
            <div class="text-[10px] text-zinc-400 mt-1 uppercase tracking-wider font-medium">平均</div>
          </div>
        </div>
      </div>

      <transition name="fade">
        <div v-if="loading" class="text-center py-12 text-zinc-400">正在加载...</div>
      </transition>

      <transition-group name="list" tag="div" class="grid grid-cols-1 md:grid-cols-2 gap-4 relative">
        <div v-if="!loading && orders.length === 0" key="empty" class="col-span-full text-center py-20 bg-white/50 backdrop-blur-sm rounded-3xl border border-zinc-200/50 border-dashed">
          <div class="w-20 h-20 bg-zinc-100 rounded-full flex items-center justify-center mx-auto mb-5 text-3xl">📜</div>
          <h3 class="text-zinc-900 font-medium mb-1">暂无历史记录</h3>
          <p class="text-zinc-400 text-sm">去菜单选个餐开始点菜吧</p>
        </div>

        <div v-for="record in orders" :key="record.id" class="bg-white/80 backdrop-blur-md rounded-3xl p-5 shadow-sm border border-zinc-200/50 hover:shadow-md transition-shadow relative">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-1 bg-zinc-100 text-zinc-700 rounded-lg text-xs font-medium">{{ record.meal_type }}</span>
              <span class="text-xs text-zinc-400 font-medium">{{ record.time }}</span>
            </div>
            <button @click="deleteOrder(record)" class="p-1.5 text-zinc-300 hover:text-red-500 transition-colors" v-html="Icons.trash"></button>
          </div>
          <div class="mb-3">
            <div v-if="record.menu_name" class="text-xs text-zinc-500 mb-2">菜单：{{ record.menu_name }}</div>
            <div class="flex flex-wrap gap-2">
              <span v-for="(dish, i) in record.dishes" :key="i" class="px-3 py-1.5 bg-zinc-50 border border-zinc-100 text-zinc-600 rounded-xl text-xs font-medium">
                {{ dish.name }} <span class="text-zinc-400 ml-1">x{{ dish.quantity }}</span>
              </span>
            </div>
          </div>
          <div class="flex items-center justify-between pt-3 border-t border-zinc-100">
            <span class="text-xs text-zinc-400 font-medium">合计</span>
            <span class="text-lg font-bold text-zinc-900 tracking-tight">¥{{ record.total_amount }}</span>
          </div>
        </div>
      </transition-group>
    </div>
  `,
  setup() {
    const orders = ref([]);
    const loading = ref(false);

    const getAuthHeaders = () => {
      const token = localStorage.getItem('token');
      return { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token, 'token': token };
    };

    const stats = computed(() => {
      const totalOrders = orders.value.length;
      let totalAmount = 0;
      orders.value.forEach(record => {
        const amt = parseFloat(record.total_amount);
        if (!isNaN(amt)) totalAmount += amt;
      });
      const avgAmount = totalOrders > 0 ? (totalAmount / totalOrders).toFixed(1) : '0';
      return { totalOrders, totalAmount: totalAmount.toFixed(0), avgAmount };
    });

    const formatTime = (iso) => {
      if (!iso) return '';
      try {
        const d = new Date(iso);
        const now = new Date();
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const h = String(d.getHours()).padStart(2, '0');
        const min = String(d.getMinutes()).padStart(2, '0');
        if (y === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate()) {
          return `今天 ${h}:${min}`;
        }
        return `${m}-${day} ${h}:${min}`;
      } catch (e) {
        return iso;
      }
    };

    const loadOrders = async () => {
      loading.value = true;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/orders', {
          method: 'GET',
          headers: getAuthHeaders()
        });
        const data = await res.json();
        if (data && data.success && Array.isArray(data.orders)) {
          orders.value = data.orders.map(o => ({
            ...o,
            time: formatTime(o.order_time),
            total_amount: parseFloat(o.total_amount || 0).toFixed(2),
            dishes: Array.isArray(o.dishes) ? o.dishes : []
          }));
        } else {
          orders.value = [];
        }
      } catch (err) {
        console.error('[历史] 加载错误:', err);
        orders.value = [];
      } finally {
        loading.value = false;
      }
    };

    const deleteOrder = async (record) => {
      if (!confirm('确定要删除这条点菜记录吗？')) return;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/orders/' + record.id, {
          method: 'DELETE',
          headers: getAuthHeaders()
        });
        const data = await res.json();
        if (data && data.success) {
          orders.value = orders.value.filter(o => o.id !== record.id);
        } else {
          alert('删除失败：' + (data.error || data.message || '未知错误'));
        }
      } catch (err) {
        console.error('[历史] 删除错误:', err);
        alert('网络连接失败');
      }
    };

    onMounted(loadOrders);

    return { Icons, orders, loading, stats, loadOrders, deleteOrder };
  }
};

// --- Profile Component ---
export const Profile = {
  template: `
    <div class="animate-fade-up">
      <div class="flex items-center gap-5 mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center shadow-inner text-white text-2xl font-bold">
          {{ store.user && store.user.nickname ? store.user.nickname.charAt(0).toUpperCase() : '?' }}
        </div>
        <div>
          <div v-if="!editingNickname" class="flex items-center gap-2">
            <h2 class="text-2xl font-bold tracking-tight text-zinc-900">{{ store.user ? (store.user.nickname || '已登录') : '未登录' }}</h2>
            <button v-if="store.user" @click="startEditNickname" type="button" class="text-zinc-400 hover:text-indigo-600 transition-colors" title="编辑昵称">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
            </button>
          </div>
          <div v-else class="flex items-center gap-2">
            <input v-model="newNickname" @keyup.enter="saveNickname" @keyup.esc="cancelEditNickname" type="text" maxlength="20" class="text-2xl font-bold tracking-tight text-zinc-900 bg-zinc-100 border-2 border-indigo-300 rounded-xl px-3 py-1.5 w-48 outline-none focus:border-indigo-500" placeholder="输入新昵称" autofocus>
            <button @click="saveNickname" :disabled="updatingNickname" type="button" class="text-indigo-600 hover:text-indigo-700 transition-colors disabled:opacity-40" title="保存">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            </button>
            <button @click="cancelEditNickname" :disabled="updatingNickname" type="button" class="text-zinc-400 hover:text-zinc-600 transition-colors disabled:opacity-40" title="取消">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <p class="text-zinc-500 text-sm mt-1 font-medium">{{ store.user ? (store.user.email || '') : '登录后可同步数据到云端' }}</p>
        </div>
      </div>

      <div v-if="!store.user" @click="goLogin" class="w-full py-4 rounded-2xl font-medium transition-colors mb-8 bg-zinc-900 text-white text-center shadow-lg shadow-zinc-900/20 hover:bg-zinc-800 cursor-pointer">
        前往登录 / 注册
      </div>

      <div class="bg-white/80 backdrop-blur-md rounded-3xl overflow-hidden shadow-sm border border-zinc-200/50">
        <div @click="router.push('/import-export')" class="flex items-center justify-between px-5 py-4 border-b border-zinc-100 cursor-pointer hover:bg-white transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-zinc-100 flex items-center justify-center text-zinc-600" v-html="Icons.download"></div>
            <span class="text-zinc-700 font-medium text-sm">数据管理（同步/导入导出）</span>
          </div>
          <span class="text-zinc-300" v-html="Icons.chevronRight"></span>
        </div>

        <div @click="clearAllData" class="flex items-center justify-between px-5 py-4 border-b border-zinc-100 cursor-pointer hover:bg-zinc-50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-red-50 flex items-center justify-center text-red-500" v-html="Icons.trash"></div>
            <span class="text-red-600 font-medium text-sm">清空本地数据</span>
          </div>
          <span class="text-zinc-300" v-html="Icons.chevronRight"></span>
        </div>

        <div @click="showAbout = true" class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-zinc-50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-zinc-100 flex items-center justify-center text-zinc-600" v-html="Icons.home"></div>
            <span class="text-zinc-700 font-medium text-sm">关于我们</span>
          </div>
          <span class="text-zinc-300" v-html="Icons.chevronRight"></span>
        </div>

        <div v-if="store.user" @click="logout" class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-zinc-50 transition-colors border-t border-zinc-100">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-zinc-100 flex items-center justify-center text-zinc-600">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
            </div>
            <span class="text-zinc-700 font-medium text-sm">退出登录</span>
          </div>
          <span class="text-zinc-300" v-html="Icons.chevronRight"></span>
        </div>
      </div>

      <!-- About Modal -->
      <transition name="page">
        <div v-if="showAbout" class="fixed inset-0 bg-zinc-900/40 backdrop-blur-sm flex items-center justify-center z-50">
          <div class="bg-white rounded-3xl p-8 max-w-sm mx-6 w-full shadow-2xl">
            <div class="text-center mb-6">
              <div class="w-16 h-16 rounded-2xl overflow-hidden mx-auto mb-4 shadow-md border border-zinc-100">
                <img src="一饭为定.jpg" alt="Logo" class="w-full h-full object-cover">
              </div>
              <h3 class="text-xl font-bold text-zinc-900 tracking-tight">一饭为定</h3>
              <p class="text-xs text-zinc-400 mt-1 font-medium">Version 3.1.0 (Vue)</p>
            </div>
            <p class="text-sm text-zinc-500 text-center mb-8 leading-relaxed">极简的饮食选择工具<br>让每天的"吃什么"不再是难题</p>
            <button @click="showAbout = false" class="w-full py-3.5 bg-zinc-900 text-white rounded-2xl font-medium hover:bg-zinc-800 transition-colors">知道了</button>
          </div>
        </div>
      </transition>
    </div>
  `,
  setup() {
    const router = useRouter();
    const showAbout = ref(false);
    const editingNickname = ref(false);
    const newNickname = ref('');
    const updatingNickname = ref(false);

    const startEditNickname = () => {
      newNickname.value = store.user && store.user.nickname ? store.user.nickname : '';
      editingNickname.value = true;
    };

    const cancelEditNickname = () => {
      editingNickname.value = false;
      newNickname.value = '';
    };

    const saveNickname = async () => {
      const trimmed = newNickname.value.trim();
      if (!trimmed) {
        alert('昵称不能为空');
        return;
      }
      if (trimmed.length > 20) {
        alert('昵称不能超过 20 个字符');
        return;
      }
      if (store.user && trimmed === store.user.nickname) {
        cancelEditNickname();
        return;
      }
      updatingNickname.value = true;
      try {
        const token = localStorage.getItem('token') || store.token || '';
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
          headers['Authorization'] = 'Bearer ' + token;
          headers['token'] = token;
        }
        const res = await fetch(API_BASE_URL + '/api/auth/profile', {
          method: 'PUT',
          headers: headers,
          body: JSON.stringify({ nickname: trimmed })
        });
        const data = await res.json();
        if (data.success) {
          if (data.user) {
            store.user = data.user;
            localStorage.setItem('userInfo', JSON.stringify(data.user));
          }
          editingNickname.value = false;
          newNickname.value = '';
        } else {
          alert(data.message || '更新失败');
        }
      } catch (e) {
        alert('网络错误，请稍后再试');
      } finally {
        updatingNickname.value = false;
      }
    };

    const goLogin = () => {
      window.location.href = 'login.html';
    };

    const logout = () => {
      if (!confirm('确定要退出登录吗？')) return;
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      store.user = null;
      store.token = '';
      window.location.href = 'login.html';
    };

    const clearAllData = () => {
      if (confirm('确定要清空所有本地数据吗？此操作不可恢复。')) {
        store.menus = [];
        store.history = [];
        store.user = null;
        store.token = '';
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
        alert('本地数据已清空');
      }
    };

    return { store, router, Icons, showAbout, goLogin, logout, clearAllData, editingNickname, newNickname, updatingNickname, startEditNickname, cancelEditNickname, saveNickname };
  }
};

// --- SelectDish Component ---
export const SelectDish = {
  template: `
    <div class="animate-fade-up pb-32">
      <div class="flex items-center gap-3 mb-6">
        <button @click="router.back()" class="p-2 -ml-2 text-zinc-500 hover:text-zinc-900 transition-colors" v-html="Icons.back"></button>
        <h1 class="text-2xl font-bold tracking-tight text-zinc-900">选择菜品</h1>
      </div>

      <div class="bg-zinc-900 rounded-3xl p-6 text-white shadow-lg shadow-zinc-900/20 relative overflow-hidden mb-8">
        <div class="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-white/10 rounded-full blur-2xl"></div>
        <div class="relative z-10">
          <div class="flex items-center justify-between mb-3">
            <span class="text-zinc-400 text-sm font-medium">当前餐别</span>
            <span class="px-3 py-1 bg-white/10 rounded-xl text-xs font-medium backdrop-blur-md">{{ meal }}</span>
          </div>
          <h2 class="text-2xl font-bold tracking-tight">{{ menu.name || '未知菜单' }}</h2>
        </div>
      </div>

      <transition name="fade">
        <div v-if="loading" class="text-center py-12 text-zinc-400">正在加载...</div>
      </transition>

      <div v-if="!loading" class="flex items-center justify-between mb-5">
        <span class="text-zinc-900 font-semibold tracking-tight">所有菜品</span>
        <button @click="randomDish" class="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-100 text-zinc-700 rounded-xl text-xs font-medium hover:bg-zinc-200 transition-colors">
          <span v-html="Icons.refresh"></span> 随机选菜
        </button>
      </div>

      <div v-if="!loading && (!menu.dishes || menu.dishes.length === 0)" class="text-center py-12">
        <div class="w-16 h-16 bg-zinc-100 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">🍳</div>
        <p class="text-zinc-400 text-sm">该菜单暂无菜品</p>
      </div>

      <div v-if="!loading && menu.dishes && menu.dishes.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div v-for="(dish, index) in menu.dishes" :key="index"
             @click="toggleDish(dish)"
             :class="['bg-white/80 backdrop-blur-md rounded-2xl p-4 shadow-sm border cursor-pointer transition-all hover:shadow-md', isSelected(dish) ? 'border-zinc-900 bg-zinc-50 ring-1 ring-zinc-900' : 'border-zinc-200/50']">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <h3 class="font-semibold text-zinc-900 tracking-tight">{{ dish.name }}</h3>
              <p class="text-xs text-zinc-400 mt-1 font-medium">{{ dish.unit || '份' }}</p>
            </div>
            <div class="flex items-center gap-4">
              <span class="text-zinc-900 font-bold tracking-tight">¥{{ (dish.price || 0).toFixed(0) }}</span>
              <div v-if="isSelected(dish)" class="flex items-center gap-2 bg-zinc-100 rounded-full p-1" @click.stop>
                <button @click="updateQuantity(dish, -1)" class="w-7 h-7 flex items-center justify-center bg-white rounded-full text-zinc-600 shadow-sm" v-html="Icons.minus"></button>
                <span class="w-4 text-center font-bold text-sm">{{ getQuantity(dish) }}</span>
                <button @click="updateQuantity(dish, 1)" class="w-7 h-7 flex items-center justify-center bg-zinc-900 rounded-full text-white shadow-sm" v-html="Icons.plus"></button>
              </div>
              <div v-else class="w-8 h-8 rounded-full border border-zinc-200 flex items-center justify-center text-zinc-300" v-html="Icons.plus"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cart Panel -->
      <transition name="page">
        <div v-if="selectedDishes.length > 0" class="fixed bottom-[72px] md:bottom-6 left-0 right-0 z-40 pointer-events-none">
          <div class="max-w-md mx-auto px-4 pointer-events-auto">
            <div class="bg-white/90 backdrop-blur-xl border border-zinc-200/50 rounded-3xl p-5 shadow-2xl shadow-zinc-900/10">
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 bg-zinc-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-bold text-zinc-900">{{ selectedDishes.length }}</span>
                  </div>
                  <span class="text-zinc-500 text-sm font-medium">已选菜品</span>
                </div>
                <span class="text-2xl font-bold text-zinc-900 tracking-tight">{{ totalPriceText }}</span>
              </div>
              
              <div class="flex gap-2 overflow-x-auto no-scrollbar pb-2 mb-4 -mx-1 px-1">
                <div v-for="(dish, i) in selectedDishes" :key="i" class="flex-shrink-0 px-3 py-1.5 bg-zinc-100 text-zinc-700 rounded-xl text-xs font-medium flex items-center gap-1.5 border border-zinc-200/50">
                  {{ dish.name }} <span class="text-zinc-400">x{{ dish.quantity }}</span>
                  <button @click="removeDish(i)" class="w-4 h-4 rounded-full bg-zinc-200 flex items-center justify-center hover:bg-zinc-300 transition-colors ml-1" v-html="Icons.close"></button>
                </div>
              </div>

              <button @click="saveSelection" :disabled="saving" class="w-full py-3.5 bg-zinc-900 text-white rounded-2xl font-medium hover:bg-zinc-800 transition-colors shadow-md shadow-zinc-900/20 disabled:opacity-50">
                {{ saving ? '保存中...' : '保存到云端' }}
              </button>
            </div>
          </div>
        </div>
      </transition>
    </div>
  `,
  setup() {
    const router = useRouter();
    const route = useRoute();
    const meal = route.query.meal || '午餐';
    const menu = ref({});
    const selectedDishes = ref([]);
    const loading = ref(false);
    const saving = ref(false);

    const getAuthHeaders = () => {
      const token = localStorage.getItem('token');
      return { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token, 'token': token };
    };

    const isSelected = (dish) => selectedDishes.value.some(d => d.name === dish.name);
    const getQuantity = (dish) => {
      const found = selectedDishes.value.find(d => d.name === dish.name);
      return found ? found.quantity : 0;
    };

    const toggleDish = (dish) => {
      const idx = selectedDishes.value.findIndex(d => d.name === dish.name);
      if (idx > -1) selectedDishes.value.splice(idx, 1);
      else selectedDishes.value.push({ ...dish, quantity: 1 });
    };

    const updateQuantity = (dish, delta) => {
      const found = selectedDishes.value.find(d => d.name === dish.name);
      if (found) {
        found.quantity += delta;
        if (found.quantity <= 0) {
          selectedDishes.value = selectedDishes.value.filter(d => d.name !== dish.name);
        }
      }
    };

    const removeDish = (index) => selectedDishes.value.splice(index, 1);

    const randomDish = () => {
      if (!menu.value.dishes || menu.value.dishes.length === 0) return alert('该菜单暂无菜品');
      const available = menu.value.dishes.filter(d => !isSelected(d));
      if (available.length === 0) return alert('所有菜品已选择');
      const random = available[Math.floor(Math.random() * available.length)];
      selectedDishes.value.push({ ...random, quantity: 1 });
    };

    const totalPriceText = computed(() => {
      const hasNoPrice = selectedDishes.value.some(d => d.price === null);
      const total = selectedDishes.value.reduce((sum, d) => sum + (d.price || 0) * d.quantity, 0);
      return (hasNoPrice ? '>¥' : '¥') + total.toFixed(0);
    });

    const saveSelection = async () => {
      if (selectedDishes.value.length === 0 || saving.value) return;
      saving.value = true;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/orders', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            menu_id: menu.value.id,
            meal_type: meal,
            selected_dishes: selectedDishes.value.map(d => ({
              name: d.name,
              price: parseFloat(d.price) || 0,
              unit: d.unit || '份',
              quantity: d.quantity
            }))
          })
        });
        const data = await res.json();
        if (data && data.success) {
          alert('点菜记录已保存到云端！');
          router.push('/history');
        } else {
          alert('保存失败：' + (data.error || data.message || '未知错误'));
        }
      } catch (err) {
        console.error('[选择菜品] 保存错误:', err);
        alert('网络连接失败');
      } finally {
        saving.value = false;
      }
    };

    onMounted(() => {
      try {
        const raw = localStorage.getItem('orderMenu');
        if (raw) {
          const parsed = JSON.parse(raw);
          if (parsed && Array.isArray(parsed.dishes)) {
            menu.value = parsed;
          }
        }
      } catch (e) {
        console.error('[选择菜品] 解析错误:', e);
      }
    });

    return { router, Icons, menu, meal, selectedDishes, loading, saving, isSelected, getQuantity, toggleDish, updateQuantity, removeDish, randomDish, totalPriceText, saveSelection };
  }
};

// --- EditMenu Component ---
export const EditMenu = {
  template: `
    <div class="animate-fade-up">
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-3">
          <button @click="router.back()" class="p-2 -ml-2 text-zinc-500 hover:text-zinc-900 transition-colors" v-html="Icons.back"></button>
          <h1 class="text-2xl font-bold tracking-tight text-zinc-900">{{ isNew ? '创建菜单' : '编辑菜单' }}</h1>
        </div>
        <button @click="saveMenu" :disabled="saving" :class="['text-sm font-medium transition-opacity', saving ? 'text-zinc-300 cursor-not-allowed' : 'text-zinc-900 hover:opacity-70']">{{ saving ? '保存中...' : '保存' }}</button>
      </div>

      <div class="bg-white rounded-3xl p-5 shadow-sm border border-zinc-100 mb-8">
        <label class="block text-xs font-medium text-zinc-400 uppercase tracking-wider mb-2">菜单名称</label>
        <input v-model="menuName" type="text" placeholder="给菜单起个名字..." class="w-full bg-transparent text-xl font-bold text-zinc-900 placeholder-zinc-300 border-none focus:ring-0 p-0 outline-none">
      </div>

      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-zinc-900 tracking-tight">菜品列表</h3>
        <button @click="addDish" class="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 text-white rounded-xl text-xs font-medium hover:bg-zinc-800 transition-colors shadow-sm shadow-zinc-900/10">
          <span v-html="Icons.plus"></span> 添加菜品
        </button>
      </div>

      <transition name="fade">
        <div v-if="loading" class="text-center py-8 text-zinc-400 text-sm">正在加载菜单...</div>
      </transition>

      <transition-group name="list" tag="div" class="grid grid-cols-1 md:grid-cols-2 gap-3" v-if="!loading">
        <div v-if="dishes.length === 0" key="empty" class="col-span-full text-center py-12 bg-white/50 backdrop-blur-sm rounded-3xl border border-zinc-200/50 border-dashed mt-3">
          <div class="w-16 h-16 bg-zinc-50 rounded-full flex items-center justify-center mx-auto mb-3 text-2xl">🍳</div>
          <p class="text-zinc-400 text-sm font-medium">暂无菜品，点击上方按钮添加</p>
        </div>

        <div v-for="(dish, index) in dishes" :key="index" class="bg-white/80 backdrop-blur-md rounded-2xl p-4 shadow-sm border border-zinc-200/50 flex items-center gap-3 hover:shadow-md transition-shadow">
          <div class="flex-1">
            <input v-model="dish.name" type="text" placeholder="菜品名称" class="w-full bg-transparent text-zinc-900 font-medium placeholder-zinc-300 border-none focus:ring-0 p-0 text-sm outline-none">
          </div>
          <div class="w-px h-6 bg-zinc-100"></div>
          <div class="flex items-center gap-2 w-24">
            <span class="text-zinc-400 text-sm">¥</span>
            <input v-model.number="dish.price" type="number" placeholder="0" class="w-full bg-transparent text-zinc-900 font-bold placeholder-zinc-300 border-none focus:ring-0 p-0 text-sm outline-none">
          </div>
          <button @click="removeDish(index)" class="w-8 h-8 rounded-full bg-zinc-50 flex items-center justify-center text-zinc-400 hover:text-red-500 hover:bg-red-50 transition-colors flex-shrink-0" v-html="Icons.close"></button>
        </div>
      </transition-group>

      <div v-if="!isNew" class="mt-8">
        <button @click="deleteMenu" :disabled="saving" :class="['w-full py-4 rounded-2xl font-medium transition-colors', saving ? 'bg-red-100 text-red-300 cursor-not-allowed' : 'bg-red-50 text-red-500 hover:bg-red-100']">删除此菜单</button>
      </div>
    </div>
  `,
  setup() {
    const router = useRouter();
    const route = useRoute();
    const menuId = route.query.id ? parseInt(route.query.id) : null;
    const isNew = menuId === null;

    const menuName = ref('');
    const dishes = ref([]);
    const saving = ref(false);
    const loading = ref(false);

    const getAuthHeaders = () => {
      const token = localStorage.getItem('token');
      return { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token, 'token': token };
    };

    const loadMenu = async () => {
      if (isNew) return;
      loading.value = true;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/menus/' + menuId, {
          method: 'GET',
          headers: getAuthHeaders()
        });
        const data = await res.json();
        if (data && data.success && data.menu) {
          menuName.value = data.menu.name || '';
          dishes.value = JSON.parse(JSON.stringify(data.menu.dishes || []));
        } else {
          dishes.value = [{ name: '', price: '', unit: '份' }];
        }
      } catch (err) {
        console.error('[编辑菜单] 加载错误:', err);
        dishes.value = [{ name: '', price: '', unit: '份' }];
      } finally {
        loading.value = false;
      }
    };

    const addDish = () => dishes.value.push({ name: '', price: '', unit: '份' });
    const removeDish = (index) => dishes.value.splice(index, 1);

    const saveMenu = async () => {
      if (saving.value) return;
      if (!menuName.value.trim()) return alert('请输入菜单名称');
      const validDishes = dishes.value.filter(d => d.name && d.name.trim()).map(d => ({
        name: d.name.trim(), price: parseFloat(d.price) || 0, unit: d.unit || '份'
      }));
      if (validDishes.length === 0) return alert('请至少添加一道菜品');

      saving.value = true;
      try {
        const method = isNew ? 'POST' : 'PUT';
        const url = isNew ? '/api/user/menus' : '/api/user/menus/' + menuId;
        const res = await fetch(API_BASE_URL + url, {
          method: method,
          headers: getAuthHeaders(),
          body: JSON.stringify({ name: menuName.value.trim(), dishes: validDishes })
        });
        const data = await res.json();
        if (data && data.success) {
          alert(isNew ? '菜单已保存到数据库！' : '菜单已更新！');
          router.back();
        } else {
          alert('保存失败：' + (data.error || data.message || '未知错误'));
        }
      } catch (err) {
        console.error('[编辑菜单] 保存错误:', err);
        alert('网络连接失败，请检查网络后重试');
      } finally {
        saving.value = false;
      }
    };

    const deleteMenu = async () => {
      if (saving.value) return;
      if (!confirm('确定要删除这个菜单吗？')) return;
      saving.value = true;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/menus/' + menuId, {
          method: 'DELETE',
          headers: getAuthHeaders()
        });
        const data = await res.json();
        if (data && data.success) {
          alert('菜单已删除');
          router.back();
        } else {
          alert('删除失败：' + (data.error || data.message || '未知错误'));
        }
      } catch (err) {
        console.error('[编辑菜单] 删除错误:', err);
        alert('网络连接失败');
      } finally {
        saving.value = false;
      }
    };

    onMounted(loadMenu);

    return { router, Icons, isNew, menuName, dishes, saving, loading, addDish, removeDish, saveMenu, deleteMenu };
  }
};

// --- ImportExport Component ---
export const ImportExport = {
  template: `
    <div class="animate-fade-up">
      <div class="flex items-center gap-3 mb-8">
        <button @click="router.back()" class="p-2 -ml-2 text-zinc-500 hover:text-zinc-900 transition-colors" v-html="Icons.back"></button>
        <h1 class="text-2xl font-bold tracking-tight text-zinc-900">数据管理</h1>
      </div>

      <!-- 云端数据统计 -->
      <div class="bg-zinc-900 rounded-3xl p-6 text-white shadow-lg shadow-zinc-900/20 mb-8">
        <h3 class="text-sm font-medium text-zinc-400 mb-4 uppercase tracking-wider">云端数据</h3>
        <div class="grid grid-cols-2 gap-4 divide-x divide-zinc-800">
          <div class="text-center">
            <div class="text-3xl font-bold tracking-tight">{{ menuCount }}</div>
            <div class="text-xs text-zinc-400 mt-1 font-medium">菜单数量</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold tracking-tight">{{ orderCount }}</div>
            <div class="text-xs text-zinc-400 mt-1 font-medium">点菜记录</div>
          </div>
        </div>
      </div>

      <!-- 第一区：云端同步 -->
      <div class="bg-white/80 backdrop-blur-md rounded-3xl p-6 shadow-sm border border-zinc-200/50 mb-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-8 h-8 bg-indigo-50 rounded-full flex items-center justify-center text-indigo-500" v-html="Icons.refresh"></div>
          <div>
            <h3 class="font-semibold text-zinc-900 tracking-tight">云端同步</h3>
            <p class="text-xs text-zinc-500 mt-0.5">前端界面与云服务器数据库之间同步</p>
          </div>
        </div>
        <div class="space-y-3">
          <button @click="refreshCounts" class="w-full py-3.5 bg-indigo-50 text-indigo-700 rounded-2xl font-medium hover:bg-indigo-100 transition-colors text-sm flex items-center justify-center gap-2">
            <span v-html="Icons.refresh"></span> 从云端刷新数据
          </button>
          <button @click="uploadLocalMenus" class="w-full py-3.5 bg-violet-50 text-violet-700 rounded-2xl font-medium hover:bg-violet-100 transition-colors text-sm flex items-center justify-center gap-2">
            <span v-html="Icons.upload"></span> 本地菜单上传到云端（{{ localMenuCount }} 个）
          </button>
          <button @click="uploadLocalOrders" class="w-full py-3.5 bg-violet-50 text-violet-700 rounded-2xl font-medium hover:bg-violet-100 transition-colors text-sm flex items-center justify-center gap-2">
            <span v-html="Icons.upload"></span> 本地点菜记录上传到云端（{{ localOrderCount }} 条）
          </button>
        </div>
      </div>

      <!-- 第二区：文件导入导出 -->
      <div class="bg-white/80 backdrop-blur-md rounded-3xl p-6 shadow-sm border border-zinc-200/50 mb-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-8 h-8 bg-emerald-50 rounded-full flex items-center justify-center text-emerald-500" v-html="Icons.download"></div>
          <div>
            <h3 class="font-semibold text-zinc-900 tracking-tight">菜单数据（JSON 文件）</h3>
            <p class="text-xs text-zinc-500 mt-0.5">从云服务器下载 JSON 文件，或上传 JSON 文件到云服务器</p>
          </div>
        </div>
        <div class="space-y-3">
          <button @click="exportMenus" class="w-full py-3.5 bg-zinc-50 text-zinc-700 rounded-2xl font-medium hover:bg-zinc-100 transition-colors text-sm flex items-center justify-center gap-2">
            <span v-html="Icons.download"></span> 下载菜单 JSON
          </button>
          <div class="relative">
            <input type="file" id="menuFileInput" accept=".json" @change="handleMenuFileSelect" class="hidden">
            <button @click="triggerMenuFileInput" class="w-full py-3.5 bg-white border border-zinc-200 border-dashed text-zinc-600 rounded-2xl font-medium hover:bg-zinc-50 transition-colors text-sm flex items-center justify-center gap-2">
              <span v-html="Icons.upload"></span> 上传菜单 JSON（合并）
            </button>
          </div>
          <div class="relative">
            <input type="file" id="menuReplaceFileInput" accept=".json" @change="handleMenuReplaceFileSelect" class="hidden">
            <button @click="triggerMenuReplaceFileInput" class="w-full py-3.5 bg-amber-50 border border-amber-200 border-dashed text-amber-700 rounded-2xl font-medium hover:bg-amber-100 transition-colors text-sm flex items-center justify-center gap-2">
              <span v-html="Icons.upload"></span> 上传菜单 JSON（替换）
            </button>
          </div>
        </div>
      </div>

      <div class="bg-white/80 backdrop-blur-md rounded-3xl p-6 shadow-sm border border-zinc-200/50 mb-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-8 h-8 bg-sky-50 rounded-full flex items-center justify-center text-sky-500" v-html="Icons.download"></div>
          <div>
            <h3 class="font-semibold text-zinc-900 tracking-tight">点菜记录（JSON 文件）</h3>
            <p class="text-xs text-zinc-500 mt-0.5">从云服务器下载 JSON 文件，或上传 JSON 文件到云服务器</p>
          </div>
        </div>
        <div class="space-y-3">
          <button @click="exportOrders" class="w-full py-3.5 bg-zinc-50 text-zinc-700 rounded-2xl font-medium hover:bg-zinc-100 transition-colors text-sm flex items-center justify-center gap-2">
            <span v-html="Icons.download"></span> 下载点菜记录 JSON
          </button>
          <div class="relative">
            <input type="file" id="orderFileInput" accept=".json" @change="handleOrderFileSelect" class="hidden">
            <button @click="triggerOrderFileInput" class="w-full py-3.5 bg-white border border-zinc-200 border-dashed text-zinc-600 rounded-2xl font-medium hover:bg-zinc-50 transition-colors text-sm flex items-center justify-center gap-2">
              <span v-html="Icons.upload"></span> 上传点菜记录 JSON
            </button>
          </div>
        </div>
      </div>

      <div class="bg-zinc-50 rounded-3xl p-6 border border-zinc-200/50">
        <h3 class="text-sm font-semibold text-zinc-700 mb-3">JSON 数据格式示例</h3>
        <div class="text-xs text-zinc-500 space-y-2 font-mono">
          <div class="bg-white rounded-xl p-3 border border-zinc-100">
            <div class="text-zinc-400 mb-2 font-sans">菜单 JSON 格式:</div>
<pre>[
  {
    "name": "家常便饭",
    "dishes": [
      {"name": "红烧肉", "price": 35, "unit": "份"},
      {"name": "米饭", "price": 3, "unit": "碗"}
    ]
  }
]</pre>
          </div>
          <div class="bg-white rounded-xl p-3 border border-zinc-100">
            <div class="text-zinc-400 mb-2 font-sans">点菜记录 JSON 格式:</div>
<pre>[
  {
    "meal_type": "午餐",
    "order_time": "2026-06-21T12:30:00",
    "selected_dishes": [
      {"name": "红烧肉", "price": 35, "unit": "份", "quantity": 1}
    ]
  }
]</pre>
          </div>
        </div>
      </div>
    </div>
  `,
  setup() {
    const router = useRouter();
    const menuCount = ref(0);
    const orderCount = ref(0);
    const localMenuCount = ref(0);
    const localOrderCount = ref(0);

    const getAuthHeaders = () => {
      const token = localStorage.getItem('token');
      return { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token, 'token': token };
    };

    const refreshCounts = async () => {
      try {
        const res = await fetch(API_BASE_URL + '/api/user/menus', { headers: getAuthHeaders() });
        const data = await res.json();
        if (data && data.success) menuCount.value = data.menus ? data.menus.length : 0;
      } catch (e) {}
      try {
        const res = await fetch(API_BASE_URL + '/api/user/orders', { headers: getAuthHeaders() });
        const data = await res.json();
        if (data && data.success) orderCount.value = data.orders ? data.orders.length : 0;
      } catch (e) {}
      const localMenus = JSON.parse(localStorage.getItem('menus') || '[]');
      const localHistory = JSON.parse(localStorage.getItem('history') || '[]');
      localMenuCount.value = Array.isArray(localMenus) ? localMenus.length : 0;
      localOrderCount.value = Array.isArray(localHistory) ? localHistory.length : 0;
    };

    const downloadFile = (content, filename) => {
      const blob = new Blob([content], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    };

    const uploadLocalMenus = async () => {
      const localMenus = JSON.parse(localStorage.getItem('menus') || '[]');
      if (!localMenus || localMenus.length === 0) {
        alert('本地没有菜单数据');
        return;
      }
      if (!confirm(`确定要将本地 ${localMenus.length} 个菜单合并上传到云端吗？`)) return;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/menus/import', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ menus: localMenus, mode: 'merge' })
        });
        const result = await res.json();
        if (result && result.success) {
          alert(`上传成功！成功: ${result.imported_count} 个${result.skipped_count ? '，跳过: ' + result.skipped_count + ' 个' : ''}`);
          refreshCounts();
        } else {
          alert('上传失败：' + (result.error || result.message || '未知错误'));
        }
      } catch (err) {
        console.error('[上传] 菜单错误:', err);
        alert('网络连接失败');
      }
    };

    const uploadLocalOrders = async () => {
      const localHistory = JSON.parse(localStorage.getItem('history') || '[]');
      if (!localHistory || localHistory.length === 0) {
        alert('本地没有点菜记录数据');
        return;
      }
      const ordersToUpload = localHistory.map(item => ({
        menu_id: null,
        meal_type: item.meal || item.meal_type || '午餐',
        selected_dishes: item.dishes || item.selected_dishes || [],
        order_time: item.time || item.order_time || new Date().toISOString()
      }));
      if (!confirm(`确定要将本地 ${ordersToUpload.length} 条点菜记录上传到云端吗？`)) return;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/orders/import', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ orders: ordersToUpload })
        });
        const result = await res.json();
        if (result && result.success) {
          alert(`上传成功！成功: ${result.imported_count} 条${result.skipped_count ? '，跳过: ' + result.skipped_count + ' 条' : ''}`);
          refreshCounts();
        } else {
          alert('上传失败：' + (result.error || result.message || '未知错误'));
        }
      } catch (err) {
        console.error('[上传] 点菜记录错误:', err);
        alert('网络连接失败');
      }
    };

    const exportMenus = async () => {
      try {
        const res = await fetch(API_BASE_URL + '/api/user/menus/export', { headers: getAuthHeaders() });
        const data = await res.json();
        if (data && data.success) {
          downloadFile(JSON.stringify(data.menus || [], null, 2), 'menus.json');
        } else {
          alert('下载失败：' + (data.error || data.message || '未知错误'));
        }
      } catch (err) {
        console.error('[下载] 菜单错误:', err);
        alert('网络连接失败');
      }
    };

    const exportOrders = async () => {
      try {
        const res = await fetch(API_BASE_URL + '/api/user/orders/export', { headers: getAuthHeaders() });
        const data = await res.json();
        if (data && data.success) {
          downloadFile(JSON.stringify(data.orders || [], null, 2), 'orders.json');
        } else {
          alert('下载失败：' + (data.error || data.message || '未知错误'));
        }
      } catch (err) {
        console.error('[下载] 订单错误:', err);
        alert('网络连接失败');
      }
    };

    const triggerMenuFileInput = () => document.getElementById('menuFileInput').click();
    const triggerMenuReplaceFileInput = () => document.getElementById('menuReplaceFileInput').click();
    const triggerOrderFileInput = () => document.getElementById('orderFileInput').click();

    const importMenus = async (data, mode) => {
      try {
        const modeText = mode === 'replace' ? '替换' : '合并';
        if (!confirm(`确定要${modeText}上传菜单数据到云端吗？${mode === 'replace' ? '这将删除云端所有菜单！' : ''}`)) return;

        const res = await fetch(API_BASE_URL + '/api/user/menus/import', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ menus: data, mode: mode })
        });
        const result = await res.json();
        if (result && result.success) {
          alert(`上传成功！成功: ${result.imported_count} 个${result.skipped_count ? '，跳过: ' + result.skipped_count + ' 个' : ''}`);
          refreshCounts();
        } else {
          alert('上传失败：' + (result.error || result.message || '未知错误'));
        }
      } catch (err) {
        console.error('[上传] 菜单错误:', err);
        alert('网络连接失败');
      }
    };

    const handleMenuFileSelect = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        try {
          const data = JSON.parse(ev.target.result);
          importMenus(data, 'merge');
        } catch (err) { alert('文件解析失败，请检查 JSON 格式'); }
      };
      reader.readAsText(file);
      e.target.value = '';
    };

    const handleMenuReplaceFileSelect = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        try {
          const data = JSON.parse(ev.target.result);
          importMenus(data, 'replace');
        } catch (err) { alert('文件解析失败，请检查 JSON 格式'); }
      };
      reader.readAsText(file);
      e.target.value = '';
    };

    const handleOrderFileSelect = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = async (ev) => {
        try {
          const data = JSON.parse(ev.target.result);
          if (!confirm('确定要上传点菜记录到云端吗？')) return;

          const res = await fetch(API_BASE_URL + '/api/user/orders/import', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ orders: data })
          });
          const result = await res.json();
          if (result && result.success) {
            alert(`上传成功！成功: ${result.imported_count} 条${result.skipped_count ? '，跳过: ' + result.skipped_count + ' 条' : ''}`);
            refreshCounts();
          } else {
            alert('上传失败：' + (result.error || result.message || '未知错误'));
          }
        } catch (err) {
          console.error('[上传] 订单错误:', err);
          alert('文件解析失败，请检查 JSON 格式');
        }
      };
      reader.readAsText(file);
      e.target.value = '';
    };

    refreshCounts();
    return { router, Icons, menuCount, orderCount, localMenuCount, localOrderCount, refreshCounts, uploadLocalMenus, uploadLocalOrders, exportMenus, exportOrders, triggerMenuFileInput, triggerMenuReplaceFileInput, triggerOrderFileInput, handleMenuFileSelect, handleMenuReplaceFileSelect, handleOrderFileSelect };
  }
};

// ==================== 点菜（从菜单中选择菜品） ====================
export const OrderDish = {
  template: `
    <div class="animate-fade-up">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-zinc-900">点菜</h1>
          <p v-if="menu" class="text-sm text-zinc-500 mt-1">{{ menu.name }}</p>
        </div>
        <button @click="router.push('/menu')" class="text-zinc-500 text-sm font-medium hover:text-zinc-900 transition-colors">返回菜单</button>
      </div>

      <div v-if="!menu" class="text-center py-20 bg-white/50 backdrop-blur-sm rounded-3xl border border-zinc-200/50 border-dashed">
        <div class="w-20 h-20 bg-zinc-100 rounded-full flex items-center justify-center mx-auto mb-5 text-3xl">🍽️</div>
        <h3 class="text-zinc-900 font-medium mb-1">未选择菜单</h3>
        <p class="text-zinc-400 text-sm mb-6">请先去菜单页面选择一个菜单</p>
        <button @click="router.push('/menu')" class="px-6 py-3 bg-zinc-900 text-white rounded-2xl text-sm font-medium hover:bg-zinc-800 transition-colors">
          去选择菜单
        </button>
      </div>

      <div v-else>
        <div class="mb-6">
          <label class="block text-xs text-zinc-500 font-medium mb-2">用餐类型</label>
          <div class="flex gap-2">
            <button v-for="mt in mealTypes" :key="mt"
                    @click="mealType = mt"
                    :class="['flex-1 py-3 rounded-2xl text-sm font-medium border transition-all', mealType === mt ? 'bg-zinc-900 text-white border-zinc-900' : 'bg-white text-zinc-700 border-zinc-200 hover:bg-zinc-50']">
              {{ mt }}
            </button>
          </div>
        </div>

        <div class="bg-white/80 backdrop-blur-md rounded-3xl p-5 shadow-sm border border-zinc-200/50 mb-6">
          <h3 class="text-sm font-semibold text-zinc-900 mb-4">选择菜品</h3>
          <div class="space-y-2">
            <div v-for="(dish, di) in menu.dishes" :key="di"
                 class="flex items-center justify-between bg-zinc-50 rounded-2xl px-4 py-3">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-white border border-zinc-100 flex items-center justify-center">
                  <span class="text-xs text-zinc-400">🍜</span>
                </div>
                <div>
                  <div class="text-sm font-medium text-zinc-900">{{ dish.name }}</div>
                  <div v-if="dish.price" class="text-xs text-zinc-400 mt-0.5">¥{{ dish.price }} / {{ dish.unit || '份' }}</div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <button @click="decQty(di)" :disabled="getQty(di) <= 0"
                        :class="['w-7 h-7 rounded-lg flex items-center justify-center transition-colors', getQty(di) > 0 ? 'bg-white border border-zinc-200 text-zinc-700 hover:bg-zinc-100' : 'bg-zinc-50 border border-zinc-100 text-zinc-300 cursor-not-allowed']">
                  <span v-html="Icons.minus"></span>
                </button>
                <span class="text-sm font-semibold text-zinc-900 w-6 text-center">{{ getQty(di) }}</span>
                <button @click="incQty(di)"
                        class="w-7 h-7 rounded-lg flex items-center justify-center bg-zinc-900 text-white hover:bg-zinc-800 transition-colors">
                  <span v-html="Icons.plus"></span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-zinc-900 rounded-3xl p-6 text-white shadow-lg shadow-zinc-900/20">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-zinc-400 font-medium">菜品数量</span>
            <span class="text-sm font-semibold">{{ totalQty }} 份</span>
          </div>
          <div class="flex items-center justify-between mb-5 pb-5 border-b border-zinc-800">
            <span class="text-sm text-zinc-400 font-medium">合计金额</span>
            <span class="text-2xl font-bold tracking-tight">¥{{ totalPrice.toFixed(2) }}</span>
          </div>
          <button @click="submitOrder" :disabled="submitting || totalQty === 0"
                  :class="['w-full py-3 rounded-2xl text-sm font-semibold transition-all', (submitting || totalQty === 0) ? 'bg-zinc-700 text-zinc-400 cursor-not-allowed' : 'bg-white text-zinc-900 hover:bg-zinc-100']">
            {{ submitting ? '提交中...' : '确认点菜' }}
          </button>
        </div>
      </div>
    </div>
  `,
  setup() {
    const router = useRouter();
    const route = useRoute();
    const menu = ref(null);
    const mealType = ref(route.query.meal || '午餐');
    const quantities = ref({});
    const submitting = ref(false);
    const mealTypes = ['早餐', '午餐', '晚餐', '夜宵', '加餐'];

    const getAuthHeaders = () => {
      const token = localStorage.getItem('token');
      return { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token, 'token': token };
    };

    const getQty = (di) => quantities.value[di] || 0;
    const incQty = (di) => quantities.value[di] = getQty(di) + 1;
    const decQty = (di) => { if (getQty(di) > 0) quantities.value[di] = getQty(di) - 1; };

    const totalQty = computed(() => Object.values(quantities.value).reduce((a, b) => a + b, 0));
    const totalPrice = computed(() => {
      if (!menu.value) return 0;
      let total = 0;
      menu.value.dishes.forEach((dish, di) => {
        const qty = getQty(di);
        const price = parseFloat(dish.price) || 0;
        total += qty * price;
      });
      return total;
    });

    const submitOrder = async () => {
      if (submitting.value || totalQty.value === 0) return;
      const selectedDishes = [];
      menu.value.dishes.forEach((dish, di) => {
        const qty = getQty(di);
        if (qty > 0) {
          selectedDishes.push({
            name: dish.name,
            price: parseFloat(dish.price) || 0,
            unit: dish.unit || '份',
            quantity: qty
          });
        }
      });
      if (selectedDishes.length === 0) return;

      submitting.value = true;
      try {
        const res = await fetch(API_BASE_URL + '/api/user/orders', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            menu_id: menu.value.id,
            meal_type: mealType.value,
            selected_dishes: selectedDishes
          })
        });
        const data = await res.json();
        if (data && data.success) {
          alert('点菜记录已保存到云端！');
          localStorage.removeItem('orderMenu');
          router.push('/history');
        } else {
          alert('提交失败：' + (data.error || data.message || '未知错误'));
        }
      } catch (err) {
        console.error('[点菜] 提交错误:', err);
        alert('网络连接失败');
      } finally {
        submitting.value = false;
      }
    };

    onMounted(() => {
      try {
        const raw = localStorage.getItem('orderMenu');
        if (raw) {
          const parsed = JSON.parse(raw);
          if (parsed && Array.isArray(parsed.dishes)) {
            menu.value = parsed;
            quantities.value = {};
            menu.value.dishes.forEach((_, di) => quantities.value[di] = 0);
          }
        }
      } catch (e) {
        console.error('[点菜] 解析菜单错误:', e);
      }
    });

    return { router, Icons, menu, mealType, mealTypes, quantities, submitting, getQty, incQty, decQty, totalQty, totalPrice, submitOrder };
  }
};

// ==================== AI 助手（菜单生成 + 对话 + 推荐菜品） ====================
export const AIAssistant = {
  template: `
    <div class="animate-fade-up h-full flex flex-col">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold tracking-tight text-zinc-900">AI 美食助手</h1>
        <button @click="clearChat" class="text-xs text-zinc-500 hover:text-zinc-900 transition-colors">清空对话</button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        <button @click="quickAction('menu')" :class="['p-4 rounded-2xl border text-left transition-all', currentTab === 'menu' ? 'bg-zinc-900 text-white border-zinc-900' : 'bg-white border-zinc-200 hover:bg-zinc-50']">
          <div class="text-lg mb-1">🍽️</div>
          <div class="font-semibold text-sm">生成菜单</div>
          <div class="text-xs opacity-70 mt-1">描述你的需求，AI 帮你创建菜单</div>
        </button>
        <button @click="quickAction('recommend')" :class="['p-4 rounded-2xl border text-left transition-all', currentTab === 'recommend' ? 'bg-zinc-900 text-white border-zinc-900' : 'bg-white border-zinc-200 hover:bg-zinc-50']">
          <div class="text-lg mb-1">✨</div>
          <div class="font-semibold text-sm">推荐菜品</div>
          <div class="text-xs opacity-70 mt-1">根据口味偏好推荐菜品</div>
        </button>
        <button @click="quickAction('chat')" :class="['p-4 rounded-2xl border text-left transition-all', currentTab === 'chat' ? 'bg-zinc-900 text-white border-zinc-900' : 'bg-white border-zinc-200 hover:bg-zinc-50']">
          <div class="text-lg mb-1">💬</div>
          <div class="font-semibold text-sm">自由对话</div>
          <div class="text-xs opacity-70 mt-1">和 AI 聊聊美食话题</div>
        </button>
      </div>

      <div class="flex-1 bg-white rounded-3xl border border-zinc-200/50 flex flex-col overflow-hidden shadow-sm">
        <div class="flex-1 overflow-y-auto p-5 space-y-4" ref="chatContainer">
          <div v-if="messages.length === 0" class="text-center py-12">
            <div class="text-5xl mb-3">🍜</div>
            <div class="text-zinc-900 font-semibold mb-1">你好！我是一饭为定 AI 助手</div>
            <div class="text-sm text-zinc-500">告诉我你想吃什么，我来帮你规划美味的一餐</div>
            <div class="mt-6 flex flex-wrap gap-2 justify-center">
              <button v-for="suggestion in suggestions" :key="suggestion" @click="sendMessage(suggestion)" class="px-4 py-2 bg-zinc-50 hover:bg-zinc-100 text-zinc-700 text-xs rounded-xl transition-colors border border-zinc-200/50">
                {{ suggestion }}
              </button>
            </div>
          </div>

          <div v-for="(msg, index) in messages" :key="index" :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
            <div :class="['max-w-[85%] rounded-2xl p-4 shadow-sm', msg.role === 'user' ? 'bg-zinc-900 text-white' : 'bg-zinc-50 text-zinc-800 border border-zinc-200/50']">
              <div v-if="msg.type === 'text'" class="text-sm whitespace-pre-wrap leading-relaxed">{{ msg.content }}</div>

              <div v-if="msg.type === 'menu'" class="min-w-[220px]">
                <div v-if="msg.text_intro" class="text-sm whitespace-pre-wrap leading-relaxed mb-3 text-zinc-700">{{ msg.text_intro }}</div>
                <div v-else class="text-xs opacity-70 mb-3">📋 为你生成的菜单</div>

                <div class="font-bold text-base mb-3">{{ msg.content.name }}</div>
                <div class="space-y-1.5 mb-4">
                  <div v-for="(dish, di) in msg.content.dishes" :key="di" class="flex items-center justify-between text-sm bg-white/50 rounded-xl px-3 py-2">
                    <span>{{ dish.name }}</span>
                    <span v-if="dish.price" class="text-xs opacity-70">¥{{ dish.price }}</span>
                  </div>
                </div>

                <div v-if="msg.raw_json" class="relative bg-zinc-900 text-zinc-100 rounded-xl p-3 mb-3 text-xs font-mono">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-zinc-400 text-xs">JSON（点击按钮复制/下载）</span>
                    <div class="flex items-center gap-1">
                      <button @click="copyJson(msg.raw_json, $event)" class="px-2 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg text-xs transition-colors">
                        {{ msg.copied ? '✓ 已复制' : '📋 复制' }}
                      </button>
                      <button @click="downloadJson(msg.raw_json, msg.content.name || 'menu', $event)" class="px-2 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg text-xs transition-colors">
                        💾 下载
                      </button>
                    </div>
                  </div>
                  <pre class="text-xs text-zinc-300 overflow-x-auto whitespace-pre-wrap break-all max-h-48">{{ msg.raw_json }}</pre>
                </div>

                <button v-if="!msg.saved" @click="saveMenu(index)" class="w-full py-2.5 bg-white text-zinc-900 rounded-xl text-sm font-semibold hover:bg-zinc-100 transition-colors">
                  💾 保存这个菜单
                </button>
                <div v-else class="text-xs text-center opacity-70 py-2">✓ 已保存到菜单列表</div>
              </div>

              <div v-if="msg.type === 'recommend'" class="min-w-[220px]">
                <div v-if="msg.text_intro" class="text-sm whitespace-pre-wrap leading-relaxed mb-3 text-zinc-700">{{ msg.text_intro }}</div>
                <div v-else class="text-xs opacity-70 mb-3">✨ 为你推荐</div>

                <div class="space-y-2 mb-4">
                  <div v-for="(dish, di) in msg.content.dishes" :key="di" class="bg-white/50 rounded-xl p-3">
                    <div class="font-semibold text-sm">{{ dish.name }}</div>
                    <div v-if="dish.price" class="text-xs opacity-60 mt-1">¥{{ dish.price }} / {{ dish.unit || '份' }}</div>
                    <div v-if="dish.reason" class="text-xs opacity-70 mt-1">{{ dish.reason }}</div>
                    <div v-if="dish.category" class="text-xs opacity-60 mt-1">{{ dish.category }}</div>
                  </div>
                </div>

                <div v-if="msg.raw_json" class="relative bg-zinc-900 text-zinc-100 rounded-xl p-3 mb-3 text-xs font-mono">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-zinc-400 text-xs">JSON（点击按钮复制/下载）</span>
                    <div class="flex items-center gap-1">
                      <button @click="copyJson(msg.raw_json, $event)" class="px-2 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg text-xs transition-colors">
                        {{ msg.copied ? '✓ 已复制' : '📋 复制' }}
                      </button>
                      <button @click="downloadJson(msg.raw_json, 'recommend', $event)" class="px-2 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg text-xs transition-colors">
                        💾 下载
                      </button>
                    </div>
                  </div>
                  <pre class="text-xs text-zinc-300 overflow-x-auto whitespace-pre-wrap break-all max-h-48">{{ msg.raw_json }}</pre>
                </div>

                <div v-if="msg.content.summary" class="text-xs opacity-70 italic">{{ msg.content.summary }}</div>
              </div>

              <div v-if="msg.type === 'error'" class="text-sm">
                <div class="flex items-center gap-2 mb-1">
                  <span>⚠️</span>
                  <span class="font-semibold text-red-500">出错了</span>
                </div>
                <div class="text-xs opacity-70">{{ msg.content }}</div>
              </div>
            </div>
          </div>

          <div v-if="loading" class="flex justify-start">
            <div class="bg-zinc-50 text-zinc-800 border border-zinc-200/50 rounded-2xl p-4 shadow-sm">
              <div class="flex items-center gap-2 text-sm">
                <div class="flex gap-1">
                  <span class="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                  <span class="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                  <span class="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                </div>
                <span>AI 正在思考...</span>
              </div>
            </div>
          </div>
        </div>

        <div class="border-t border-zinc-100 p-4">
          <div class="flex gap-2">
            <input v-model="inputText" @keyup.enter="sendMessage()" :placeholder="inputPlaceholder" class="flex-1 bg-zinc-50 text-zinc-900 placeholder-zinc-400 rounded-2xl px-4 py-3 text-sm border border-zinc-200/50 focus:outline-none focus:ring-2 focus:ring-zinc-900/20 focus:bg-white transition-all">
            <button @click="sendMessage()" :disabled="loading || !inputText.trim()" class="px-5 py-3 bg-zinc-900 text-white rounded-2xl text-sm font-medium hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              发送
            </button>
          </div>
          <div class="text-xs text-zinc-400 mt-2 text-center">按 Enter 发送消息</div>
        </div>
      </div>
    </div>
  `,
  setup() {
    const { ref, nextTick, onMounted } = Vue;

    const currentTab = ref('menu');
    const inputText = ref('');
    const messages = ref([]);
    const loading = ref(false);
    const chatContainer = ref(null);

    const suggestions = [
      '帮我做一个3人份的家常菜菜单',
      '推荐几道适合夏天的凉菜',
      '我想吃辣的，有什么推荐',
      '给我推荐简单快手的早餐'
    ];

    const inputPlaceholder = computed(() => {
      if (currentTab.value === 'menu') return '描述你想要的菜单，例如：3人份的清淡晚餐';
      if (currentTab.value === 'recommend') return '描述你的口味偏好，例如：想吃辣的、清淡的...';
      return '和 AI 聊聊美食话题...';
    });

    const scrollToBottom = async () => {
      await nextTick();
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    };

    const quickAction = (tab) => {
      currentTab.value = tab;
    };

    const clearChat = () => {
      if (confirm('确定清空所有对话吗？')) {
        messages.value = [];
      }
    };

    const getAuthHeaders = () => {
      const token = store.token || localStorage.getItem('token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = 'Bearer ' + token;
        headers['token'] = token;
      }
      return headers;
    };

    const sendMessage = async (text) => {
      const content = text || inputText.value.trim();
      if (!content || loading.value) return;

      messages.value.push({ role: 'user', type: 'text', content });
      inputText.value = '';
      loading.value = true;
      await scrollToBottom();

      try {
        let endpoint, body;

        if (currentTab.value === 'menu') {
          endpoint = '/api/ai/create-menu';
          body = { description: content, save: false };
        } else if (currentTab.value === 'recommend') {
          endpoint = '/api/ai/recommend';
          body = { preference: content };
        } else {
          endpoint = '/api/ai/chat';
          body = { message: content, save_menu: false };
        }

        const response = await fetch(API_BASE_URL + endpoint, {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!data.success) {
          messages.value.push({
            role: 'assistant',
            type: 'error',
            content: data.message || data.error || 'AI 服务暂时不可用'
          });
          await scrollToBottom();
          return;
        }

        if (currentTab.value === 'menu') {
          if (data.menu) {
            messages.value.push({
              role: 'assistant',
              type: 'menu',
              content: data.menu,
              text_intro: data.text_intro || '',
              raw_json: data.raw_json || JSON.stringify(data.menu, null, 2),
              saved: false
            });
          } else {
            messages.value.push({
              role: 'assistant',
              type: 'text',
              content: '菜单生成成功！'
            });
          }
        } else if (currentTab.value === 'recommend') {
          if (data.dishes || (data.data && data.data.dishes)) {
            const content = data.data || { dishes: data.dishes, summary: data.summary || '' };
            messages.value.push({
              role: 'assistant',
              type: 'recommend',
              content: content,
              text_intro: data.text_intro || '',
              raw_json: data.raw_json || JSON.stringify(content, null, 2)
            });
          } else {
            messages.value.push({
              role: 'assistant',
              type: 'text',
              content: '推荐生成完成！'
            });
          }
        } else {
          if (data.type === 'action' && data.data && data.data.action === 'create_menu') {
            messages.value.push({
              role: 'assistant',
              type: 'menu',
              content: data.data,
              text_intro: data.text_intro || '',
              raw_json: data.raw_json || JSON.stringify(data.data, null, 2),
              saved: !!data.saved
            });
          } else if (data.type === 'action' && data.data) {
            messages.value.push({
              role: 'assistant',
              type: 'recommend',
              content: data.data,
              text_intro: data.text_intro || '',
              raw_json: data.raw_json || JSON.stringify(data.data, null, 2)
            });
          } else {
            const reply = data.reply || (data.data && data.data.reply) || data.text || data.content || data.message;
            messages.value.push({
              role: 'assistant',
              type: 'text',
              content: reply || 'AI 已返回内容，但前端暂时无法识别，请稍后重试。'
            });
          }
        }
      } catch (err) {
        console.error('[AI] 请求错误:', err);
        messages.value.push({
          role: 'assistant',
          type: 'error',
          content: '网络连接失败，请检查网络后重试'
        });
      } finally {
        loading.value = false;
        await scrollToBottom();
      }
    };

    const saveMenu = async (msgIndex) => {
      const msg = messages.value[msgIndex];
      if (!msg || msg.type !== 'menu') return;

      const name = msg.content.name || 'AI 生成的菜单';
      const dishes = (msg.content.dishes || []).map(d => ({
        name: d.name,
        price: parseFloat(d.price) || 0,
        unit: d.unit || '份'
      }));

      try {
        const res = await fetch(API_BASE_URL + '/api/user/menus', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ name, dishes })
        });
        const data = await res.json();

        if (data && data.success) {
          msg.saved = true;
          alert('菜单已保存到数据库！');
        } else {
          alert('保存失败：' + (data.error || data.message || '未知错误'));
        }
      } catch (err) {
        console.error('[AI] 保存菜单错误:', err);
        alert('网络连接失败，请检查网络后重试');
      }
    };

    const copyJson = (jsonStr, event) => {
      try {
        navigator.clipboard.writeText(jsonStr);
      } catch (e) {
        const textarea = document.createElement('textarea');
        textarea.value = jsonStr;
        document.body.appendChild(textarea);
        textarea.select();
        try { document.execCommand('copy'); } catch (_) {}
        document.body.removeChild(textarea);
      }

      const msg = event && event.target.closest('.min-w-\\[220px\\], [class*="min-w"]');
      if (msg) {
        const btn = msg.querySelector('button');
        if (btn) {
          const original = btn.textContent;
          btn.textContent = '✓ 已复制';
          setTimeout(() => { btn.textContent = original; }, 1500);
        }
      }
    };

    const downloadJson = (jsonStr, filename) => {
      const safeName = (filename || 'data').replace(/[\\/:*?"<>|\s]/g, '_').slice(0, 60);
      const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = safeName + '.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    };

    return {
      currentTab, inputText, messages, loading, chatContainer,
      suggestions, inputPlaceholder,
      sendMessage, clearChat, saveMenu, quickAction, copyJson, downloadJson
    };
  }
};