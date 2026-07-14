import logging
import os
from typing import Dict, Any

from .tts_engine import tts_engine
from .audio_processor import audio_processor
from backend.utils.minio_client import minio_client
from backend.models.database import SessionLocal
from backend.models.schema import Asset

logger = logging.getLogger(__name__)

class AudioArtistAgent:
    """
    Agent 4: 声音艺术家
    负责将最终文案转化为配音，混入 BGM 并应用抗去重策略，最后上传到 MinIO。
    """
    
    async def run(self, task_id: int, final_script: str, bgm_path: str = None) -> Dict[str, Any]:
        """
        执行音频生成流水线。
        返回生成的 Asset 信息。
        """
        logger.info(f"AudioArtistAgent starting for task {task_id}")
        
        # 1. 生成原始 TTS
        raw_filename = f"task_{task_id}_raw.mp3"
        raw_path = await tts_engine.generate_audio(final_script, raw_filename)
        
        if not raw_path or not os.path.exists(raw_path):
            logger.error("TTS generation failed.")
            return {}
            
        # 2. 音频处理 (加白噪音、变速、混音)
        processed_filename = f"task_{task_id}_processed.mp3"
        processed_path = os.path.join(tts_engine.output_dir, processed_filename)
        
        success = audio_processor.process_and_export(raw_path, processed_path, bgm_path)
        if not success:
            logger.error("Audio processing failed.")
            return {}
            
        # 3. 上传到 MinIO
        bucket_name = "matrixv-assets"
        object_name = f"tasks/{task_id}/audio/{processed_filename}"
        s3_url = minio_client.upload_file(bucket_name, object_name, processed_path)
        
        if not s3_url:
            logger.error("Failed to upload processed audio to MinIO.")
            return {}
            
        # 4. 数据库持久化
        db = SessionLocal()
        try:
            asset = Asset(
                task_id=task_id,
                type="audio",
                storage_url=s3_url,
                metadata_json={
                    "source": "edge-tts",
                    "voice": tts_engine.default_voice,
                    "has_bgm": bgm_path is not None,
                    "anti_fingerprint_applied": True
                }
            )
            db.add(asset)
            db.commit()
            db.refresh(asset)
            
            logger.info(f"AudioArtistAgent finished. Asset ID: {asset.id}")
            return {
                "asset_id": asset.id,
                "s3_url": s3_url,
                "local_path": processed_path
            }
        except Exception as e:
            logger.error(f"Failed to save audio asset to DB: {e}")
            return {}
        finally:
            db.close()

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        agent = AudioArtistAgent()
        dummy_script = "你一定不知道，昨晚发生了什么。其实，年轻人不买房的真相，远比你想象的残酷。点赞关注，听我慢慢说。"
        result = await agent.run(task_id=888, final_script=dummy_script)
        print("\n=== Final Audio Asset ===")
        print(result)
        print("=========================\n")
        
    asyncio.run(test())
