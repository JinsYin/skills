#!/usr/bin/env node
// 视觉校验。smoke 只查实现：类名是否真的生成样式、渲染报错、横向溢出；diff 与原型成对截全页图并出差异图。
// 用法：node scripts/visual-check.mjs smoke <appUrl> [--only a,b]
//       node scripts/visual-check.mjs diff <protoUrl> <appUrl> [--only a,b]
// smoke 前先构建（查 dist/ 的 CSS）。依赖与产物都在 .visual-check/（需 gitignore），不进 app 的 package.json。
// 目标清单 scripts/visual-targets.mjs：
//   export const widths = [1280, 1440]           // 可选
//   export const scan = ['src']                  // 可选，monorepo 加上组件库的 src
//   export async function setup(page, base, side) {}  // 可选，side 为 'proto' | 'app'，如登录
//   export default [{ name: 'overview', proto: '#overview', app: 'console/overview' }]
//   proto/app 为字符串时按 base 解析；为 async (page, base) => {} 时自行导航、打开浮层或切状态
import { execSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

process.chdir(fileURLToPath(new URL('..', import.meta.url)))
const OUT = '.visual-check'
const [mode, ...args] = process.argv.slice(2)
const at = args.indexOf('--only')
const only = at >= 0 ? args.splice(at, 2)[1].split(',') : null
if (!['smoke', 'diff'].includes(mode) || args.length !== (mode === 'diff' ? 2 : 1)) {
  console.error('用法见文件头'); process.exit(2)
}
mkdirSync(OUT, { recursive: true })

const req = createRequire(resolve(OUT, 'index.js'))
function load(...names) {
  try { return names.map((n) => req(n)) } catch {
    execSync(`npm i --prefix ${OUT} --silent playwright-core pngjs pixelmatch@5`, { stdio: 'inherit' })
    return names.map((n) => req(n))
  }
}

const cfg = await import(pathToFileURL(resolve('scripts/visual-targets.mjs')).href)
const widths = cfg.widths ?? [1280, 1440]
const targets = cfg.default.filter((t) => !only || only.includes(t.name))
const walk = (d) => existsSync(d)
  ? readdirSync(d, { recursive: true }).map((f) => join(d, f)).filter((f) => statSync(f).isFile()) : []

// 截取从 i 开始的引号串或配平的括号段，跳过字符串内的括号
function span(src, i) {
  const open = src[i], close = { '(': ')', '{': '}' }[open]
  if (!close) return src.slice(i, src.indexOf(open, i + 1) + 1)
  for (let j = i, depth = 0, q = null; j < src.length; j++) {
    const ch = src[j]
    if (q) { if (ch === '\\') j++; else if (ch === q) q = null }
    else if ('\'"`'.includes(ch)) q = ch
    else if (ch === open) depth++
    else if (ch === close && --depth === 0) return src.slice(i, j + 1)
  }
  return src.slice(i)
}

// className= 与 cn/cva/clsx 调用里的类名；跳过对象键、cva 默认值与组合条件里的变体名
function classesIn(src) {
  src = src.replace(/defaultVariants\s*:\s*\{[^}]*\}/g, '')
    .replace(/compoundVariants\s*:\s*\[[\s\S]*?\]/g, (m) => m.replace(/\b(?!class(?:Name)?\b)\w+\s*:\s*(['"`])[^'"`]*\1/g, ''))
  const out = new Set()
  const re = /\bclassName=|\b(?:cn|cva|clsx|twMerge)\(/g
  for (let m; (m = re.exec(src));) {
    const region = span(src, m[0].endsWith('(') ? re.lastIndex - 1 : re.lastIndex)
    for (const s of region.matchAll(/(['"`])((?:(?!\1)[^\\]|\\.)*)\1/g)) {
      const end = s.index + s[0].length
      if (/[{,]\s*$/.test(region.slice(0, s.index)) && /^\s*:/.test(region.slice(end))) continue
      for (const c of s[2].replace(/\$\{[^}]*\}/g, '\0').split(/\s+/))
        if (/[-:[]/.test(c) && !c.includes('\0') && !/^(group|peer)(\/|$)/.test(c)) out.add(c)
    }
  }
  return out
}

// 静默失效的类（如超出刻度的 min-w-65）不会报错，只能对照产物 CSS 查
function classCheck() {
  const css = walk('dist').filter((f) => f.endsWith('.css')).map((f) => readFileSync(f, 'utf8')).join('')
  if (!css) return ['dist/ 下没有 CSS，先构建']
  const esc = (c) => c.replace(/[^\w-]/g, (m) => '\\' + m)
  const hit = (c) => css.includes('.' + esc(c)) || (/^\d/.test(c) && [' ', ''].some((s) => css.includes(`.\\3${c[0]}${s}${esc(c.slice(1))}`)))
  const missing = []
  for (const f of (cfg.scan ?? ['src']).flatMap(walk).filter((f) => /\.tsx?$/.test(f) && !/\.(test|spec)\./.test(f)))
    for (const c of classesIn(readFileSync(f, 'utf8'))) if (!hit(c)) missing.push(`类名未生成样式 ${f}: ${c}`)
  return missing
}

const [{ chromium }] = load('playwright-core')
const browser = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch())
async function open(base, step, width, side) {
  const page = await (await browser.newContext({ viewport: { width, height: 900 } })).newPage()
  const errors = []
  page.on('console', (m) => m.type() === 'error' && !m.location().url.endsWith('favicon.ico') && errors.push(m.text()))
  page.on('pageerror', (e) => errors.push(e.message))
  await cfg.setup?.(page, base, side)
  if (typeof step === 'function') await step(page, base)
  else await page.goto(new URL(step, base).href, { waitUntil: 'networkidle' })
  await page.waitForTimeout(cfg.settle ?? 800)
  return { page, errors }
}

const problems = mode === 'smoke' ? classCheck() : []
const rows = []
for (const t of targets) for (const w of widths) {
  if (mode === 'diff' && !t.proto) continue
  const app = await open(args.at(-1), t.app, w, 'app')
  if (mode === 'smoke') {
    const over = await app.page.evaluate(() => [...document.querySelectorAll('*')]
      .filter((el) => el.scrollWidth > el.clientWidth + 1
        && (el === document.documentElement || /auto|scroll/.test(getComputedStyle(el).overflowX)))
      .map((el) => `${el.tagName.toLowerCase()}.${[...el.classList].slice(0, 3).join('.')} +${el.scrollWidth - el.clientWidth}px`))
    problems.push(...app.errors.map((e) => `${t.name}@${w} 控制台报错：${e}`),
      ...over.map((o) => `${t.name}@${w} 横向溢出：${o}`))
  } else {
    const [{ PNG }, pixelmatch] = load('pngjs', 'pixelmatch')
    const proto = await open(args[0], t.proto, w, 'proto')
    const shot = (p) => p.screenshot({ fullPage: true, animations: 'disabled' })
    const [A, B] = [PNG.sync.read(await shot(proto.page)), PNG.sync.read(await shot(app.page))]
    const width = Math.max(A.width, B.width), height = Math.max(A.height, B.height)
    const pad = (p) => { const o = new PNG({ width, height }); o.data.fill(255); PNG.bitblt(p, o, 0, 0, p.width, p.height, 0, 0); return o }
    const diff = new PNG({ width, height })
    const n = pixelmatch(pad(A).data, pad(B).data, diff.data, width, height, { threshold: 0.1 })
    const f = join(OUT, `${t.name}@${w}`)
    writeFileSync(`${f}.proto.png`, PNG.sync.write(A)); writeFileSync(`${f}.app.png`, PNG.sync.write(B))
    writeFileSync(`${f}.diff.png`, PNG.sync.write(diff))
    rows.push([n / (width * height), `| ${t.name} | ${w} | ${A.width}×${A.height} / ${B.width}×${B.height} | ${(n * 100 / (width * height)).toFixed(2)}% | \`${f}.{proto,app,diff}.png\` |`])
    await proto.page.context().close()
  }
  await app.page.context().close()
}
await browser.close()

if (mode === 'diff') {
  const md = ['| 目标 | 宽度 | 尺寸 原型 / 实现 | 差异 | 截图 |', '|---|---|---|---|---|',
    ...rows.sort((a, b) => b[0] - a[0]).map((r) => r[1])].join('\n')
  writeFileSync(join(OUT, 'report.md'), md + '\n'); console.log(md)
} else {
  problems.forEach((p) => console.log('✗ ' + p))
  console.log(problems.length ? `✗ ${problems.length} 项` : '✓ 类名、渲染与溢出检查通过')
  process.exit(problems.length ? 1 : 0)
}
