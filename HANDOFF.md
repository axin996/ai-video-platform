# GPU 机器零基础启动指南 — AI数字人视频生产SaaS平台

> 本文档从零开始，目标是让一台全新 Windows 机器跑通整个项目。
> 最后的 Claude Code 接手提示在第 9 节。

---

## 1. 项目概述

这是一个 **AI 数字人视频自动生产 SaaS 平台**。用户提交一个视频 URL，系统自动完成：

```
URL输入 → 视频下载 → Whisper文案提取 → DeepSeek文案仿写
→ CosyVoice语音合成 → HeyGem数字人渲染 → FFmpeg字幕+BGM合成 → 多平台发布
```

**技术栈**: FastAPI (Python) + Next.js 14 (TypeScript) + Celery + PostgreSQL + Redis + MinIO

**代码仓库**: `https://github.com/axin996/ai-video-platform.git`

**前端语言**: 全部中文

---

## 2. 当前项目状态

### 已完成
- ✅ FastAPI 后端 + JWT 认证（注册/登录/令牌刷新）
- ✅ SQLAlchemy 2.0 异步 ORM + Alembic 数据库迁移
- ✅ Next.js 14 前端，全部用中文，6 个路由
- ✅ Docker Compose 基础设施定义（PostgreSQL 15、Redis 7、MinIO）
- ✅ Celery GPU Worker 代码（Whisper 预加载、HeyGem 预留）
- ✅ Celery Upload Worker 代码（多平台 Playwright 发布框架）
- ✅ TanStack Query 前端状态管理
- ✅ 所有 UI 组件使用 Tailwind v3 + shadcn 风格，非 v4

### 前端路由
| 路由 | 功能 | 状态 |
|---|---|---|
| `/` | 自动跳转(有token→仪表盘, 无→登录) | ✅ |
| `/login` | 登录页 | ✅ |
| `/register` | 注册页 | ✅ |
| `/dashboard` | 仪表盘（统计卡片+最近任务） | ✅ |
| `/dashboard/tasks` | 任务列表（状态筛选+新建任务弹窗） | ✅ |
| `/dashboard/tasks/[id]` | 任务详情（流水线步骤时间线+发布记录） | ✅ |
| `/dashboard/settings` | 账号设置 | ✅ |

### 后端 API
| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/auth/login` | POST | 登录，返回 access_token + refresh_token |
| `/api/v1/auth/me` | GET | 获取当前用户信息(JWT) |
| `/api/v1/tasks` | GET/POST | 任务列表(分页+状态筛选)/创建新任务 |
| `/api/v1/tasks/{id}` | GET | 任务详情(含所有步骤状态+耗时+发布记录) |
| `/api/v1/tasks/{id}/retry` | POST | 失败任务从断点重试 |

---

## 3. 关键密钥与配置

### 3.1 DeepSeek API Key（用于文案改写）
```
sk-cdd361a60c8f49a3a6e77e80a808646a
```
已写入原机的 `backend/.env`，但 `.env` 没进 git。GPU 机器需要手动创建。

### 3.2 测试账号
| 字段 | 值 |
|---|---|
| 邮箱 | `test@example.com` |
| 密码 | `testpass123` |

### 3.3 MinIO 对象存储
| 字段 | 值 |
|---|---|
| 控制台 | `http://localhost:9001` |
| API | `http://localhost:9000` |
| 用户名 | `minioadmin` |
| 密码 | `minioadmin` |
| Bucket | `ai-video-platform` |

### 3.4 Celery Flower 任务监控
- 地址: `http://localhost:5555`
- 可查看所有 Celery 任务状态和 Worker 情况

---

## 4. 环境安装 — 从零开始（Windows）

> 所有下载在当前中文 Windows 环境下完成，浏览器访问官网即可。

### 4.1 Git
1. 下载: https://git-scm.com/download/win → 点 "64-bit Git for Windows Setup"
2. 安装: 一路 Next 默认就好。关键页:
   - "Default editor" → 建议选 VS Code（或保留 Vim）
   - "Adjusting your PATH" → 选 **"Git from the command line and also from 3rd-party software"**
   - 其余全部默认
3. 验证: 打开 PowerShell，运行 `git --version`，应输出 `git version 2.47.x`

### 4.2 Docker Desktop（PostgreSQL + Redis + MinIO 用）
1. 下载: https://www.docker.com/products/docker-desktop/ → Windows 版
2. 安装: 双击 `Docker Desktop Installer.exe`
   - **关键**: 如果提示 WSL2 未安装，按提示点"Restart"会自动安装 WSL2 内核更新
   - 安装完成后**重启电脑**
3. 启动: 开始菜单找到 Docker Desktop，打开，等鲸鱼图标变白（表示运行中）
   - 如果是第一次，会要求登录 Docker Hub，可以点 "Continue as guest" 跳过
4. 验证: PowerShell 运行 `docker ps`，应显示空列表（表头正常）

### 4.3 Python 3.11
1. 下载: https://www.python.org/downloads/ → 点黄色 "Download Python 3.11.x"
2. 安装:
   - **必须勾选** "Add Python to PATH"（页面最下面的勾选框）
   - 点 "Install Now"
   - 如果提示"Disable path length limit"，点一下它
3. 验证: 新开 PowerShell，运行:
   ```
   python --version
   ```
   应输出 `Python 3.11.x`

### 4.4 Node.js 20（前端用）
1. 下载: https://nodejs.org/zh-cn → 点左侧 "20.x LTS" → 下载 Windows 安装包(.msi)
2. 安装: 一路 Next + Install
3. 验证: 新开 PowerShell，运行:
   ```
   node --version
   npm --version
   ```
   分别显示 `v20.x.x` 和 `10.x.x`

### 4.5 FFmpeg（视频处理用）
1. 下载: https://www.gyan.dev/ffmpeg/builds/ → 点 `ffmpeg-release-essentials.zip`
2. 解压: 把 zip 里的 `ffmpeg-x.x-essentials_build` 文件夹放到 `C:\ffmpeg`
   - 确保路径是这样的: `C:\ffmpeg\bin\ffmpeg.exe`
3. 加入 PATH:
   - 按 Win 键，输入"环境变量"，点"编辑系统环境变量"
   - 对话框右下"环境变量(N)..." → 上面"用户变量"找 `Path` → 双击
   - 右侧"新建" → 输入 `C:\ffmpeg\bin` → 确定
4. 验证: 新开 PowerShell，运行:
   ```
   ffmpeg -version
   ```
   应显示版本信息和编译配置

### 4.6 CUDA（NVIDIA GPU 驱动，GPU Worker 必须）
1. 先确认显卡: PowerShell 运行 `nvidia-smi`
   - 如果显示显卡信息和驱动版本 → 已有 CUDA 驱动，跳到 4.7
   - 如果报错 `nvidia-smi` 不是命令 → 需要安装

2. 安装 NVIDIA 驱动:
   - 下载 GeForce Experience: https://www.nvidia.cn/geforce/geforce-experience/
   - 安装后打开，用微信扫码登录，点"驱动程序"页面 → "检查更新" → 更新到最新

3. 安装 CUDA Toolkit:
   - 下载: https://developer.nvidia.com/cuda-downloads
   - 选 Windows → x86_64 → 12.x → exe(local)
   - 安装: 精简安装(Express)，一路默认
4. 验证: **重启** PowerShell，运行 `nvidia-smi`，应显示 GPU 信息和 CUDA 版本

### 4.7 yt-dlp（视频下载工具）
PowerShell 中:
```
pip install yt-dlp
```
验证: `yt-dlp --version`

---

## 5. 拉取代码和创建配置

### 5.1 克隆代码
```powershell
cd C:\
git clone https://github.com/axin996/ai-video-platform.git
cd ai-video-platform
```

### 5.2 创建 .env 文件
`backend\.env` 不在仓库中（gitignore 排除了），需要手动创建。

在 `C:\workspace\ai-video-platform\backend\` 目录下创建文件 `.env`，内容如下:

```
# ── 数据库 ──────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_video_platform
DATABASE_URL_SYNC=postgresql+psycopg2://postgres:postgres@localhost:5432/ai_video_platform

# ── Redis ───────────────────────────
REDIS_URL=redis://localhost:6379/0

# ── JWT ─────────────────────────────
SECRET_KEY=Lt6_tcwFgv6OG3wgyT6qqkAFqdcjb38tOjApu34HVyw
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# ── MinIO 对象存储 ──────────────────
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=ai-video-platform
MINIO_SECURE=False

# ── DeepSeek API（文案改写）─────────
DEEPSEEK_API_KEY=sk-cdd361a60c8f49a3a6e77e80a808646a
DEEPSEEK_BASE_URL=https://api.deepseek.com

# ── CosyVoice 语音合成 ──────────────
COSYVOICE_BASE_URL=http://localhost:9880

# ── HeyGem 数字人 ───────────────────
HEYGEM_BASE_URL=http://localhost:8081
HEYGEM_MODELS_DIR=C:/workspace/ai-video-platform/models/heygem

# ── Whisper 配置 ────────────────────
WHISPER_MODEL_SIZE=large-v3
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16

# ── CORS ────────────────────────────
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

> 创建方法: 在 backend 文件夹里右键 → 新建 → 文本文档 → 复制上面内容 → 另存为 `.env`（注意: 保存类型选"所有文件"，文件名输入 `.env`）

---

## 6. 启动项目 — 分步操作

以下每一步对应一个 **单独的终端窗口**。建议用 Windows Terminal（Microsoft Store 免费安装），可以开多个标签页。

### 终端 1: 启动 Docker 基础设施
```powershell
cd C:\workspace\ai-video-platform
docker compose up -d
```
等 1-2 分钟。验证:
```powershell
docker ps
```
应该看到 3 个容器的 Status 都是 "Up" 或 "healthy":
- `aivideo-postgres` — PostgreSQL 15
- `aivideo-redis` — Redis 7
- `aivideo-minio` — MinIO 对象存储

### 终端 2: Python 虚拟环境 + 安装后端依赖
```powershell
cd C:\workspace\ai-video-platform
python -m venv venv
.\venv\Scripts\Activate.ps1
```
如果 Activate.ps1 被阻止（ExecutionPolicy 问题），用这个代替:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

安装依赖（可能需要 5-10 分钟，部分包需要编译）:
```powershell
pip install --upgrade pip
pip install -r backend\requirements.txt
```

### 终端 3: 数据库迁移 + 启动 FastAPI
```powershell
cd C:\workspace\ai-video-platform
.\venv\Scripts\Activate.ps1
cd backend
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
看到 `Uvicorn running on http://127.0.0.1:8000` 就是成功了。

**重要: 必须是 `127.0.0.1`，不能用 `0.0.0.0`** — Windows Hyper-V 会占用 0.0.0.0 上的端口。

### 终端 4: 启动 GPU Worker
```powershell
cd C:\workspace\ai-video-platform
.\venv\Scripts\Activate.ps1
cd workers
celery -A gpu_worker.app worker --pool=solo -Q pipeline_queue --concurrency=1 -l info
```
第一次启动时，Worker 会自动从 HuggingFace 下载 Whisper large-v3 模型（~3GB），需要稳定的网络。下载进度会显示在终端中。

**重要: Windows 必须用 `--pool=solo`** — `prefork` 在 Windows 上不可用。

### 终端 5: 启动 Upload Worker
```powershell
cd C:\workspace\ai-video-platform
.\venv\Scripts\Activate.ps1
cd workers
celery -A upload_worker.app worker --pool=solo -Q upload_queue --concurrency=1 -l info
```

### 终端 6: 安装前端依赖并启动
```powershell
cd C:\workspace\ai-video-platform\frontend
npm install
npm run dev
```
看到 `ready started server on http://localhost:3000` 就是成功了。

---

## 7. 验证流程

### 7.1 检查后端
浏览器打开 `http://localhost:8000/health` → 应返回 `{"status":"ok"}`

### 7.2 检查前端
浏览器打开 `http://localhost:3000` → 应自动跳转到登录页（中文界面）

### 7.3 注册并登录
1. 点"注册账号"或直接打开 `http://localhost:3000/register`
2. 填邮箱、用户名、密码 → 点注册
3. 注册成功后自动跳转登录页 → 输入刚才的账号密码
4. 登录成功后进入仪表盘 `http://localhost:3000/dashboard`

### 7.4 测试创建任务
1. 点左侧"任务管理" → 右上角"新建任务"
2. 输入一个视频 URL（比如 `https://www.example.com/video.mp4`）
3. 选目标平台 → 点"创建"
4. 任务创建后，Celery GPU Worker 会自动开始处理（下载 → 提取 → 改写 → ...）
5. 点任务名进入详情页查看流水线进度

### 7.5 检查 Celery Worker
浏览器打开 `http://localhost:5555`（Celery Flower 监控），可以实时看到 Worker 状态和正在执行的任务。

---

## 8. Windows 特有问题的背景说明

以下问题在开发过程中已遇到并解决，如果将来出问题可以优先检查这些:

### 8.1 Celery 必须 `--pool=solo`
Windows 没有 `fork()` 系统调用，所以 Celery 的 `prefork` pool 不可用。所有 Worker 命令必须加上 `--pool=solo`。

### 8.2 FastAPI 不能用 `0.0.0.0:8000`
Windows 上的 Hyper-V（Docker Desktop 依赖的虚拟化）会动态预留 0.0.0.0 范围的端口。FastAPI 必须绑定 `127.0.0.1`。如果遇到 `[Errno 10048]` 错误，就是这个原因。

### 8.3 异步事件循环
Windows 的 `asyncio.get_event_loop()` 在非主线程中会报错。已在 `workers/gpu_worker/tasks/orchestrator.py` 中通过 `_run_async()` 辅助函数修复，内部使用 `asyncio.new_event_loop()` + `asyncio.set_event_loop()`。

### 8.4 bcrypt==4.0.1
bcrypt 5.x 与 passlib 1.7.4 不兼容，登录时会报 `AttributeError`。已在 `requirements.txt` 中固定为 4.0.1。

### 8.5 Tailwind v3
前端所有 UI 组件是用 Tailwind v3（`tailwindcss@3.4.1`）写的，使用 HSL 颜色变量而非 v4 的 oklch()。不要升级 tailwind 到 v4。

### 8.6 SQLAlchemy 异步关系
所有 Task 模型的 relationship 使用 `lazy="selectin"`，避免 `MissingGreenlet` 错误。查询时用 `selectinload()` 预加载关联。

---

## 9. 目录结构

```
C:\workspace\ai-video-platform\
│
├── frontend\                        # Next.js 14 前端 (app router)
│   └── src\
│       ├── app\
│       │   ├── layout.tsx           # 根布局 (Inter 字体)
│       │   ├── page.tsx             # 首页 (自动跳转)
│       │   ├── globals.css          # Tailwind v3 + HSL 变量
│       │   ├── login\page.tsx       # 登录
│       │   ├── register\page.tsx    # 注册
│       │   └── dashboard\
│       │       ├── layout.tsx       # 仪表盘布局 (侧栏 + AuthGate)
│       │       ├── page.tsx         # 总览页 (统计卡片 + 最近任务)
│       │       ├── tasks\
│       │       │   ├── page.tsx     # 任务列表 (筛选 + 新建 + 分页)
│       │       │   └── [id]\page.tsx # 任务详情 (步骤时间线)
│       │       └── settings\page.tsx # 设置页
│       ├── components\
│       │   ├── sidebar.tsx          # 左侧导航
│       │   └── ui\                  # 15个 UI 组件 (Tailwind v3 手工实现)
│       ├── hooks\
│       │   ├── use-auth.tsx         # AuthContext (登录/注册/登出/JWT刷新)
│       │   └── use-tasks.ts         # TanStack Query hooks
│       ├── lib\
│       │   ├── api.ts               # Axios 实例 (JWT 拦截器)
│       │   ├── types.ts             # 所有 TypeScript 类型定义
│       │   └── utils.ts
│       └── providers\
│           └── providers.tsx        # QueryClientProvider + AuthProvider
│
├── backend\
│   ├── app\
│   │   ├── main.py                  # FastAPI 入口
│   │   ├── api\v1\                  # 路由: auth, tasks, assets, platforms, quota, templates, webhooks
│   │   ├── models\__init__.py       # SQLAlchemy 模型: User, Task, TaskStep, TaskAsset, PublishRecord
│   │   ├── schemas\                 # Pydantic 请求/响应 schema
│   │   ├── services\task_service.py # 任务 CRUD + 查询逻辑
│   │   └── core\                    # config.py, database.py, security.py, dependencies.py
│   ├── migrations\                  # Alembic 迁移 (已执行: ddb3dd52864f_initial.py)
│   └── requirements.txt             # Python 依赖 (全部固定版本)
│
├── workers\
│   ├── core\config.py               # Worker 共享配置
│   ├── gpu_worker\
│   │   ├── app.py                   # Celery app (Whisper预加载)
│   │   └── tasks\
│   │       ├── orchestrator.py      # 流水线编排 (链式执行 + 断点重试)
│   │       ├── download.py          # 视频下载 (yt-dlp)
│   │       ├── extract.py           # 文案提取 (Whisper)
│   │       ├── rewrite.py           # 文案改写 (DeepSeek API)
│   │       ├── tts.py               # 语音合成 (CosyVoice API)
│   │       ├── digital_human.py     # 数字人生成 (HeyGem)
│   │       └── composite.py         # 视频合成 (FFmpeg)
│   └── upload_worker\
│       ├── app.py                   # Celery app
│       ├── tasks\publish.py         # 多平台并发发布
│       └── uploaders\               # douyin, xiaohongshu, shipinhao, bilibili, youtube
│
├── services\cosyvoice\              # CosyVoice Flask 服务 (端口 9880)
├── deploy\                          # Docker Compose + K8s 部署文件
├── docker-compose.yml               # 基础设施编排 (postgres, redis, minio, cosyvoice, workers)
└── HANDOFF.md                       # 本文档
```

---

## 10. GPU Worker 任务流水线

每提交一个视频，后台依次执行 7 个 Celery Task:

| 步骤 | Task | 输入 | 输出 | 状态 |
|---|---|---|---|---|
| 1 | `pipeline.download` | 视频 URL | `source_video.mp4` | 代码就绪 |
| 2 | `pipeline.extract` | 视频文件 | 音频 .wav + 原始字幕 .srt | 代码就绪 |
| 3 | `pipeline.rewrite` | 原始文案 JSON | 仿写文案 JSON | 代码就绪 (DeepSeek) |
| 4 | `pipeline.tts` | 仿写文案 + 参考音频 | TTS 语音 .wav | 框架就绪,需要 CosyVoice 服务 |
| 5 | `pipeline.digital_human` | TTS 语音 + 模型 | 数字人原始视频 | 框架就绪,需要 HeyGem |
| 6 | `pipeline.composite` | 视频 + 字幕 + BGM | 最终成品 .mp4 | 代码就绪 |
| 7 | `pipeline.publish` | 成品视频 | 各平台 video_id | 框架就绪,需要 Playwright + 账号 |

### 重试机制
每步独立记录到 `task_steps` 表。如果某步失败，调用 `POST /api/v1/tasks/{id}/retry` 只会从失败步骤开始重新执行，已完成的步骤全部跳过。

### 状态流转
```
pending → downloading → extracting → rewriting → tts_synthesizing
                                                        ↓
completed ← publishing ← compositing ← digital_human ←─┘
    ↑          ↑            ↑             ↑
    └──────────┴────────────┴── failed ←──┘ (任意步骤可进入failed)
```

---

## 11. 多平台发布架构

| 平台 | 发布方式 | Session 有效期 | 优先级 |
|---|---|---|---|
| **B站** | 开放 API (OAuth2) 为主 | ~30天 | ⭐高 (免浏览器) |
| **YouTube** | YouTube Data API v3 (OAuth2) | 长期 | ⭐高 (最稳定) |
| **抖音** | Playwright | ~7天 | 中 |
| **小红书** | Playwright | ~7天 | 中 |
| **视频号** | Playwright (必须有头) | ~3天 | 低 (强检测) |

### 账号模式
- **共享账号池**: 平台统一维护，免费用户排队使用
- **用户独占**: Pro 用户可绑定自己的平台账号（扫码登录后，storage_state 序列化存入 `platform_sessions` 表）

---

## 12. 待完成工作

### 立即需要
- [ ] **CosyVoice 服务部署**: `services/cosyvoice/` 有框架代码，需要安装 CosyVoice 模型和启动 Flask 服务 (端口 9880)
- [ ] **HeyGem 集成**: `digital_human.py` 有框架代码，需要 HeyGem SDK 和模型文件
- [ ] **yt-dlp 安装**: `pip install yt-dlp`，视频下载的第一步依赖
- [ ] **端到端测试**: 提交真实视频 URL，验证流水线各步

### 需要你提供的密钥
- [ ] B站开放平台 OAuth2 Client ID / Secret（用于 API 发布）
- [ ] YouTube Data API v3 OAuth2 Client ID / Secret

### 后续开发
- [ ] 抖音/小红书/视频号 Playwright 自动化（代码框架已有，5个平台文件）
- [ ] 实时进度推送（WebSocket/SSE）
- [ ] 用户配额系统 + VIP 订阅计费
- [ ] Webhook 任务完成通知

---

## 13. 已知问题

1. **`wsl_update.msi` 误提交**: 根目录 160MB 的 WSL 安装包被 commit 了，后续应 `git rm` 清理
2. **Whisper 模型首次下载**: ~3GB，从 HuggingFace 下载。如果网络不好，可以手动下载放在 `~/.cache/huggingface/`
3. **CPU 回退**: 如果 GPU 不可用或 VRAM 不够，Worker 的 Whisper 会自动回退到 CPU（慢很多但能跑）
4. **CosyVoice + HeyGem 未部署**: 流水线第 4、5 步目前只有框架代码，需要实际部署模型服务

---

## 14. 给接手 Claude Code 的指令

当你在这个仓库目录下启动 Claude Code 后，按照以下步骤逐步推进:

### Step 0: 了解项目
- 读本文件（你已经读完了）
- 看看 `git log --oneline` 了解提交记录
- 读 `backend/.env` 确认配置正确

### Step 1: 安装缺失的环境
- 按第 4 节清单，逐个验证: `git --version`、`python --version`、`node --version`、`docker ps`、`ffmpeg -version`、`nvidia-smi`
- 缺失的按对应小节安装

### Step 2: 启动 Docker 基础设施
```powershell
docker compose up -d
docker ps  # 确认 3 个容器都在运行
```

### Step 3: 安装后端依赖
```powershell
cd C:\workspace\ai-video-platform
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### Step 4: 初始化数据库
```powershell
cd backend
alembic upgrade head
```

### Step 5: 启动后端
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 6: 启动前端
```powershell
cd frontend
npm install
npm run dev
```

### Step 7: 尝试验证
- 浏览器打开 `http://localhost:3000`
- 注册一个新账号
- 登录

### Step 8: 启动 GPU Worker
```powershell
cd workers
celery -A gpu_worker.app worker --pool=solo -Q pipeline_queue --concurrency=1 -l info
```
观察 Whisper 模型是否成功加载（终端会打印 `Whisper model 'large-v3' loaded successfully`）

### Step 9: 走向完整流水线
- 安装 yt-dlp: `pip install yt-dlp`
- 部署 CosyVoice 服务
- 集成 HeyGem
- 提交一个测试视频，观察 Celery Flower (`http://localhost:5555`) 的任务执行情况

---

> 任何问题，对照第 8 节的 Windows 常见坑排查。
> 所有命令行在 **PowerShell** 中运行（不要用 cmd）。
