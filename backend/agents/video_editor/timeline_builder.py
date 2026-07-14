import logging
import os
import subprocess
from typing import List

logger = logging.getLogger(__name__)

class TimelineBuilder:
    """
    负责构建和执行 FFmpeg 渲染图。
    """
    
    def render_final_video(
        self, 
        video_paths: List[str], 
        audio_path: str, 
        srt_path: str, 
        output_path: str,
        target_resolution: str = "1080:1920"
    ) -> bool:
        """
        组装所有碎片视频、配音轨，烧录字幕。
        """
        if not video_paths:
            logger.error("No video paths provided for rendering.")
            return False
            
        try:
            logger.info("Building FFmpeg timeline...")
            
            # 1. 预处理：生成文件列表供 ffmpeg concat demuxer 使用
            # （由于不同视频的编解码器或帧率可能不同，保险起见应先统一转码，
            # 为 MVP 效率，这里直接尝试使用 concat filter）
            
            # 使用复杂滤镜 (filter_complex) 拼接多个视频
            inputs = []
            filter_parts = []
            
            for i, vp in enumerate(video_paths):
                inputs.extend(["-i", vp])
                # 将每个视频缩放裁切到指定分辨率，设置 30fps，提取视频流
                filter_parts.append(f"[{i}:v]scale={target_resolution}:force_original_aspect_ratio=increase,crop={target_resolution},setsar=1,fps=30,format=yuv420p[v{i}]")
                
            # concat 视频流
            concat_str = "".join([f"[v{i}]" for i in range(len(video_paths))])
            filter_parts.append(f"{concat_str}concat=n={len(video_paths)}:v=1:a=0[concat_v]")
            
            # 烧录字幕 (注意在 Windows 环境下路径中的反斜杠和冒号需要转义，这里做了极简处理)
            # 在 Linux 环境下通常更稳定。如果 srt_path 是 /tmp/xx.srt 就没问题。
            escaped_srt = srt_path.replace("\\", "/").replace(":", "\\:")
            filter_parts.append(f"[concat_v]subtitles='{escaped_srt}':force_style='FontSize=24,PrimaryColour=&H00FFFF,Outline=1'[final_v]")
            
            filter_complex = ";".join(filter_parts)
            
            # 组合 FFmpeg 命令
            cmd = [
                "ffmpeg",
                "-y", # 覆盖输出
            ]
            cmd.extend(inputs)
            # 添加音频轨
            cmd.extend(["-i", audio_path])
            
            cmd.extend([
                "-filter_complex", filter_complex,
                "-map", "[final_v]",
                "-map", f"{len(video_paths)}:a", # 映射最后一个输入(音频)的音频流
                "-shortest", # 以最短的流（通常是音频）为准截断视频
                "-c:v", "libx264",
                "-c:a", "aac",
                "-b:a", "192k",
                output_path
            ])
            
            logger.info(f"Executing FFmpeg command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg failed with code {process.returncode}:\n{stderr}")
                return False
                
            logger.info(f"Rendering complete: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error during video rendering: {e}")
            return False

timeline_builder = TimelineBuilder()
