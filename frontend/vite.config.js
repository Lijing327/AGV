import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const publicBase = env.VITE_PUBLIC_BASE || '/agv/'
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://127.0.0.1:8000'

  return {
    // 须与实际访问路径一致，如 https://www.yonghongjituan.com:4013/AGV → 常设为 /AGV/
    base: publicBase.endsWith('/') ? publicBase : `${publicBase}/`,
    plugins: [vue()],
    server: {
      port: Number(env.VITE_DEV_PORT) || 3000,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
