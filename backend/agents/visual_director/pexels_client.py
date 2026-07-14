import httpx
import logging
import aiofiles
import os
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class PexelsClient:
    """
    Pexels API 客户端封装，用于根据关键词搜索和下载免费正版视频素材。
    """
    def __init__(self):
        self.api_key = settings.PEXELS_API_KEY
        self.base_url = "https://api.pexels.com/videos"
        self.headers = {
            "Authorization": self.api_key
        }
        # 临时存储路径
        self.temp_dir = "/tmp/matrixv/downloads"
        os.makedirs(self.temp_dir, exist_ok=True)

    async def search_video(self, query: str, orientation: str = "portrait") -> dict | None:
        """
        根据关键词搜索视频。默认竖屏 (portrait)。
        返回最高赞/最相关的一个视频信息。
        """
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": 1
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("videos") and len(data["videos"]) > 0:
                    video_info = data["videos"][0]
                    # 获取视频列表中质量最高或特定分辨率的下载链接
                    # Pexels 返回的 video_files 是按质量排序的
                    video_files = video_info.get("video_files", [])
                    if video_files:
                        # 简单策略：获取 HD 质量的竖屏视频
                        best_file = video_files[0]
                        for vf in video_files:
                            if vf.get("quality") == "hd":
                                best_file = vf
                                break
                                
                        return {
                            "id": video_info["id"],
                            "url": best_file["link"],
                            "author": video_info["user"]["name"]
                        }
        except Exception as e:
            logger.error(f"Pexels API search failed for query '{query}': {e}")
            
        return None

    async def download_video(self, video_url: str, filename: str) -> str | None:
        """
        下载视频到本地临时目录。
        返回本地文件路径。
        """
        filepath = os.path.join(self.temp_dir, filename)
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Downloading video from {video_url}")
                response = await client.get(video_url, timeout=30.0)
                response.raise_for_status()
                
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(response.content)
                    
            logger.info(f"Video downloaded to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to download video {video_url}: {e}")
            return None

pexels_client = PexelsClient()
