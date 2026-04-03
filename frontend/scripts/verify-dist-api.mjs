/**
 * 构建后检查：避免把仍指向 :8000 的旧配置打进 dist 却误部署。
 * 若你们合法使用 8000，可临时跳过：npm run build -- --skipVerify（需改 package 脚本）或直接 vite build。
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const assetsDir = path.join(__dirname, '..', 'dist', 'assets')

if (!fs.existsSync(assetsDir)) {
  console.error('verify-dist-api: dist/assets 不存在，请先执行 vite build')
  process.exit(1)
}

const patterns = [
  { re: /yonghongjituan\.com:8000/i, msg: '仍包含 yonghongjituan.com:8000' },
  { re: /:8000\/api/, msg: '仍包含 :8000/api（应使用 .env.production 中的 6715 或同源反代）' },
]

let failed = false
for (const name of fs.readdirSync(assetsDir)) {
  if (!name.endsWith('.js')) continue
  const filePath = path.join(assetsDir, name)
  const s = fs.readFileSync(filePath, 'utf8')
  for (const { re, msg } of patterns) {
    if (re.test(s)) {
      console.error(`verify-dist-api: 失败 ${msg}`)
      console.error(`  文件: ${name}`)
      failed = true
    }
  }
}

if (failed) {
  console.error('\n请确认：1) frontend/.env.production 已保存  2) 在项目根执行 npm run build  3) 上传的是整个 dist 且清理/刷新线上缓存')
  process.exit(1)
}

console.log('verify-dist-api: 通过（dist 内未发现 yonghongjituan.com:8000 / :8000/api）')
