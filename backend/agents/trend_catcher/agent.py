import logging
import asyncio
from typing import List, Dict, Any

from backend.scraper.platforms.douyin import DouyinScraper
from backend.scraper.platforms.xiaohongshu import XiaohongshuScraper
from backend.agents.trend_catcher.filter import TopicFilter
from backend.scraper.browser_pool import browser_pool

logger = logging.getLogger(__name__)

class TrendCatcherAgent:
    """
    Agent 1: 趋势捕手
    负责协调各平台爬虫，收集热点，并过滤出黑马选题。
    """
    
    def __init__(self):
        self.scrapers = {
            "douyin": DouyinScraper(),
            "xiaohongshu": XiaohongshuScraper()
        }
        self.topic_filter = TopicFilter(min_hot_score=1000)

    async def run(self, platforms: List[str] = ["douyin", "xiaohongshu"], limit_per_platform: int = 10) -> List[Dict[str, Any]]:
        """
        执行抓取流水线。
        """
        all_topics = []
        try:
            logger.info("TrendCatcherAgent starting...")
            # 并发执行各个平台的抓取任务
            tasks = []
            for p in platforms:
                if p in self.scrapers:
                    tasks.append(self.scrapers[p].fetch_hot_topics(limit=limit_per_platform))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for res in results:
                if isinstance(res, list):
                    all_topics.extend(res)
                else:
                    logger.error(f"Scraper returned error: {res}")
                    
            # 过滤高潜力选题
            filtered_topics = self.topic_filter.filter_topics(all_topics)
            logger.info(f"TrendCatcherAgent finished. Retained {len(filtered_topics)} high potential topics.")
            return filtered_topics
            
        except Exception as e:
            logger.error(f"TrendCatcherAgent failed: {e}")
            return []
        finally:
            # MVP: 运行结束后关闭浏览器池
            await browser_pool.close()

if __name__ == "__main__":
    # 本地测试入口
    logging.basicConfig(level=logging.INFO)
    agent = TrendCatcherAgent()
    results = asyncio.run(agent.run(["douyin"], limit_per_platform=5))
    for r in results:
        print(f"[{r['platform']}] {r['title']} - Score: {r['hot_score']} - Tag: {r.get('quality_tag')}")
