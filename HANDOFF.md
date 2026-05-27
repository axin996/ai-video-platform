# GPU 机器接手文档 — AI数字人视频生产SaaS平台

> 本文档记录截止 2026-05-28 的项目状态，供 GPU 机器上的 Claude Code 或开发者接管使用。

---

## 1. 项目概述

基于 KrLongAI 开源底座构建的多用户 SaaS 平台，核心流水线：

```
URL输入 → 视频下载 → Whisper文案提取 → DeepSeek文案仿写 → CosyVoice语音合成 → HeyGem数字人 → FFmpeg合成 → 多平台发布
```

- **技术栈**: FastAPI + Next.js 14 + Celery + PostgreSQL + Redis + MinIO
- **前端语言**: 中文
- **代码仓库**: `https://github.com/axin996/ai-video-platform.git`

---

## 2. 当前已完成状态

### 基础设施 (Phase 1-3 完成)
- [x] Docker Compose 基础设施（PostgreSQL 15, Redis 7, MinIO）
- [x] FastAPI 后端 + JWT 认证（注册/登录/JWT刷新）
- [x] SQLAlchemy 2.0 异步模型 + Alembic 迁移（已执行一次 `alembic upgrade head`）
- [x] Next.js 14 前端 + 中文界面（仪表盘/任务列表/任务详情/设置/登录/注册）
- [x] Celery GPU Worker + Upload Worker 代码
- [x] Wiper large-v3 模型已开始下载（从 HuggingFace）

### 前端路由（全部中文）
| 路由 | 页面 | 状态 |
|---|---|---|
| `/` | 自动跳转（有 token → 仪表盘，无 → 登录）| ✅ |
| `/login` | 登录页 | ✅ |
| `/register` | 注册页 | ✅ |
| `/dashboard` | 仪表盘总览（统计卡片 + 最近任务）| ✅ |
| `/dashboard/tasks` | 任务列表（状态筛选 + 新建任务弹窗）| ✅ |
| `/dashboard/tasks/[id]` | 任务详情（流水线步骤时间线 + 发布记录）| ✅ |
| `/dashboard/settings` | 设置页（用户信息 + API地址）| ✅ |

### 后端 API（全部已测试通过）
| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/v1/auth/register` | POST | 注册 |
| `/api/v1/auth/login` | POST | 登录（返回 access_token + refresh_token）|
| `/api/v1/auth/me` | GET | 当前用户信息 |
| `/api/v1/tasks` | GET/POST | 任务列表/创建任务 |
| `/api/v1/tasks/{id}` | GET | 任务详情（含步骤+发布记录）|
| `/api/v1/tasks/{id}/retry` | POST | 重试失败任务 |

---

## 3. 关键配置与密钥

### DeepSeek API Key
```
sk-cdd361a60c8f49a3a6e77e80a808646a
```
已写入 `backend/.env`，但 `.env` 已加入 `.gitignore`，GPU 机器需手动创建。

### backend/.env 完整内容（需要在 GPU 机器重建）
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_video_platform
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/ai_video_platform
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=Lt6_tcwFgv6OG3wgyT6qqkAFqdcjb38tOjApu34HVyw
DEEPSEEK_API_KEY=sk-cdd361a60c8f49a3a6e77e80a808646a
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=ai-video-platform
CORS_ORIGINS=http://localhost:3000
```

### 测试账号
| 字段 | 值 |
|---|---|
| 邮箱 | test@example.com |
| 密码 | testpass123 |

---

## 4. Windows 系统关键注意事项

以下问题在 Windows 开发机上都遇到过，GPU 机器如也是 Windows，必须按此处理：

### 4.1 Celery 必须用 `--pool=solo`
Windows 不支持 `prefork`，所有 Worker 启动命令必须加 `--pool=solo`

### 4.2 FastAPI 不能用 `0.0.0.0:8000`
Windows Hyper-V 会占用 `0.0.0.0` 段端口。FastAPI 必须用 `127.0.0.1:8000`：
```
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4.3 Celery Worker 异步事件循环
Windows 的 `asyncio.get_event_loop()` 会报错，已在 `workers/gpu_worker/tasks/orchestrator.py` 中修复：
```python
def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
```

### 4.4 bcrypt 版本
必须使用 `bcrypt==4.0.1`，5.x 与 passlib 不兼容。已在 `requirements.txt` 中固定。

---

## 5. GPU 机器启动步骤

### 前提条件
- [ ] Git 已安装
- [ ] Python 3.11+ 已安装
- [ ] Node.js 20+ 已安装
- [ ] Docker Desktop 已安装并运行
- [ ] CUDA ≥ 11.8 + cuDNN 已安装（`nvidia-smi` 确认）
- [ ] FFmpeg 已安装并加入 PATH

### 启动步骤

```bash
# 1. 克隆代码
git clone https://github.com/axin996/ai-video-platform.git
cd ai-video-platform

# 2. 创建 backend/.env（内容见第3节）
cp backend/.env.example backend/.env
# 然后用编辑器填入第3节的完整内容

# 3. 启动基础设施 (Docker)
docker compose up -d

# 4. 创建 Python 虚拟环境
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# 或 bash:
source venv/Scripts/activate

# 5. 安装后端依赖
pip install -r backend/requirements.txt

# 6. 运行数据库迁移
cd backend
alembic upgrade head
cd ..

# 7. 启动 FastAPI 后端 (终端1)
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 8. 启动 Celery GPU Worker (终端2)
cd workers
celery -A gpu_worker.app worker --pool=solo -Q pipeline_queue --concurrency=1 -l info

# 9. 启动 Celery Upload Worker (终端3)
cd workers
celery -A upload_worker.app worker --pool=solo -Q upload_queue --concurrency=1 -l info

# 10. 安装前端依赖并启动 (终端4)
cd frontend
npm install
npm run dev
```

### 前端访问
- 浏览器打开 `http://localhost:3000`
- 使用测试账号 test@example.com / testpass123 登录

---

## 6. 待完成工作

### 高优先级
- [ ] **GPU Worker 模型下载**: Whisper (large-v3, ~3GB), HeyGem 模型权重
- [ ] **CosyVoice 服务部署**: 端口 9880，独立 Flask 进程
- [ ] **yt-dlp + FFmpeg 安装**: 视频下载和处理的底层工具
- [ ] **端到端流水线测试**: 提交一个真实视频URL，跑通6步

### 待提供的密钥
- [ ] B站开放平台 OAuth2 Client ID / Secret
- [ ] YouTube Data API v3 OAuth2 Client ID / Secret

### 未开发功能
- [ ] 抖音/小红书/视频号 Playwright 自动化发布（代码框架已有）
- [ ] 实时进度推送（WebSocket/SSE）
- [ ] 用户配额系统
- [ ] VIP 订阅计费
- [ ] Webhook 通知

---

## 7. 目录结构速查

```
ai-video-platform/
├── frontend/src/           # Next.js 前端
│   ├── app/                # App Router 页面
│   ├── components/         # UI 组件
│   ├── hooks/              # useAuth, useTasks
│   ├── lib/                # api.ts, types.ts
│   └── providers/          # Auth + QueryClient providers
├── backend/                # FastAPI
│   ├── app/api/v1/         # REST 端点
│   ├── app/models/         # SQLAlchemy 模型
│   ├── app/schemas/        # Pydantic 请求/响应
│   ├── app/services/       # 业务逻辑
│   ├── app/core/           # 配置/数据库/安全
│   └── migrations/         # Alembic
├── workers/
│   ├── gpu_worker/tasks/   # Whisper/HeyGem/FFmpeg/DeepSeek 任务
│   ├── upload_worker/tasks/ # 多平台发布任务
│   └── upload_worker/uploaders/ # 各平台 Playwright 脚本
├── services/cosyvoice/     # CosyVoice Flask 服务
├── deploy/                 # Docker Compose + K8s
└── docker-compose.yml      # 基础设施编排
```

---

## 8. 已知问题

1. **`wsl_update.msi` 误提交**: 根目录下的 `wsl_update.msi` 是 Windows WSL 安装包，不应在仓库中。后续可 `git rm` 清理。
2. **Whisper 模型首次下载**: 首次启动 GPU Worker 会自动从 HuggingFace 下载 large-v3 (~3GB)，需要稳定的网络。
3. **CosyVoice 未部署**: `services/cosyvoice/api.py` 有框架代码，但需要实际部署 CosyVoice 模型和 Flask 服务。
4. **HeyGem 未集成**: GPU Worker 中有 `digital_human.py` 任务，但需要 HeyGem SDK 和模型文件。

---

## 9. 给接手 Claude Code 的提示

参阅此文档后：
1. 先运行 `git log --oneline -5` 了解提交历史
2. 读取 `backend/.env` 确认配置正确
3. 确认 Docker 容器运行: `docker ps`
4. 检查 GPU 可用: `nvidia-smi`
5. 从第5节"启动步骤"开始，根据 GPU 机器实际环境调整命令
