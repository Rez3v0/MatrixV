# MatrixV 详细开发计划

基于 [instruction.md](instruction.md) 的完整设计文档，以下是从零到一的项目开发计划。

---

## 一、项目总览与技术选型

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| **前端** | React 18 + TypeScript + Ant Design / shadcn-ui | 视频预览看板、任务管理面板、素材库 |
| **API 网关** | FastAPI (Python 3.11+) + WebSocket | 异步支持好，与 ML 生态无缝对接 |
| **任务队列** | Celery + Redis (Broker) + PostgreSQL (Backend) | 异步视频渲染、重试与状态追踪 |
| **多 Agent 编排** | LangGraph + LangChain | 有向无环图(DAG)编排 6 个 Agent 的协同 |
| **LLM** | DeepSeek-V3 / GPT-4o (可插拔) | 文案改写、Prompt 生成、策略判定 |
| **数据采集** | Scrapy + Playwright | 反反爬，模拟真实浏览器指纹 |
| **音频处理** | Edge-TTS / 火山引擎 TTS + Librosa + Pydub | TTS 合成 + 声学指纹对抗 |
| **视频渲染** | FFmpeg (GPU NVENC) + MoviePy | 硬解码加速，批量流水线渲染 |
| **存储** | MinIO / 阿里云 OSS | 原始素材 + 成品视频 + 中间资产 |
| **容器化** | Docker Compose (开发) / K8s (生产) | 各服务独立部署，GPU 节点亲和 |

---

## 二、项目目录结构

```
MatrixV/
├── backend/
│   ├── api/                    # FastAPI 网关
│   │   ├── routes/             # tasks, projects, assets, stats
│   │   ├── middleware/         # auth, rate_limit, cors
│   │   └── websocket/          # 实时推送渲染进度
│   ├── agents/                 # 6 大 Agent 实现
│   │   ├── trend_catcher/      # Agent 1: 趋势捕手
│   │   ├── script_editor/      # Agent 2: 文案总编
│   │   ├── visual_director/    # Agent 3: 视觉导演
│   │   ├── audio_artist/       # Agent 4: 声音艺术家
│   │   ├── editor_pro/         # Agent 5: 混剪大师
│   │   └── ops_planner/        # Agent 6: 闭环运营
│   ├── orchestration/          # LangGraph DAG 编排
│   ├── scraper/                # Scrapy + Playwright 爬虫
│   ├── tts/                    # TTS 服务封装
│   ├── video_engine/           # FFmpeg + MoviePy 渲染核心
│   │   ├── anti_detect/        # 像素去重、非标帧率、噪声层
│   │   └── templates/          # 字幕/特效模板引擎
│   ├── models/                 # ORM 模型 (SQLAlchemy)
│   ├── tasks/                  # Celery 任务定义
│   └── config/                 # 配置管理
├── frontend/                   # React Web UI
│   ├── src/
│   │   ├── pages/              # Dashboard, ProjectEditor, TaskList
│   │   ├── components/         # VideoPreview, AgentPipeline, AssetPicker
│   │   └── hooks/              # useWebSocket, useTaskStatus
├── infra/                      # 运维配置
│   ├── docker-compose.yml
│   ├── Dockerfile.*
│   └── k8s/
├── tests/                      # 测试
└── docs/                       # 文档
```

---

## 三、六阶段开发路线图

### 🔵 Phase 1：基础设施搭建（第 1-4 周）

**目标：** 跑通"API → Celery → FFmpeg → 输出"的最小闭环。

| 任务 | 详情 | 优先级 |
|------|------|--------|
| 1.1 项目脚手架 | FastAPI 项目结构、Docker Compose 开发环境、Poetry 依赖管理 | P0 |
| 1.2 数据库设计 | User、Project、VideoTask、Asset、AgentLog 等核心表 | P0 |
| 1.3 Celery 任务队列 | Redis Broker + PostgreSQL Result Backend，任务状态机：pending → scraping → writing → rendering → done/failed | P0 |
| 1.4 FFmpeg 渲染核心 | Python 封装 FFmpeg 命令行，支持 GPU NVENC 硬编码，基础的字幕叠加 + BGM 混音 | P0 |
| 1.5 MinIO 存储集成 | 素材上传/下载 SDK 封装，预签名 URL 生成 | P1 |
| 1.6 前端骨架 | React 项目初始化，Dashboard + TaskList 基础页面，WebSocket 实时状态推送 | P0 |

**交付物：** 一段手工编排的视频能被 API 触发 → Celery 渲染 → 输出到 MinIO → 前端预览。

---

### 🟢 Phase 2：Agent 单点突破（第 5-8 周）

**目标：** 逐个实现 6 个 Agent 的核心能力，每个 Agent 独立可测。

#### Agent 1 — 趋势捕手

| 任务 | 详情 |
|------|------|
| 2.1.1 Playwright 浏览器池 | 管理多实例、自动轮换 User-Agent、Canvas 指纹、Cookie 隔离 |
| 2.1.2 知乎/小红书爬虫 | 解析热榜 API/页面，反反爬策略（随机延迟、鼠标轨迹模拟） |
| 2.1.3 抖音/百度热搜 | 移动端 UA 模拟 + 签名破解 |
| 2.1.4 黑马选题过滤器 | 量化评分算法：评论/点赞比 > 10%，低粉高播放检测 |

#### Agent 2 — 文案总编

| 任务 | 详情 |
|------|------|
| 2.2.1 LLM Pipeline 抽象层 | 支持 DeepSeek / GPT-4o 可插拔，统一接口 |
| 2.2.2 敏感词过滤引擎 | Aho-Corasick 多模式匹配 + 黑名单词库 + LLM 二次审核 |
| 2.2.3 三段式文案生成 Prompt | 黄金前3秒(冲突) → 密集输出(每2s一切换) → 结尾留钩子 |
| 2.2.4 文案评分与改写回路 | 基于可读性、情绪曲线、完播率预测的自动迭代优化 |

#### Agent 3 — 视觉导演

| 任务 | 详情 |
|------|------|
| 2.3.1 文案→镜头切分 | NLP 分句 + 语义段落检测，每段 2-3 秒 |
| 2.3.2 空镜检索关键词生成 | LLM 为每个镜头生成 Pexels/Pixabay 英文检索词 |
| 2.3.3 AI 生图 Prompt 生成 | 为 Midjourney / SD / DALL-E 生成分镜级 Prompt |
| 2.3.4 素材版权库对接 | Pexels、Pixabay API 集成，自动下载 + 版权标记 |

#### Agent 4 — 声音艺术家

| 任务 | 详情 |
|------|------|
| 2.4.1 TTS 多引擎集成 | Edge-TTS (免费) + 火山引擎 TTS (商业级)，统一适配器 |
| 2.4.2 声学指纹对抗 | 音调随机 ±0.5%、-40dB 白噪音叠加、混响变调 |
| 2.4.3 BGM 智能匹配 | 按情绪分类的 BGM 库 + 自动音量包络 |

#### Agent 5 — 混剪大师

| 任务 | 详情 |
|------|------|
| 2.5.1 视听轨道自动对齐 | 配音时长驱动画面时长，动态变速适配 |
| 2.5.2 动态大字报字幕 | SRT → ASS 字幕渲染，字体/颜色/位置随机组合 |
| 2.5.3 像素去重策略 | 29.97fps 非标帧率、1% 透明噪声迭加层、每3秒 1-3% 缩放抖动 |

#### Agent 6 — 闭环运营

| 任务 | 详情 |
|------|------|
| 2.6.1 多平台分发 | 抖音/快手/视频号发布 API 对接 (Playwright 模拟) |
| 2.6.2 数据回传采集 | 24h 后自动抓取播放量/完播率/互动数据 |
| 2.6.3 反哺闭环 | 数据写入选题质量模型，优化 Agent 1 的选题权重 |

---

### 🟡 Phase 3：多 Agent 编排与流水线（第 9-12 周）

**目标：** LangGraph 串联 6 个 Agent，实现"一键全自动生成"。

| 任务 | 详情 | 优先级 |
|------|------|--------|
| 3.1 LangGraph DAG 定义 | 6 节点有向图，条件分支（全自动 / 人机协同），状态持久化 | P0 |
| 3.2 Agent 间数据契约 | 标准化 Agent 输入输出 Schema (Pydantic)，确保松耦合 | P0 |
| 3.3 人机协同中断点 | DAG 中插入 Human-in-the-loop 节点，暂停等待人工确认后继续 | P0 |
| 3.4 流水线监控看板 | 实时展示每个 Agent 的状态、耗时、LLM Token 消耗 | P1 |
| 3.5 错误恢复与重试 | Agent 级失败重试策略、降级方案（如 TTS 不可用时切换引擎） | P1 |
| 3.6 多任务并发调度 | 同一 GPU 节点多视频并行渲染的资源调度策略 | P1 |

---

### 🟠 Phase 4：防限流引擎深度打磨（第 13-15 周）

**目标：** 将 instruction 中所有防封策略系统化落地为可配置的渲染参数。

| 任务 | 详情 |
|------|------|
| 4.1 模板随机化引擎 | 字幕 5 参数（字体/粗细/位置浮动3-5%/颜色/边框）随机组合器 |
| 4.2 非标帧率渲染管线 | 强制 29.97fps / 59.94fps，FFmpeg 参数固化 |
| 4.3 动态噪声层 | 透明度 1% 的 Perlin 噪声生成，每帧随机变化 |
| 4.4 画面微抖动 | 每 3 秒随机缩放 1-3%，关键帧插值平滑 |
| 4.5 音频指纹对抗管线 | TTS → 变调 → 白噪音混入 → BGM 叠加，全流程自动化 |
| 4.6 AI 标签自动声明 | 分发接口自动勾选"由AI生成"标签 |
| 4.7 去重效果 A/B 测试框架 | 同内容用不同去重策略渲染多版本，对比过审率 |

---

### 🔴 Phase 5：矩阵化运营平台（第 16-19 周）

**目标：** 支持多账号矩阵管理、养号自动化、发布调度。

| 任务 | 详情 |
|------|------|
| 5.1 账号管理面板 | 多平台账号绑定、状态监控（正常/限流/封禁）、Cookie 管理 |
| 5.2 IP 隔离代理池 | 一机一卡一IP，静态住宅 IP 代理池管理，自动分配 |
| 5.3 养号自动化脚本 | 3-5 天养号期：模拟刷视频（停留≥15s）、随机点赞、评论浏览 |
| 5.4 阶梯式发布调度器 | 新号 1-2 条/天，老号≤5 条/天，间隔≥2h，定时队列 |
| 5.5 选题黑名单管理 | 敏感词库维护，红线选题自动熔断 |
| 5.6 矩阵数据大盘 | 跨账号播放量/粉丝增长/过审率聚合分析 |

---

### 🟣 Phase 6：生产化与迭代（第 20-24 周+）

**目标：** 性能优化、成本控制、持续迭代。

| 任务 | 详情 |
|------|------|
| 6.1 GPU 渲染集群优化 | K8s GPU 节点亲和调度，渲染任务排队与优先级 |
| 6.2 LLM 成本控制 | Prompt 缓存、本地模型推理 (vLLM) 降本方案 |
| 6.3 端到端测试 | 全流程集成测试，覆盖 6 Agent 串联 + 渲染 + 分发 |
| 6.4 监控告警 | Prometheus + Grafana，渲染失败/API 限流/账号异常告警 |
| 6.5 CI/CD | GitHub Actions 自动化测试 → Docker 镜像构建 → 部署 |
| 6.6 运营数据分析 | 基于回传数据的选题质量模型持续训练与优化 |

---

## 四、数据库核心模型设计

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│    User      │────→│     Project      │────→│     VideoTask       │
├──────────────┤     ├──────────────────┤     ├─────────────────────┤
│ id           │     │ id               │     │ id                  │
│ username     │     │ user_id (FK)     │     │ project_id (FK)     │
│ role         │     │ name             │     │ status (状态机)      │
│ created_at   │     │ mode (auto/manual)│    │ source_topic_id (FK) │
└──────────────┘     │ platform_target  │     │ script_text         │
                     └──────────────────┘     │ video_url (output)   │
                                              │ anti_detect_config  │
┌──────────────────┐     ┌──────────────────┐ │ publish_status      │
│   SourceTopic    │     │   PublishRecord  │ │ created_at          │
├──────────────────┤     ├──────────────────┤ └─────────────────────┘
│ id               │     │ id               │
│ source_url       │     │ task_id (FK)     │     ┌──────────────────┐
│ platform         │     │ account_id (FK)  │     │ PlatformAccount   │
│ title            │     │ platform         │     ├──────────────────┤
│ hot_score        │     │ publish_url      │     │ id               │
│ raw_content      │     │ views_24h        │     │ user_id (FK)     │
│ fetched_at       │     │ completion_rate  │     │ platform         │
│ status           │     │ likes/comments   │     │ cookies/ token   │
└──────────────────┘     │ published_at     │     │ proxy_ip         │
                         └──────────────────┘     │ health_status    │
                                                  └──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│     Asset        │     │    AgentLog      │
├──────────────────┤     ├──────────────────┤
│ id               │     │ id               │
│ task_id (FK)     │     │ task_id (FK)     │
│ type (video/audio│     │ agent_name       │
│       /image)    │     │ input_data (JSON)│
│ storage_url      │     │ output_data (JSON)│
│ duration         │     │ llm_tokens       │
│ metadata (JSON)  │     │ duration_ms      │
└──────────────────┘     │ error_message    │
                         └──────────────────┘
```

---

## 五、VideoTask 状态机

```
                    ┌──────────┐
                    │  pending │  初始状态，等待调度
                    └────┬─────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   scraping    │  Agent 1: 采集热点数据
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   writing     │  Agent 2: 文案生成 + 敏感词过滤
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
      ┌──────────────┐      ┌──────────────────┐
      │   reviewing  │      │  visual_matching │  Agent 3: 镜头匹配
      │ (人机协同模式) │      └────────┬─────────┘
      └──────┬───────┘               │
             │                       ▼
             │              ┌──────────────────┐
             │              │  audio_gen       │  Agent 4: TTS + 声学对抗
             │              └────────┬─────────┘
             │                       │
             └───────────┬───────────┘
                         ▼
                 ┌───────────────┐
                 │  rendering    │  Agent 5: FFmpeg 混剪渲染
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  publishing   │  Agent 6: 分发 + 数据回传
                 └───────┬───────┘
                         │
                    ┌────┴─────┐
                    ▼          ▼
              ┌────────┐  ┌────────┐
              │  done  │  │ failed │
              └────────┘  └────────┘
```

---

## 六、建议切入策略

根据 instruction 最后的落地建议，**强烈推荐"人机协同半自动"路线先行**：

| 阶段 | 时间 | 范围 | 交付物 |
|------|------|------|--------|
| **MVP-1** | 第 1-4 周 | Phase 1：基础设施 | FFmpeg 渲染闭环 + 前端看板 |
| **MVP-2** | 第 5-8 周 | Agent 2(文案) + Agent 3(视觉) + Agent 5(混剪) | 文案→粗剪→人工精调 半自动 MVP |
| **MVP-3** | 第 9-12 周 | Agent 1(趋势) + Agent 4(声音) + Phase 3 编排 | 全自动链路打通 |
| **V1.0** | 第 13-15 周 | Phase 4：防限流引擎 | 过审率优化版本 |
| **V2.0** | 第 16-19 周 | Phase 5：矩阵运营 | 多账号矩阵管理平台 |
| **V3.0** | 第 20-24 周+ | Phase 6：生产化 | 性能优化、监控、CI/CD |

每一步都有可交付、可验证的产出，在早期就能拿到真实的平台流量反馈来指导后续的防限流参数调优。

---

## 七、风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|---------|
| 平台反爬升级 | 数据采集失效 | Playwright 定期更新指纹库，多源降级 |
| LLM API 成本过高 | 运营成本不可控 | DeepSeek 为主力模型，Prompt 缓存，探索本地 vLLM |
| 平台风控升级 | 过审率下降 | 去重参数持续 A/B 测试，社区情报共享 |
| GPU 资源瓶颈 | 渲染排队严重 | 云 GPU 弹性扩缩容，非高峰期预渲染 |
| 版权合规风险 | 下架/法律纠纷 | Pexels/Pixabay 版权库优先，AI 生图自主版权 |
