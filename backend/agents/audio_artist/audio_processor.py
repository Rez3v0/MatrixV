import logging
import random
import os
from pydub import AudioSegment
from pydub.generators import WhiteNoise

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    音频处理器。
    负责对抗各大平台的音频特征去重，以及 BGM 混合。
    """
    
    def add_white_noise(self, audio: AudioSegment, noise_level_db: int = -45) -> AudioSegment:
        """
        在音频底层加入极弱的白噪音，破坏物理 MD5 和极度精细的波形。
        """
        logger.info("Adding white noise for anti-fingerprinting...")
        noise = WhiteNoise().to_audio_segment(duration=len(audio))
        # 调整白噪音音量非常低
        noise = noise - abs(noise_level_db)
        return audio.overlay(noise)

    def shift_speed(self, audio: AudioSegment, min_speed: float = 0.98, max_speed: float = 1.05) -> AudioSegment:
        """
        微调语速（变速不变调通常需要更高级的算法，pydub 默认变速会变调，但在极小范围内可接受。
        为防平台根据音频长度去重，这里进行极细微的时长扭曲）
        """
        speed = random.uniform(min_speed, max_speed)
        logger.info(f"Shifting audio speed by {speed:.3f}x")
        
        # 改变采样率来变速
        sound_with_altered_frame_rate = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        })
        # 设回标准帧率
        return sound_with_altered_frame_rate.set_frame_rate(audio.frame_rate)

    def mix_bgm(self, vocal: AudioSegment, bgm_path: str, vocal_vol_boost: int = 5, bgm_vol_drop: int = -15) -> AudioSegment:
        """
        将 BGM 混合到人声下方。
        """
        try:
            logger.info(f"Mixing BGM from {bgm_path}")
            bgm = AudioSegment.from_file(bgm_path)
            
            # 调整音量
            vocal = vocal + vocal_vol_boost
            bgm = bgm + bgm_vol_drop
            
            # 如果 BGM 短于人声，则循环
            if len(bgm) < len(vocal):
                loop_count = (len(vocal) // len(bgm)) + 1
                bgm = bgm * loop_count
                
            # 裁剪多余的 BGM
            bgm = bgm[:len(vocal)]
            
            # 叠加
            mixed = vocal.overlay(bgm)
            return mixed
        except Exception as e:
            logger.error(f"Failed to mix BGM: {e}")
            return vocal # 失败则原样返回人声

    def process_and_export(self, input_path: str, output_path: str, bgm_path: str = None) -> bool:
        """
        处理主链路。
        """
        try:
            audio = AudioSegment.from_file(input_path)
            
            # 抗去重策略 1: 变速
            audio = self.shift_speed(audio)
            
            # 抗去重策略 2: 注入白噪音
            audio = self.add_white_noise(audio)
            
            # 混音 BGM
            if bgm_path and os.path.exists(bgm_path):
                audio = self.mix_bgm(audio, bgm_path)
                
            # 导出
            audio.export(output_path, format="mp3", bitrate="192k")
            logger.info(f"Audio processed and exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return False

audio_processor = AudioProcessor()
