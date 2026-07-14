# MatrixV: Fully Automated Short Video Generation Workstation

MatrixV is a fully automated short video creation pipeline system built for the local environment. By integrating Large Language Models (like DeepSeek-V3/GPT-4) with various intelligent Agents, it enables a one-stop service from **capturing internet trends** to **producing final audio-video synchronized short videos** equipped with voiceovers and anti-plagiarism obfuscation.

## 🌟 Core Features (Agents)

1. **Trend Catcher (Agent 1)**: Utilizes Playwright to bypass anti-scraping mechanisms, grabbing trending topics from major platforms (TikTok/Douyin, Xiaohongshu, etc.), and screening potential viral content via a scoring mechanism.
2. **Script Editor (Agent 2)**: Connects to Large Language Models to rewrite dry materials into a three-part viral spoken script that aligns with the "Golden First 3 Seconds" logic of short videos. Features a built-in Aho-Corasick multi-pattern matching algorithm to block sensitive words, and includes a self-scoring rewrite loop.
3. **Visual Director (Agent 3)**: Intelligently splits the long script into several shots, generates English search keywords based on semantics, and automatically fetches matching high-definition royalty-free b-roll videos from platforms like Pexels.
4. **Audio Artist (Agent 4)**: Connects with Microsoft's high-fidelity Edge-TTS to generate natural human voices for free. Meanwhile, it uses PyDub to inject subtle white noise and fine-tune speech speed at the physical layer, achieving acoustic anti-plagiarism protection, and supports auto-mixing with environmental BGM.
5. **Video Editor (Agent 5)**: Uses FFmpeg filter networks to forcefully crop and align all shots, burns in proportionally split SRT subtitles, and multiplexes all audio tracks to output the final product.

## 🏗️ Technology Architecture

- **Backend Layer**: FastAPI + Celery + SQLAlchemy (PostgreSQL) + Redis (Task Broker)
- **Frontend Layer**: React 18 + Vite + Ant Design 5
- **Storage Layer**: Local Object Storage Cluster (MinIO)
- **Infrastructure**: Docker Compose (One-click start/stop for database, cache, and object storage)

## 🚀 Quick Start Guide

### 1. Environment Preparation
Ensure your local machine has the following installed:
- Docker Desktop (WSL2 recommended)
- Node.js 20+
- Python 3.11+ (and Poetry for dependency management)

### 2. Start Infrastructure
Navigate to the infrastructure directory and start all related container services:
```bash
cd infra
docker-compose up -d
```
The started services include: PostgreSQL (5432), Redis (6379), MinIO (9000, 9001).

### 3. Backend Setup & Start
Configure environment variables (or directly modify `backend/config/settings.py`):
Ensure you provide valid `OPENAI_API_KEY` and `PEXELS_API_KEY` (if left blank, the system will fallback to a Dummy mock flow for testing).
```bash
cd backend
poetry install
poetry run playwright install # Install required browser binaries
```
Start the backend API service:
```bash
poetry run uvicorn backend.api.main:app --reload --port 8000
```
Start the Celery Worker to process rendering tasks:
```bash
poetry run celery -A backend.config.celery_app worker --loglevel=info -P solo
```
*(Note: On Windows, it is recommended to add `-P solo` to avoid concurrency compatibility issues)*

### 4. Frontend Start
```bash
cd frontend
npm install
npm run dev
```
Open your browser and navigate to `http://localhost:5173` to enter the workstation Dashboard.

## ⚠️ FAQ
- **MinIO Upload Error**: Please ensure you have accessed `http://localhost:9001` via browser, initialized buckets named `matrixv-assets` and `matrixv-videos`, and set their access policies to Public Read.
- **Task Stuck at Pending**: Check if the Redis container is running normally and if there are any error logs in the Celery Worker terminal.

## 📄 License
MIT License
