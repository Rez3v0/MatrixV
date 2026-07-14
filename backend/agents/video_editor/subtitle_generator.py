import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SubtitleGenerator:
    """
    简易 SRT 字幕生成器。
    MVP 阶段：根据音频总时长和分镜数，简单等分时间轴（或者根据字数比例分配）。
    """
    
    def _format_time(self, seconds: float) -> str:
        """将秒数格式化为 SRT 的 HH:MM:SS,mmm 格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milli = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milli:03d}"
        
    def generate_srt(self, shots: List[Dict[str, Any]], total_audio_duration: float, output_path: str) -> bool:
        """
        根据字数权重分配时间轴生成 SRT。
        :param shots: 包含 "text" 的分镜列表
        :param total_audio_duration: 音频轨总时长（秒）
        """
        try:
            total_chars = sum(len(shot.get("text", "")) for shot in shots)
            if total_chars == 0:
                logger.warning("No text found in shots to generate subtitles.")
                return False
                
            current_time = 0.0
            
            with open(output_path, "w", encoding="utf-8") as f:
                for idx, shot in enumerate(shots):
                    text = shot.get("text", "")
                    if not text:
                        continue
                        
                    # 按字数比例估算该句的时长
                    duration = (len(text) / total_chars) * total_audio_duration
                    start_time = current_time
                    end_time = current_time + duration
                    
                    # 写入 SRT 格式
                    f.write(f"{idx + 1}\n")
                    f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                    f.write(f"{text}\n\n")
                    
                    current_time = end_time
                    
            logger.info(f"Subtitles generated successfully at {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate SRT: {e}")
            return False

subtitle_generator = SubtitleGenerator()
