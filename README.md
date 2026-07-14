# MatrixV: 全自动短视频生发工作站

MatrixV 是一个基于本地环境构建的全自动化短视频创作流水线系统。通过接入大语言模型 (如 DeepSeek-V3/GPT-4) 与各种智能 Agent 的配合，它可以实现从**捕获全网热点**到**最终产出音画同步带配音及防搬运混淆的短视频**的一站式服务。

## 🌟 核心特性 (Agents)

1. **趋势捕手 (Agent 1)**: 基于 Playwright 绕过反爬机制，抓取各大平台（抖音/小红书等）的热榜，并通过打分机制筛选爆款潜力素材。
2. **文案总编 (Agent 2)**: 接入大语言模型，将干瘪素材洗稿为符合短视频“黄金前三秒”等逻辑的三段式爆款口播文案。内置 Aho-Corasick 多模式匹配算法拦截敏感词，并带有自我打分的重写回路。
3. **视觉导演 (Agent 3)**: 将长文案智能切分为若干分镜，根据语义生成全英文检索词，并在 Pexels 等平台自动拉取相符的高清免版税视频空镜。
4. **声音艺术家 (Agent 4)**: 对接微软高保真 Edge-TTS 免费生成自然人声。同时利用 PyDub 在物理底层混入弱白噪音和微调语速，实现声纹抗搬运，并支持自动混合环境 BGM。
5. **剪辑大师 (Agent 5)**: 使用 FFmpeg 滤镜网络对所有分镜进行强制裁剪对齐，烧录按照字数切分的等比例 SRT 字幕，并混合所有音轨输出最终成品。

## 🏗️ 技术架构

- **后端层**: FastAPI + Celery + SQLAlchemy (PostgreSQL) + Redis (Task Broker)
- **前端层**: React 18 + Vite + Ant Design 5
- **存储层**: 本地对象存储集群 MinIO
- **基础设施**: Docker Compose (一键起停数据库、缓存和对象存储)

## 🚀 快速启动指南

### 1. 环境准备
确保您的本机已安装：
- Docker Desktop (建议启用 WSL2)
- Node.js 20+
- Python 3.11+ (以及 Poetry 依赖管理工具)

### 2. 启动基础设施
进入基础设施目录，启动所有相关的容器服务：
```bash
cd infra
docker-compose up -d
```
启动的服务包括: PostgreSQL(5432), Redis(6379), MinIO(9000, 9001)。

### 3. 后端准备与启动
配置环境变量（或者直接在 `backend/config/settings.py` 修改）：
确保填入有效的 `OPENAI_API_KEY` 和 `PEXELS_API_KEY`（若不填系统将走 Dummy 降级流打桩测试）。
```bash
cd backend
poetry install
poetry run playwright install # 安装所需浏览器内核
```
启动后端 API 服务：
```bash
poetry run uvicorn backend.api.main:app --reload --port 8000
```
启动 Celery Worker 处理剪辑任务：
```bash
poetry run celery -A backend.config.celery_app worker --loglevel=info -P solo
```
*(注意: Windows下建议加上 `-P solo` 避免兼容性问题)*

### 4. 前端启动
```bash
cd frontend
npm install
npm run dev
```
打开浏览器访问 `http://localhost:5173` 即可进入工作站 Dashboard。

## ⚠️ 常见问题
- **MinIO 上传报错**：请确保通过浏览器访问 `http://localhost:9001` 初始化了一个叫 `matrixv-assets` 和 `matrixv-videos` 的 bucket 并且设置为 Public 读权限。
- **任务一直处于 pending**：检查 Redis 容器是否正常运行，以及 Celery Worker 窗口是否有报错日志。

## 📄 License
MIT License
