/** 前端应用入口 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router'
import './style.css'
import './styles/markdown.css'
import './styles/party-theme.css'
import App from './App.vue'
import { useAuthStore } from './stores/authStore'
import { initCodeBlockHandlers } from './utils/codeBlockHandlers'

const app = createApp(App)

// 配置 Pinia
const pinia = createPinia()
app.use(pinia)

// 配置 Vue Router
app.use(router)

// 配置 Element Plus
app.use(ElementPlus)

// 初始化认证状态（从存储中恢复Token）
const authStore = useAuthStore()
authStore.restoreAuth()

app.mount('#app')

// 初始化代码块按钮事件处理器
initCodeBlockHandlers()
