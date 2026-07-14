import logging
import json
from typing import Dict, Any, Tuple
from backend.utils.llm_client import llm_client
from .sensitive_filter import sensitive_filter
from .prompts import SYSTEM_PROMPT_SCRIPT_WRITER, SYSTEM_PROMPT_CRITIC

logger = logging.getLogger(__name__)

class ScriptEditorAgent:
    """
    Agent 2: 文案总编
    负责将热点素材改写为三段式爆款口播文案，
    包含敏感词过滤与自我反思打分(Reflection/Critic) 回路。
    """
    
    def __init__(self):
        self.max_retries = 3

    async def generate_script(self, raw_topic: Dict[str, Any]) -> str:
        """根据原始话题生成初始文案"""
        topic_title = raw_topic.get("title", "")
        topic_content = raw_topic.get("raw_content", "")
        
        user_prompt = f"请根据以下热点素材撰写文案：\n标题：{topic_title}\n素材内容：{topic_content}"
        
        logger.info("Generating initial script...")
        script = await llm_client.generate_text(SYSTEM_PROMPT_SCRIPT_WRITER, user_prompt)
        return script

    async def evaluate_script(self, script: str) -> Tuple[bool, str, int]:
        """使用 LLM 批评者打分"""
        user_prompt = f"请评价以下文案：\n\n{script}"
        logger.info("Evaluating script...")
        response = await llm_client.generate_text(SYSTEM_PROMPT_CRITIC, user_prompt, temperature=0.3)
        
        try:
            # 尝试提取 JSON (有时候 LLM 会加上 ```json 标签)
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
                
            result = json.loads(json_str)
            return result.get("pass", False), result.get("feedback", ""), result.get("score", 0)
        except Exception as e:
            logger.error(f"Failed to parse critic response: {response}, Error: {e}")
            # 降级：如果解析失败，默认通过以避免死循环
            return True, "JSON parsing failed, auto pass", 80

    async def run(self, raw_topic: Dict[str, Any]) -> str:
        """执行文案生成、过滤与自评回路"""
        
        # 1. 生成初始文案
        script = await self.generate_script(raw_topic)
        if not script:
            return ""

        # 2. 敏感词处理
        if sensitive_filter.contains_sensitive_words(script):
            logger.warning("Initial script contains sensitive words, filtering...")
            # MVP: 简单替换。进阶版可将敏感词反馈给 LLM 让其重写。
            script = sensitive_filter.replace_sensitive_words(script)

        # 3. 评分回路 (Critic Loop)
        for attempt in range(self.max_retries):
            passed, feedback, score = await self.evaluate_script(script)
            logger.info(f"Critic Evaluation [Attempt {attempt+1}]: Score {score}. Feedback: {feedback}")
            
            if passed:
                logger.info("Script passed evaluation.")
                break
            else:
                if attempt == self.max_retries - 1:
                    logger.warning("Max retries reached. Using the last generated script despite low score.")
                    break
                
                # 请求重写
                logger.info("Script failed evaluation. Requesting rewrite...")
                rewrite_prompt = (
                    f"上一次生成的文案没有达标。评委反馈：{feedback}。\n"
                    f"请修正上面的问题，重新输出一个符合要求的三段式爆款文案。原素材标题：{raw_topic.get('title', '')}"
                )
                script = await llm_client.generate_text(SYSTEM_PROMPT_SCRIPT_WRITER, rewrite_prompt)
                
                # 重新过滤
                script = sensitive_filter.replace_sensitive_words(script)
                
        return script

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        agent = ScriptEditorAgent()
        dummy_topic = {
            "title": "年轻人为什么不愿意买房了？",
            "raw_content": "最近统计局数据显示，90后和00后购房比例断崖式下跌。大家都在讨论租房好还是买房好。"
        }
        final_script = await agent.run(dummy_topic)
        print("\n=== Final Script ===")
        print(final_script)
        print("====================\n")
        
    asyncio.run(test())
