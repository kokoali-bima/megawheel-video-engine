import os
from typing import List, Dict, Any, Optional
from faster_whisper import WhisperModel

class SubtitleEngine:
    """Whisper transcription and animated ASS subtitle generator."""
    
    _model = None
    
    @classmethod
    def get_model(cls, model_size: str = "base"):
        if cls._model is None:
            cls._model = WhisperModel(model_size, device="cpu", compute_type="int8")
        return cls._model

    @classmethod
    def transcribe(cls, audio_or_video_path: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract word-level timestamps."""
        model = cls.get_model()
        segments, info = model.transcribe(
            audio_or_video_path,
            language=language,
            word_timestamps=True,
            vad_filter=True
        )
        
        results = []
        for segment in segments:
            for word in segment.words:
                results.append({
                    "start": word.start,
                    "end": word.end,
                    "word": word.word.strip(),
                    "probability": word.probability
                })
        return results

    @staticmethod
    def generate_ass_subtitles(
        word_list: List[Dict[str, Any]],
        output_ass_path: str,
        font_name: str = "Arial",
        font_size: int = 24,
        primary_color: str = "&H00FFFFFF",
        highlight_color: str = "&H0000FFFF", # Yellow in ASS (BGR format)
        words_per_group: int = 3
    ) -> str:
        """
        Generate kinetic pop-up subtitles in ASS format for TikTok/Shorts safe zones.
        """
        ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size * 2},{primary_color},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,40,40,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        def format_ass_time(sec: float) -> str:
            hrs = int(sec // 3600)
            mins = int((sec % 3600) // 60)
            secs = int(sec % 60)
            cs = int(round((sec - int(sec)) * 100))
            if cs >= 100:
                cs = 99
            return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"

        events = []
        # Group words into short dynamic chunks
        for i in range(0, len(word_list), words_per_group):
            chunk = word_list[i:i + words_per_group]
            start_time = chunk[0]['start']
            end_time = chunk[-1]['end']
            
            # Simple bounce animation effect {\t(0,100,\fscx115\fscy115)\t(100,200,\fscx100\fscy100)}
            chunk_text = " ".join([w['word'] for w in chunk]).upper()
            line = f"Dialogue: 0,{format_ass_time(start_time)},{format_ass_time(end_time)},Default,,0,0,0,,{{\\t(0,80,\\fscx110\\fscy110)\\t(80,160,\\fscx100\\fscy100)}}{chunk_text}"
            events.append(line)

        os.makedirs(os.path.dirname(os.path.abspath(output_ass_path)), exist_ok=True)
        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(ass_header + "\n".join(events))
            
        return output_ass_path
