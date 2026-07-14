import logging
from openai import AsyncOpenAI
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """
    通用 LLM 客户端，封装官方 openai-python SDK。
    支持所有兼容 OpenAI 接口的模型（如 DeepSeek-V3, Qwen 等）。
    """
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        # 默认使用的模型名称，根据服务商而定 (比如 deepseek-chat 或 gpt-4o)
        self.default_model = "deepseek-chat"

    async def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        基础的文本生成。
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return ""

llm_client = LLMClient()
