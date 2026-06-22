import { Home, MenuList, History, Profile, SelectDish, EditMenu, ImportExport, AIAssistant, OrderDish } from './components.js';
import { store } from './store.js';

const { createApp } = Vue;
const { createRouter, createWebHashHistory } = VueRouter;

// 登录守卫：未登录跳转到 login.html
const ensureAuth = () => {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('userInfo');
  return Boolean(token && user);
}

// 进入应用前先校验登录态
if (!ensureAuth()) {
  // 触发跳转到登录页，停止后续初始化
  window.location.replace('login.html');
} else {
  initApp();
}

function initApp() {

const routes = [
  { path: '/', component: Home },
  { path: '/menu', component: MenuList },
  { path: '/order-dish', component: OrderDish },
  { path: '/history', component: History },
  { path: '/profile', component: Profile },
  { path: '/select-dish', component: SelectDish },
  { path: '/edit-menu', component: EditMenu },
  { path: '/import-export', component: ImportExport },
  { path: '/ai', component: AIAssistant }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

const AppLayout = {
  template: `
    <div class="flex h-screen overflow-hidden bg-zinc-50">
      <!-- Sidebar (Desktop) -->
      <aside class="hidden md:flex flex-col w-64 bg-white border-r border-zinc-200/60 px-6 py-8 z-20">
        <div class="flex items-center gap-3 mb-12">
          <div class="w-10 h-10 rounded-xl overflow-hidden shadow-lg shadow-zinc-900/10 border border-zinc-100 flex-shrink-0">
            <img src="一饭为定.jpg" alt="Logo" class="w-full h-full object-cover">
          </div>
          <h1 class="text-xl font-bold tracking-tight">一饭为定</h1>
        </div>
        <nav class="flex-1 space-y-2">
          <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900" active-class="bg-zinc-900 !text-white font-semibold shadow-md shadow-zinc-900/10">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
            首页
          </router-link>
          <router-link to="/ai" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900" active-class="bg-zinc-900 !text-white font-semibold shadow-md shadow-zinc-900/10">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
            AI 助手
          </router-link>
          <router-link to="/menu" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900" active-class="bg-zinc-900 !text-white font-semibold shadow-md shadow-zinc-900/10">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>
            菜单
          </router-link>
          <router-link to="/history" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900" active-class="bg-zinc-900 !text-white font-semibold shadow-md shadow-zinc-900/10">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            历史
          </router-link>
          <router-link to="/profile" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900" active-class="bg-zinc-900 !text-white font-semibold shadow-md shadow-zinc-900/10">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
            我的
          </router-link>
        </nav>

        <!-- 底部用户信息 + 退出 -->
        <div class="pt-4 border-t border-zinc-100">
          <div class="flex items-center gap-3 px-3 py-2 mb-2">
            <div class="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white text-sm font-semibold shadow-sm flex-shrink-0">
              {{ (store.user && store.user.nickname ? store.user.nickname : 'U').charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-zinc-900 truncate">{{ store.user && store.user.nickname ? store.user.nickname : '已登录' }}</div>
              <div class="text-[10px] text-zinc-400">在线</div>
            </div>
          </div>
          <button @click="logout" class="w-full flex items-center gap-2 px-3 py-2 text-sm text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50 rounded-xl transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
            退出登录
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 flex flex-col h-screen overflow-hidden relative bg-zinc-50/50">
        <!-- Decorative Ambient Background -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <div class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-gradient-to-br from-indigo-100/40 to-purple-100/40 blur-3xl"></div>
          <div class="absolute top-[20%] -right-[10%] w-[40%] h-[40%] rounded-full bg-gradient-to-br from-zinc-200/40 to-zinc-100/40 blur-3xl"></div>
          <div class="absolute -bottom-[20%] left-[20%] w-[60%] h-[60%] rounded-full bg-gradient-to-br from-orange-100/30 to-rose-100/30 blur-3xl"></div>
        </div>

        <!-- Header (Mobile) -->
        <header class="md:hidden bg-white/80 backdrop-blur-xl border-b border-zinc-200/50 px-6 py-4 flex items-center justify-between sticky top-0 z-30 pt-safe">
           <div class="flex items-center gap-2">
             <div class="w-8 h-8 rounded-lg overflow-hidden shadow-md border border-zinc-100 flex-shrink-0">
               <img src="一饭为定.jpg" alt="Logo" class="w-full h-full object-cover">
             </div>
             <h1 class="text-lg font-bold tracking-tight">一饭为定</h1>
           </div>
           <button @click="logout" class="text-zinc-500 hover:text-zinc-900 transition-colors p-1.5" aria-label="退出登录">
             <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
           </button>
        </header>

        <!-- Scrollable Content -->
        <div class="flex-1 overflow-y-auto p-6 md:p-10 pb-24 md:pb-10 relative no-scrollbar z-10" id="main-scroll">
          <div class="max-w-5xl mx-auto">
            <router-view v-slot="{ Component }">
              <transition name="page" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </div>

        <!-- Bottom Nav (Mobile) -->
        <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-xl border-t border-zinc-200/50 pb-safe z-40">
          <div class="flex justify-around py-2 px-2">
            <router-link to="/" class="flex flex-col items-center gap-1 p-2 text-zinc-400 w-16 transition-colors" active-class="!text-zinc-900 font-semibold">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
              <span class="text-[10px]">首页</span>
            </router-link>
            <router-link to="/ai" class="flex flex-col items-center gap-1 p-2 text-zinc-400 w-16 transition-colors" active-class="!text-zinc-900 font-semibold">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
              <span class="text-[10px]">AI</span>
            </router-link>
            <router-link to="/menu" class="flex flex-col items-center gap-1 p-2 text-zinc-400 w-16 transition-colors" active-class="!text-zinc-900 font-semibold">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>
              <span class="text-[10px]">菜单</span>
            </router-link>
            <router-link to="/history" class="flex flex-col items-center gap-1 p-2 text-zinc-400 w-16 transition-colors" active-class="!text-zinc-900 font-semibold">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              <span class="text-[10px]">历史</span>
            </router-link>
            <router-link to="/profile" class="flex flex-col items-center gap-1 p-2 text-zinc-400 w-16 transition-colors" active-class="!text-zinc-900 font-semibold">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
              <span class="text-[10px]">我的</span>
            </router-link>
          </div>
        </nav>
      </main>
    </div>
  `,
  methods: {
    logout() {
      if (!confirm('确定要退出登录吗？')) return;
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      window.location.href = 'login.html';
    }
  },
  setup() {
    return { store };
  }
};

const app = createApp(AppLayout);
app.use(router);
app.mount('#app');

} // end initApp