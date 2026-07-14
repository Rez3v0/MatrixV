from typing import List, Dict, Any

class TopicFilter:
    """
    黑马选题过滤器。
    通过简单的量化模型筛选出潜力高的热点。
    """
    
    def __init__(self, min_hot_score: int = 1000):
        self.min_hot_score = min_hot_score

    def filter_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤逻辑：
        1. 过滤掉热度低于阈值的选题。
        2. 若有详细的评论、点赞数，计算互动率 (点赞/评论比)。
           （MVP 版本暂用基础的分数阈值进行过滤，模拟其机制）
        """
        filtered = []
        for topic in topics:
            score = topic.get("hot_score", 0)
            
            # 基础过滤规则：热度需达标
            if score >= self.min_hot_score:
                # 给选题打个评估标签
                topic["quality_tag"] = "High Potential" if score > self.min_hot_score * 5 else "Normal"
                filtered.append(topic)
                
        # 按照热度从高到低排序
        filtered.sort(key=lambda x: x.get("hot_score", 0), reverse=True)
        return filtered
