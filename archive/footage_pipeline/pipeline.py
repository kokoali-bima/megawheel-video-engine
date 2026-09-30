#!/usr/bin/env python3
"""
Master Video Pipeline CLI
Usage: python3 pipeline.py --source /path/to/video.mp4 --script script.json --out /tmp/final_video.mp4
"""

import argparse
import json
import os
from pydub import AudioSegment

from core.downloader import VideoDownloader
from core.scene_detector import SceneAnalyzer
from core.semantic_sync import SemanticSyncEngine
from core.audio_engine import AudioEngine
from core.subtitle_engine import SubtitleEngine
from core.compositor import VideoCompositor
from core.validator import PreflightValidator


def load_script(script_arg: str):
    """Accept a JSON file path or an inline JSON array of narration sentences."""
    if os.path.exists(script_arg):
        with open(script_arg) as f:
            data = json.load(f)
    else:
        data = json.loads(script_arg)
    return data if isinstance(data, list) else [data]


def main():
    parser = argparse.ArgumentParser(description="iPandu Automated Video Engine")
    parser.add_argument("--source", required=True, help="Source video URL or local file path")
    parser.add_argument("--script", required=True, help="JSON file or inline JSON array of narration sentences")
    parser.add_argument("--voice", default="id_male", help="Voice ID (id_male, id_female, en_male, en_female)")
    parser.add_argument("--out", required=True, help="Output MP4 file path")
    parser.add_argument("--work-dir", default="/tmp/ipandu_sync", help="Scratch directory for intermediate files")
    args = parser.parse_args()

    os.makedirs(args.work_dir, exist_ok=True)
    sentences = load_script(args.script)

    print(f"[iPandu Engine] Sourcing video -> {args.source}")
    video_path = args.source
    if args.source.startswith("http://") or args.source.startswith("https://"):
        video_path = os.path.join(args.work_dir, "source.mp4")
        VideoDownloader.search_and_download(args.source, video_path)

    print("[iPandu Engine] Detecting scenes...")
    scenes = SceneAnalyzer.detect_scenes(video_path)
    if not scenes:
        raise RuntimeError(f"No scenes detected in {video_path}")

    print(f"[iPandu Engine] Semantic sync: {len(sentences)} sentences -> {len(scenes)} scenes")
    matches = SemanticSyncEngine.sync_narration_to_scenes(
        video_path, scenes, sentences, thumb_dir=os.path.join(args.work_dir, "thumbs")
    )

    print("[iPandu Engine] Generating narration + fitting scene timing to TTS duration...")
    voice_clips = []
    segments = []
    cursor_ms = 0
    for i, match in enumerate(matches):
        voice_file = os.path.join(args.work_dir, f"voice_{i:03d}.mp3")
        AudioEngine.generate_speech(match["sentence"], voice_file, voice_key=args.voice)
        duration_sec = len(AudioSegment.from_file(voice_file)) / 1000.0

        fit = SemanticSyncEngine.fit_scene_to_duration(
            match["scene_start"], match["scene_end"], duration_sec
        )
        segments.append({**match, **fit, "voice_file": voice_file})
        voice_clips.append({"file": voice_file, "start_ms": cursor_ms})
        cursor_ms += int(duration_sec * 1000)

    print("[iPandu Engine] Mixing narration track...")
    mixed_audio = AudioEngine.mix_tracks_with_ducking(
        voice_clips, output_path=os.path.join(args.work_dir, "mixed_audio.aac")
    )

    print("[iPandu Engine] Rendering matched scene segments...")
    rendered_segments = []
    for i, seg in enumerate(segments):
        seg_file = os.path.join(args.work_dir, f"segment_{i:03d}.mp4")
        VideoCompositor.render_shorts_segment(
            video_path, seg["video_in"], seg["duration"], seg_file, hold_sec=seg["hold_sec"]
        )
        rendered_segments.append(seg_file)

    print("[iPandu Engine] Transcribing narration for kinetic subtitles...")
    words = SubtitleEngine.transcribe(mixed_audio)
    ass_path = SubtitleEngine.generate_ass_subtitles(words, os.path.join(args.work_dir, "subs.ass"))

    print(f"[iPandu Engine] Finalizing -> {args.out}")
    VideoCompositor.merge_and_finalize(rendered_segments, mixed_audio, ass_path, args.out)

    print("[iPandu Engine] Running preflight validation...")
    report = PreflightValidator.audit_video(args.out)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
