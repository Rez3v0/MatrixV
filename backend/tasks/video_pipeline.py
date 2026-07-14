import time
from celery.utils.log import get_task_logger
from backend.config.celery_app import celery_app
from backend.models.database import SessionLocal
from backend.models.schema import VideoTask

logger = get_task_logger(__name__)

def update_task_status(db_session, task_id: int, status: str):
    """辅助函数：更新数据库中任务的状态"""
    task = db_session.query(VideoTask).filter(VideoTask.id == task_id).first()
    if task:
        task.status = status
        db_session.commit()
        logger.info(f"Task {task_id} status updated to {status}")

@celery_app.task(bind=True, max_retries=3)
def run_video_pipeline(self, task_id: int):
    """
    运行视频生成的完整流水线任务（骨架版）。
    模拟状态机流转：pending → scraping → writing → rendering → publishing → done/failed
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting video pipeline for task {task_id}")
        
        # 1. Scraping (Agent 1: 趋势捕手/数据采集)
        update_task_status(db, task_id, "scraping")
        # TODO: 接入 Agent 1 逻辑
        time.sleep(1) # 模拟耗时
        
        # 2. Writing (Agent 2: 文案生成)
        update_task_status(db, task_id, "writing")
        # TODO: 接入 Agent 2 逻辑
        time.sleep(1)
        
        # 3. Visual & Audio (Agent 3 & 4: 镜头匹配与声音生成，通常与 writing 或 rendering 结合)
        # 此处简化为在 rendering 前准备好素材
        
        # 4. Rendering (Agent 5: FFmpeg 混剪)
        update_task_status(db, task_id, "rendering")
        # TODO: 调用 FFmpeg 渲染引擎
        time.sleep(2)
        
        # 5. Publishing (Agent 6: 分发与回传)
        update_task_status(db, task_id, "publishing")
        # TODO: 执行发布脚本
        time.sleep(1)
        
        # 6. Done
        update_task_status(db, task_id, "done")
        return {"task_id": task_id, "status": "done", "video_url": "dummy_url.mp4"}
        
    except Exception as exc:
        logger.error(f"Error in video pipeline for task {task_id}: {exc}")
        update_task_status(db, task_id, "failed")
        # 可选：重试
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()
