from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    """
    平台爬虫基类。
    所有具体平台的爬虫都需要继承此类，并实现 fetch_hot_topics 方法。
    """
    
    @abstractmethod
    async def fetch_hot_topics(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        抓取当前平台的热点/热搜榜单。
        
        :param limit: 获取的条目数量限制
        :return: 包含热点信息的字典列表
                 结构建议:
                 {
                     "platform": "douyin",
                     "source_url": "...",
                     "title": "...",
                     "hot_score": 10000,
                     "raw_content": "{...}" 
                 }
        """
        pass
