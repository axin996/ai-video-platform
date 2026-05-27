# AI Video Platform — AI数字人视频生产SaaS平台

基于 KrLongAI 开源底座，提供视频链接输入 → AI 文案仿写 → 声音克隆 → 数字人渲染 → 多平台发布的全自动流水线。

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | Next.js 14 + React + shadcn/ui + Tailwind |
| 后端 | FastAPI (Python 3.12) + SQLAlchemy + Alembic |
| 任务队列 | Celery + Redis |
| 数据库 | PostgreSQL 15 |
| 对象存储 | MinIO (S3 兼容) |
| ASR 语音识别 | OpenAI Whisper (faster-whisper) |
| 文案改写 | DeepSeek API |
| 语音合成 | CosyVoice (port 9880) |
| 数字人 | HeyGem |
| 视频处理 | FFmpeg |
| 浏览器自动化 | Playwright + Chrome |
| 部署 | Docker Compose / Kubernetes |

## 流水线

```
视频链接 → [1.Download] → [2.Whisper提取文案] → [3.DeepSeek仿写]
                                                       ↓
         [7.多平台发布] ← [6.FFmpeg合成] ← [5.HeyGem数字人] ← [4.CosyVoice配音]
```

## 目录结构

```
ai-video-platform/
├── frontend/                     # Next.js 前端
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/               # REST API 路由
│   │   ├── core/                 # 配置/数据库/安全
│   │   ├── models/               # SQLAlchemy ORM (11 张表)
│   │   ├── schemas/              # Pydantic 校验
│   │   └── services/             # 业务逻辑层
│   ├── migrations/               # Alembic 迁移
│   └── requirements.txt
├── workers/
│   ├── gpu_worker/               # GPU Worker (Whisper+HeyGem+CosyVoice)
│   │   └── tasks/                # 7 个 Celery Task
│   ├── upload_worker/            # 发布 Worker (Playwright)
│   │   └── uploaders/            # 5 个平台上传器
│   └── housekeeping/             # 定时清理
├── services/cosyvoice/           # CosyVoice 独立服务
├── deploy/
│   ├── docker-compose/           # Dockerfiles
│   └── k8s/                      # K8s manifests
└── docker-compose.yml            # 一键启动
```

## 前置依赖

在启动项目前，需要先安装以下软件：

### 必须安装

| 软件 | 最低版本 | 用途 | 安装方式 |
|---|---|---|---|
| **Docker Desktop** | 24.0+ | 容器编排 | `winget install Docker.DockerDesktop` |
| **Python** | 3.12 | 后端运行 | `winget install Python.Python.3.12` |
| **Node.js** | 20.x (已安装 ✓) | 前端构建 | `winget install OpenJS.NodeJS.LTS` |

### 可选安装（本地开发用，Docker 容器内已自带）

| 软件 | 用途 | Docker 替代 |
|---|---|---|
| FFmpeg | 视频处理 | `docker.io` 内建 |
| PostgreSQL 15 | 数据库 | Docker service `postgres` |
| Redis 7 | 消息队列/缓存 | Docker service `redis` |
| MinIO | 对象存储 | Docker service `minio` |

### Docker 安装后验证

```bash
docker --version
docker compose version
```

## 快速开始

### 1. 克隆仓库

```bash
cd ai-video-platform
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY 等必要配置
```

### 3. 启动基础设施

```bash
docker compose up -d postgres redis minio
```

### 4. 初始化数据库

```bash
# 创建 Python 虚拟环境
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r backend/requirements.txt

# 执行数据库迁移
cd backend
alembic upgrade head
```

### 5. 启动后端

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文档: http://localhost:8000/docs

### 6. 启动 Celery Worker

```bash
# GPU Worker (需要 NVIDIA GPU)
celery -A workers.gpu_worker.app worker --loglevel=info -Q pipeline_queue --concurrency=1

# Upload Worker
celery -A workers.upload_worker.app worker --loglevel=info -Q upload_queue --concurrency=2
```

### 7. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端: http://localhost:3000

## 环境变量说明

| 变量 | 说明 | 默认值 |
|---|---|---|
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://postgres:postgres@localhost:5432/ai_video_platform` |
| `REDIS_URL` | Redis 连接串 | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT 签名密钥 | **生产环境务必更换** |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 无，需自行申请 |
| `MINIO_ENDPOINT` | MinIO S3 地址 | `localhost:9000` |
| `COSYVOICE_BASE_URL` | CosyVoice 服务地址 | `http://localhost:9880` |
| `HEYGEM_BASE_URL` | HeyGem 服务地址 | `http://localhost:8081` |
| `BILIBILI_CLIENT_ID` | B站开放平台 ID | 无 |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth2 ID | 无 |

## API 概览

| 端点 | 说明 |
|---|---|
| `POST /api/v1/auth/register` | 用户注册 |
| `POST /api/v1/auth/login` | 登录 -> JWT |
| `GET  /api/v1/auth/me` | 当前用户信息 |
| `POST /api/v1/tasks` | 创建视频生产任务 |
| `GET  /api/v1/tasks` | 任务列表（分页） |
| `GET  /api/v1/tasks/{id}` | 任务详情（含步骤状态） |
| `POST /api/v1/tasks/{id}/retry` | 失败重试 |
| `DELETE /api/v1/tasks/{id}` | 取消任务 |
| `GET  /api/v1/tasks/{id}/steps` | 查看各步骤 |
| `GET  /api/v1/tasks/{id}/assets` | 查看产物文件 |
| `GET  /api/v1/templates` | 预设模板 |
| `GET  /api/v1/quota` | 配额使用情况 |

## GPU 节点部署

GPU Worker 负责 Whisper、CosyVoice、HeyGem 三个 GPU 密集型步骤。
建议配置：NVIDIA A10 (24GB VRAM) 或以上。

```bash
# 单独启动 GPU 相关服务
docker compose -f docker-compose.yml -f deploy/docker-compose/docker-compose.gpu.yml up -d celery-gpu-worker cosyvoice
```

### GPU 显存规划 (24GB A10)

| 组件 | 显存占用 |
|---|---|
| faster-whisper (large-v3) | ~3 GB |
| HeyGem (Wav2Lip + SCRFD) | ~7 GB |
| CosyVoice (独立进程) | ~5 GB |
| 系统预留 | ~9 GB |

## 多平台发布

| 平台 | 方式 | 备注 |
|---|---|---|
| B站 | 开放平台 OAuth2 | 推荐，最稳定，~30天有效 |
| YouTube | YouTube Data API v3 OAuth2 | 推荐，长期有效 |
| 抖音 | Playwright + stealth.js | ~7天 session，需真实 Chrome |
| 小红书 | Playwright | ~7天 session，≥30s 间隔 |
| 视频号 | Playwright 有头模式 | ~3天 session，强反爬检测 |

## License

MIT
