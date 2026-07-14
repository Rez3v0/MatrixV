import logging
import asyncio
from typing import Dict, Any

from backend.config.celery_app import celery_app
from backend.models.database import SessionLocal
from backend.models.schema import VideoTask, AgentLog
from backend.config.settings import settings

# Agents
from backend.agents.trend_catcher.agent import TrendCatcherAgent
from backend.agents.script_editor.agent import ScriptEditorAgent
from backend.agents.visual_director.agent import VisualDirectorAgent
from backend.agents.audio_artist.agent import AudioArtistAgent
from backend.agents.video_editor.agent import VideoEditorAgent

logger = logging.getLogger(__name__)

def update_task_status(db, task_id: int, status: str):
    task = db.query(VideoTask).filter(VideoTask.id == task_id).first()
    if task:
        task.status = status
        db.commit()
        logger.info(f"Task {task_id} status updated to: {status}")

def log_agent_action(db, task_id: int, agent_name: str, action: str, output: str):
    log = AgentLog(task_id=task_id, agent_name=agent_name, action=action, output_metadata=output)
    db.add(log)
    db.commit()

async def async_pipeline(task_id: int):
    """异步执行整个流水线"""
    db = SessionLocal()
    try:
        # 检测是否配置了真的 Key，如果没有，启用 Dummy 模式，直接跳到完成
        if settings.OPENAI_API_KEY == "dummy-key-for-local" or settings.PEXELS_API_KEY == "dummy-pexels-key":
            logger.warning("Using DUMMY API Keys. Running fallback mock pipeline for demonstration...")
            
            update_task_status(db, task_id, "scraping")
            await asyncio.sleep(2)
            update_task_status(db, task_id, "writing")
            await asyncio.sleep(2)
            update_task_status(db, task_id, "rendering")
            await asyncio.sleep(2)
            
            # 假装完成，给一个测试用的视频链接
            task = db.query(VideoTask).filter(VideoTask.id == task_id).first()
            task.status = "done"
            task.output_url = "https://www.w3schools.com/html/mov_bbb.mp4" # 测试用视频
            db.commit()
            return
            
        # --- 真实流水线 ---
        
        # 1. Agent 1: 趋势捕手
        update_task_status(db, task_id, "scraping")
        trend_agent = TrendCatcherAgent()
        trends = await trend_agent.run(["douyin"], limit_per_platform=3)
        if not trends:
            raise Exception("No trends found.")
        best_trend = trends[0]
        log_agent_action(db, task_id, "TrendCatcher", "Found Best Trend", str(best_trend.get("title")))

        # 2. Agent 2: 文案总编
        update_task_status(db, task_id, "writing")
        script_agent = ScriptEditorAgent()
        final_script = await script_agent.run(best_trend)
        if not final_script:
            raise Exception("Script generation failed.")
        log_agent_action(db, task_id, "ScriptEditor", "Generated Script", final_script[:50] + "...")

        # 3. Agent 3: 视觉导演 (由于渲染需要较长时间，这里提前)
        visual_agent = VisualDirectorAgent()
        shots = await visual_agent.run(task_id, final_script)
        log_agent_action(db, task_id, "VisualDirector", "Fetched Shots", f"Count: {len(shots)}")

        # 4. Agent 4: 声音艺术家
        audio_agent = AudioArtistAgent()
        audio_asset = await audio_agent.run(task_id, final_script)
        log_agent_action(db, task_id, "AudioArtist", "Generated Audio", str(audio_asset.get("s3_url")))

        # 5. Agent 5: 剪辑大师
        update_task_status(db, task_id, "rendering")
        editor_agent = VideoEditorAgent()
        output_url = await editor_agent.run(task_id, shots, audio_asset)
        
        if output_url:
            log_agent_action(db, task_id, "VideoEditor", "Rendered Video", output_url)
            update_task_status(db, task_id, "done")
        else:
            raise Exception("Final rendering failed.")
            
    except Exception as e:
        logger.error(f"Pipeline failed for task {task_id}: {e}")
        update_task_status(db, task_id, "failed")
    finally:
        db.close()

@celery_app.task(name="backend.tasks.video_pipeline.run_video_pipeline", bind=True, max_retries=3)
def run_video_pipeline(self, task_id: int):
    """
    Celery 任务入口。
    整合 Agent 1 到 5，完成从热点捕获到视频渲染的全流程。
    """
    logger.info(f"--- Starting Video Pipeline for Task ID: {task_id} ---")
    asyncio.run(async_pipeline(task_id))
    logger.info(f"--- Finished Video Pipeline for Task ID: {task_id} ---")
    return {"status": "completed", "task_id": task_id}
