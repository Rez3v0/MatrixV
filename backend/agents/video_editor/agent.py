import logging
import os
from typing import List, Dict, Any

from .subtitle_generator import subtitle_generator
from .timeline_builder import timeline_builder
from backend.utils.minio_client import minio_client
from backend.models.database import SessionLocal
from backend.models.schema import VideoTask, Asset
from mutagen.mp3 import MP3 # 用于获取音频时长

logger = logging.getLogger(__name__)

class VideoEditorAgent:
    """
    Agent 5: 剪辑大师
    终极合成引擎。拉取视觉资产、声音资产，生成字幕，驱动 FFmpeg 渲染。
    """
    
    def __init__(self):
        self.temp_dir = "/tmp/matrixv/render"
        os.makedirs(self.temp_dir, exist_ok=True)

    def _get_audio_duration(self, audio_path: str) -> float:
        try:
            audio = MP3(audio_path)
            return audio.info.length
        except Exception as e:
            logger.error(f"Failed to get audio length: {e}")
            return 30.0 # 默认兜底
            
    async def run(self, task_id: int, shots: List[Dict[str, Any]], audio_asset: Dict[str, Any]) -> str:
        """
        :param shots: 包含 text 和 local_path (视频文件本地路径) 的列表
        :param audio_asset: 包含 local_path 的字典
        """
        logger.info(f"VideoEditorAgent starting for task {task_id}")
        
        audio_path = audio_asset.get("local_path")
        if not audio_path or not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return ""
            
        video_paths = [s.get("local_path") for s in shots if s.get("local_path")]
        if not video_paths:
            logger.error("No valid video shots found.")
            return ""

        # 1. 生成字幕
        audio_duration = self._get_audio_duration(audio_path)
        srt_path = os.path.join(self.temp_dir, f"task_{task_id}.srt")
        subtitle_generator.generate_srt(shots, audio_duration, srt_path)
        
        # 2. 渲染视频
        final_video_path = os.path.join(self.temp_dir, f"task_{task_id}_final.mp4")
        success = timeline_builder.render_final_video(
            video_paths=video_paths,
            audio_path=audio_path,
            srt_path=srt_path,
            output_path=final_video_path
        )
        
        if not success or not os.path.exists(final_video_path):
            logger.error("Final render failed.")
            return ""
            
        # 3. 上传成品到 MinIO
        bucket_name = "matrixv-videos"
        object_name = f"{task_id}/final_output.mp4"
        s3_url = minio_client.upload_file(bucket_name, object_name, final_video_path)
        
        if s3_url:
            # 4. 更新数据库状态
            db = SessionLocal()
            try:
                task = db.query(VideoTask).filter(VideoTask.id == task_id).first()
                if task:
                    task.status = "done"
                    task.video_url = s3_url
                    db.commit()
                    logger.info(f"Task {task_id} completed successfully! URL: {s3_url}")
            except Exception as e:
                logger.error(f"Failed to update task status: {e}")
            finally:
                db.close()
                
            return s3_url
            
        return ""

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    print("Video Editor Module Ready.")
