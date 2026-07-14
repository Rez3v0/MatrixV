import edge_tts
import logging
import os

logger = logging.getLogger(__name__)

class TTSEngine:
    """
    文本转语音引擎，使用微软 Edge TTS。
    """
    def __init__(self, default_voice: str = "zh-CN-XiaoxiaoNeural"):
        self.default_voice = default_voice
        self.output_dir = "/tmp/matrixv/audio"
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_audio(self, text: str, filename: str, voice: str = None) -> str | None:
        """
        生成语音文件。
        """
        v = voice if voice else self.default_voice
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            logger.info(f"Generating TTS audio for text (length {len(text)}) using voice {v}")
            # Edge-TTS 生成音频
            communicate = edge_tts.Communicate(text, v)
            await communicate.save(output_path)
            
            logger.info(f"Audio generated successfully at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate TTS audio: {e}")
            return None

tts_engine = TTSEngine()
