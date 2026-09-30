import os
import asyncio
from typing import List, Dict, Any, Optional
from pydub import AudioSegment
import edge_tts

class AudioEngine:
    """Natural TTS voice generator and multi-track audio ducking engine."""
    
    VOICE_MAP = {
        "id_male": "id-ID-ArdiNeural",
        "id_female": "id-ID-GadisNeural",
        "en_male": "en-US-ChristopherNeural",
        "en_female": "en-US-JennyNeural"
    }
    
    @classmethod
    async def generate_speech_async(
        cls,
        text: str,
        output_file: str,
        voice_key: str = "id_male",
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> str:
        """Generate neural TTS voice file asynchronously."""
        voice = cls.VOICE_MAP.get(voice_key, cls.VOICE_MAP["id_male"])
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_file)
        return output_file

    @classmethod
    def generate_speech(
        cls,
        text: str,
        output_file: str,
        voice_key: str = "id_male",
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> str:
        """Synchronous wrapper for generating speech."""
        return asyncio.run(cls.generate_speech_async(text, output_file, voice_key, rate, pitch))

    @staticmethod
    def mix_tracks_with_ducking(
        voice_clips: List[Dict[str, Any]],
        bgm_file: Optional[str] = None,
        output_path: str = "/tmp/mixed_audio.m4a",
        total_duration_ms: Optional[int] = None,
        bgm_normal_db: float = -14.0,
        bgm_ducked_db: float = -26.0
    ) -> str:
        """
        Mix voice clips with automatic BGM ducking and precise timing.
        voice_clips format: [{'file': path, 'start_ms': 1000, 'volume_db': 0}]
        """
        # Calculate timeline end
        max_voice_end = 0
        loaded_voices = []
        for item in voice_clips:
            aud = AudioSegment.from_file(item['file'])
            start_ms = item.get('start_ms', 0)
            vol_db = item.get('volume_db', 0)
            if vol_db != 0:
                aud = aud + vol_db
            loaded_voices.append((start_ms, aud))
            end_ms = start_ms + len(aud)
            if end_ms > max_voice_end:
                max_voice_end = end_ms
                
        final_len_ms = total_duration_ms if total_duration_ms else max_voice_end + 1000
        base_timeline = AudioSegment.silent(duration=final_len_ms)
        
        # If BGM is provided, apply auto-ducking around voice segments
        if bgm_file and os.path.exists(bgm_file):
            bgm = AudioSegment.from_file(bgm_file)
            # Loop bgm if needed
            while len(bgm) < final_len_ms:
                bgm = bgm + bgm
            bgm = bgm[:final_len_ms]
            
            # Simple ducking segment construction
            ducked_bgm = AudioSegment.empty()
            cur_pos = 0
            # Sort voices by start_ms
            loaded_voices.sort(key=lambda x: x[0])
            
            # Construct ducked volume envelope
            bgm_track = bgm + bgm_normal_db
            for start_ms, aud in loaded_voices:
                voice_len = len(aud)
                duck_start = max(0, start_ms - 200)
                duck_end = min(final_len_ms, start_ms + voice_len + 300)
                
                # Apply ducking
                duck_segment = bgm[duck_start:duck_end] + bgm_ducked_db
                # Overlay ducked segment on base bgm
                bgm_track = bgm_track.overlay(duck_segment, position=duck_start)
                
            base_timeline = base_timeline.overlay(bgm_track)

        # Overlay all voice clips
        for start_ms, aud in loaded_voices:
            base_timeline = base_timeline.overlay(aud, position=start_ms)
            
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        # format="ipod" (m4a/mp4 container) instead of raw "adts": a bare ADTS elementary
        # stream has no reliable duration header, so ffmpeg/ffprobe estimate its length from
        # bitrate and can get it badly wrong (observed: reporting ~7s for actual ~10.5s audio),
        # which risks downstream tools mis-seeking or mis-trimming it.
        base_timeline.export(output_path, format="ipod")
        return output_path
