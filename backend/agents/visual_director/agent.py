import logging
import json
import asyncio
from typing import Dict, Any, List

from backend.utils.llm_client import llm_client
from backend.utils.minio_client import minio_client
from .prompts import SYSTEM_PROMPT_VISUAL_DIRECTOR
from .pexels_client import pexels_client
from backend.models.database import SessionLocal
from backend.models.schema import Asset

logger = logging.getLogger(__name__)

class VisualDirectorAgent:
    """
    Agent 3: 视觉导演
    负责将口播文案切分为镜头，并从 Pexels 等素材库拉取视频素材，落盘到 MinIO。
    """
    
    async def split_script_to_shots(self, script: str) -> List[Dict[str, Any]]:
        """使用 LLM 切分文案并生成关键词"""
        logger.info("Splitting script into shots...")
        user_prompt = f"请拆解以下文案：\n\n{script}"
        
        response = await llm_client.generate_text(
            system_prompt=SYSTEM_PROMPT_VISUAL_DIRECTOR,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        try:
            # 提取 JSON
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
                
            data = json.loads(json_str)
            return data.get("shots", [])
        except Exception as e:
            logger.error(f"Failed to parse shots JSON: {e}")
            return []

    async def fetch_and_store_asset(self, task_id: int, shot: Dict[str, Any]) -> Dict[str, Any]:
        """为单个镜头搜索素材、下载并上传至 MinIO，并入库"""
        keyword = shot.get("search_keyword")
        if not keyword:
            return shot
            
        logger.info(f"Searching video for keyword: {keyword}")
        video_info = await pexels_client.search_video(keyword)
        
        if video_info:
            filename = f"task_{task_id}_shot_{shot.get('id')}.mp4"
            local_path = await pexels_client.download_video(video_info["url"], filename)
            
            if local_path:
                # 上传到 MinIO
                bucket_name = "matrixv-assets"
                object_name = f"tasks/{task_id}/videos/{filename}"
                s3_url = minio_client.upload_file(bucket_name, object_name, local_path)
                
                # 记录到数据库
                db = SessionLocal()
                try:
                    asset = Asset(
                        task_id=task_id,
                        type="video",
                        storage_url=s3_url,
                        metadata_json={
                            "source": "pexels",
                            "author": video_info["author"],
                            "keyword": keyword,
                            "text_content": shot.get("text")
                        }
                    )
                    db.add(asset)
                    db.commit()
                    db.refresh(asset)
                    shot["asset_id"] = asset.id
                    shot["s3_url"] = s3_url
                except Exception as e:
                    logger.error(f"Failed to save asset to DB: {e}")
                finally:
                    db.close()
                    
        return shot

    async def run(self, task_id: int, final_script: str) -> List[Dict[str, Any]]:
        """执行视觉素材获取流水线"""
        # 1. 拆分镜头
        shots = await self.split_script_to_shots(final_script)
        
        if not shots:
            logger.warning("No shots generated.")
            return []
            
        # 2. 并发拉取并存储每个镜头的素材
        logger.info(f"Generated {len(shots)} shots. Fetching visual assets...")
        tasks = []
        for shot in shots:
            tasks.append(self.fetch_and_store_asset(task_id, shot))
            
        completed_shots = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤掉异常
        valid_shots = [s for s in completed_shots if not isinstance(s, Exception)]
        logger.info(f"Visual Director finished. Gathered assets for {len(valid_shots)} shots.")
        return valid_shots

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        agent = VisualDirectorAgent()
        dummy_script = "你一定不知道，昨晚发生了什么。其实，年轻人不买房的真相，远比你想象的残酷。点赞关注，听我慢慢说。"
        # 假设当前有一个 task_id = 999
        shots = await agent.run(task_id=999, final_script=dummy_script)
        print("\n=== Final Storyboard ===")
        print(json.dumps(shots, indent=2, ensure_ascii=False))
        print("========================\n")
        
    asyncio.run(test())
