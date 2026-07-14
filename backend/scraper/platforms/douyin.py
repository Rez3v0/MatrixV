import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseScraper
from backend.scraper.browser_pool import browser_pool

logger = logging.getLogger(__name__)

class DouyinScraper(BaseScraper):
    """
    抖音热榜/热搜抓取。
    初始 MVP 版本：通过 Playwright 打开抖音热搜网页版并解析 DOM。
    """
    
    async def fetch_hot_topics(self, limit: int = 20) -> List[Dict[str, Any]]:
        url = "https://www.douyin.com/hot"
        topics = []
        
        context = await browser_pool.get_context()
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle")
            
            # 简单的向下滚动以触发懒加载
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # 这里的选择器是伪代码，因为真实的 DOM 结构会变化
            # 需要根据实际页面的 class 调整
            items = soup.select('div[data-e2e="hot-board-item"]') 
            
            for index, item in enumerate(items):
                if index >= limit:
                    break
                    
                title_elem = item.select_one('.title')
                hot_score_elem = item.select_one('.hot-value')
                
                title = title_elem.text.strip() if title_elem else f"Unknown_Topic_{index}"
                
                # 尝试解析热度分，如 "123.4万"
                hot_score_text = hot_score_elem.text.strip() if hot_score_elem else "0"
                hot_score = 0
                try:
                    if '万' in hot_score_text:
                        hot_score = int(float(hot_score_text.replace('万', '')) * 10000)
                    else:
                        hot_score = int(hot_score_text)
                except ValueError:
                    hot_score = 0

                topics.append({
                    "platform": "douyin",
                    "source_url": url,
                    "title": title,
                    "hot_score": hot_score,
                    "raw_content": {"html_snippet": str(item)[:100]} 
                })
                
            logger.info(f"Fetched {len(topics)} hot topics from Douyin.")
        except Exception as e:
            logger.error(f"Error fetching Douyin hot topics: {e}")
        finally:
            await page.close()
            
        return topics
