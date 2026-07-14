import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseScraper
from backend.scraper.browser_pool import browser_pool

logger = logging.getLogger(__name__)

class XiaohongshuScraper(BaseScraper):
    """
    小红书热点抓取。
    初始 MVP 版本：通过 Playwright 抓取探索页，提取图文/视频的标题及点赞数。
    小红书反爬非常严格，未登录通常有极大的限制，此脚本仅作演示骨架。
    """
    
    async def fetch_hot_topics(self, limit: int = 20) -> List[Dict[str, Any]]:
        url = "https://www.xiaohongshu.com/explore"
        topics = []
        
        context = await browser_pool.get_context()
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle")
            
            # 小红书如果没有登录可能遇到弹窗，尝试关闭弹窗或注入 cookie
            # (在此版本暂留 TODO 供后续扩展)
            
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # 小红书的笔记卡片通常在 class="note-item" 这样的结构中
            items = soup.select('section.note-item')
            
            for index, item in enumerate(items):
                if index >= limit:
                    break
                    
                title_elem = item.select_one('.title span')
                like_elem = item.select_one('.like-count')
                
                title = title_elem.text.strip() if title_elem else f"XHS_Topic_{index}"
                
                like_text = like_elem.text.strip() if like_elem else "0"
                like_count = 0
                try:
                    if 'w' in like_text or 'W' in like_text:
                        like_count = int(float(like_text.replace('w', '').replace('W', '')) * 10000)
                    else:
                        like_count = int(like_text)
                except ValueError:
                    like_count = 0

                topics.append({
                    "platform": "xiaohongshu",
                    "source_url": url,
                    "title": title,
                    "hot_score": like_count, # 用点赞数近似表示热度
                    "raw_content": {"html_snippet": str(item)[:100]} 
                })
                
            logger.info(f"Fetched {len(topics)} hot topics from Xiaohongshu.")
        except Exception as e:
            logger.error(f"Error fetching Xiaohongshu hot topics: {e}")
        finally:
            await page.close()
            
        return topics
