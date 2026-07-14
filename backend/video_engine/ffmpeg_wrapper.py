import subprocess
import os
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class FFmpegWrapper:
    """
    轻量级 FFmpeg Python 封装，用于基础的视频渲染、混音、添加字幕等。
    后续可扩展为基于 GPU (NVENC) 的硬解码。
    """
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def _run_command(self, cmd: List[str]):
        """执行 FFmpeg 命令行并捕获输出"""
        logger.info(f"Running FFmpeg: {' '.join(cmd)}")
        try:
            # 捕获异常，并且抑制标准输出以避免日志过多，仅在出错时暴露
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg command failed. stderr: {e.stderr}")
            raise RuntimeError(f"FFmpeg error: {e.stderr}") from e

    def mix_audio(self, video_path: str, audio_path: str, output_path: str, bgm_volume: float = 1.0):
        """
        基础功能: 将 BGM/配音 混音到视频中。
        这里使用最基础的替换/叠加逻辑。
        """
        # ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 output.mp4
        cmd = [
            self.ffmpeg_path,
            "-y", # 覆盖输出
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            # 如果需要调整音量，可加 filter: -filter_complex "volume={bgm_volume}"
            "-map", "0:v:0",
            "-map", "1:a:0",
            output_path
        ]
        self._run_command(cmd)
        return output_path

    def add_subtitle(self, video_path: str, srt_path: str, output_path: str):
        """
        基础功能: 给视频添加硬字幕。
        注意 srt 文件路径在不同系统下的转义问题。
        """
        # ffmpeg -i video.mp4 -vf subtitles=sub.srt output.mp4
        
        # 兼容 Windows 的路径转义
        escaped_srt_path = srt_path.replace("\\", "/").replace(":", "\\:")
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", video_path,
            "-vf", f"subtitles='{escaped_srt_path}'",
            "-c:a", "copy",
            output_path
        ]
        self._run_command(cmd)
        return output_path

    def generate_basic_video(self, image_or_video_path: str, audio_path: str, srt_path: Optional[str], output_path: str):
        """
        MVP1.4 测试流: 组合 视频/图片 + 音频 + 字幕 输出成品。
        """
        # 这里仅作骨架演示，实际业务会复杂很多
        temp_video = "temp_output.mp4"
        try:
            # 1. 混音
            self.mix_audio(image_or_video_path, audio_path, temp_video)
            
            # 2. 加字幕
            if srt_path:
                self.add_subtitle(temp_video, srt_path, output_path)
            else:
                os.rename(temp_video, output_path)
        finally:
            if os.path.exists(temp_video) and srt_path:
                os.remove(temp_video)
                
        return output_path
