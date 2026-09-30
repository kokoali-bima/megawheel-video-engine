#!/usr/bin/env python3
"""
iPandu Video Engine API Server
- FastAPI REST Backend
- End-to-End Autonomous Rendering Pipeline
- Approval-Gated YouTube Shorts Uploader
"""

import os
import uuid
import json
import logging
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from pydub import AudioSegment
from core.downloader import VideoDownloader
from core.scene_detector import SceneAnalyzer
from core.semantic_sync import SemanticSyncEngine
from core.audio_engine import AudioEngine
from core.subtitle_engine import SubtitleEngine
from core.compositor import VideoCompositor
from core.validator import PreflightValidator
from core.youtube_uploader import YouTubeUploader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("video-engine-service")

app = FastAPI(title="iPandu Video Engine API", version="1.1.0")

executor = ThreadPoolExecutor(max_workers=2)
JOBS: Dict[str, Dict[str, Any]] = {}
uploader = YouTubeUploader()

class RenderJobRequest(BaseModel):
    source: str = Field(..., description="Source video URL or local path")
    script: List[str] = Field(..., description="List of narration sentences")
    voice: str = Field(default="id_male", description="Voice ID (id_male, id_female, en_male, en_female, af_heart, etc.)")
    title: Optional[str] = Field(default=None, description="Suggested video title for publishing")
    output_filename: Optional[str] = None

class ApproveUploadRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    privacy_status: str = Field(default="unlisted", description="Privacy: 'unlisted', 'private', or 'public'")
    category_id: str = Field(default="20", description="20: Gaming, 24: Entertainment, 27: Education")

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[str] = None
    output_file: Optional[str] = None
    suggested_title: Optional[str] = None
    suggested_description: Optional[str] = None
    suggested_tags: Optional[List[str]] = None
    youtube_url: Optional[str] = None
    error: Optional[str] = None
    report: Optional[Dict[str, Any]] = None

def run_render_pipeline(job_id: str, req: RenderJobRequest):
    work_dir = f"/tmp/ipandu_render_{job_id}"
    os.makedirs(work_dir, exist_ok=True)
    out_file = req.output_filename or f"/root/renders/render_{job_id}.mp4"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    try:
        JOBS[job_id]["status"] = "processing"
        JOBS[job_id]["progress"] = "Preparing source video"
        logger.info(f"Job {job_id}: starting render with source {req.source}")

        video_path = req.source
        if req.source.startswith("http://") or req.source.startswith("https://"):
            video_path = os.path.join(work_dir, "source.mp4")
            VideoDownloader.search_and_download(req.source, video_path)

        JOBS[job_id]["progress"] = "Detecting scenes"
        scenes = SceneAnalyzer.detect_scenes(video_path)
        if not scenes:
            raise RuntimeError(f"No scenes detected in {video_path}")

        JOBS[job_id]["progress"] = f"Semantic syncing {len(req.script)} sentences"
        matches = SemanticSyncEngine.sync_narration_to_scenes(
            video_path, scenes, req.script, thumb_dir=os.path.join(work_dir, "thumbs")
        )

        JOBS[job_id]["progress"] = "Generating TTS & audio fitting"
        voice_clips = []
        segments = []
        cursor_ms = 0
        for i, match in enumerate(matches):
            voice_file = os.path.join(work_dir, f"voice_{i:03d}.mp3")
            AudioEngine.generate_speech(match["sentence"], voice_file, voice_key=req.voice)
            duration_sec = len(AudioSegment.from_file(voice_file)) / 1000.0

            fit = SemanticSyncEngine.fit_scene_to_duration(
                match["scene_start"], match["scene_end"], duration_sec
            )
            segments.append({**match, **fit, "voice_file": voice_file})
            voice_clips.append({"file": voice_file, "start_ms": cursor_ms})
            cursor_ms += int(duration_sec * 1000)

        JOBS[job_id]["progress"] = "Mixing audio"
        mixed_audio = AudioEngine.mix_tracks_with_ducking(
            voice_clips, output_path=os.path.join(work_dir, "mixed_audio.m4a")
        )

        JOBS[job_id]["progress"] = "Rendering scene segments"
        rendered_segments = []
        for i, seg in enumerate(segments):
            seg_file = os.path.join(work_dir, f"segment_{i:03d}.mp4")
            VideoCompositor.render_shorts_segment(
                video_path, seg["video_in"], seg["duration"], seg_file, hold_sec=seg["hold_sec"]
            )
            rendered_segments.append(seg_file)

        JOBS[job_id]["progress"] = "Generating subtitles"
        words = SubtitleEngine.transcribe(mixed_audio)
        ass_path = SubtitleEngine.generate_ass_subtitles(words, os.path.join(work_dir, "subs.ass"))

        JOBS[job_id]["progress"] = "Compositing final video"
        VideoCompositor.merge_and_finalize(rendered_segments, mixed_audio, ass_path, out_file)

        JOBS[job_id]["progress"] = "Validating final video"
        report = PreflightValidator.audit_video(out_file)

        # Gated Human-in-the-Loop Status
        default_title = req.title or f"BeamNG Physics Challenge #{job_id} #Shorts"
        default_desc = "Exciting car crash simulation and challenge! Watch till the end! #Shorts #BeamNG #Gaming"
        default_tags = ["Shorts", "BeamNG", "CarCrash", "Gaming", "Simulation"]

        JOBS[job_id]["status"] = "waiting_approval"
        JOBS[job_id]["progress"] = "Render complete. Waiting for user approval to upload."
        JOBS[job_id]["output_file"] = out_file
        JOBS[job_id]["suggested_title"] = default_title
        JOBS[job_id]["suggested_description"] = default_desc
        JOBS[job_id]["suggested_tags"] = default_tags
        JOBS[job_id]["report"] = report
        logger.info(f"Job {job_id} ready for review: {out_file}")

    except Exception as e:
        logger.exception(f"Job {job_id} failed: {e}")
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        JOBS[job_id]["progress"] = f"Error: {e}"

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "video-engine",
        "version": "1.1.0",
        "youtube_authenticated": uploader.is_authenticated()
    }

@app.post("/api/render")
def submit_render_job(req: RenderJobRequest):
    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": "Queued",
        "output_file": None,
        "suggested_title": None,
        "suggested_description": None,
        "suggested_tags": None,
        "youtube_url": None,
        "error": None,
        "report": None
    }
    executor.submit(run_render_pipeline, job_id, req)
    return {"job_id": job_id, "status": "pending", "message": "Render job queued"}

@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]

@app.get("/api/jobs")
def list_jobs():
    return {"jobs": list(JOBS.values())}

@app.post("/api/jobs/{job_id}/approve_upload")
def approve_upload(job_id: str, req: ApproveUploadRequest):
    """
    Explicit user approval gate.
    Triggers YouTube upload only when explicitly commanded.
    """
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = JOBS[job_id]
    if job["status"] != "waiting_approval" and job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot upload job with status '{job['status']}'. Job must be 'waiting_approval'."
        )

    out_file = job.get("output_file")
    if not out_file or not os.path.exists(out_file):
        raise HTTPException(status_code=400, detail="Rendered video file not found on disk.")

    title = req.title or job.get("suggested_title") or f"Shorts Video #{job_id}"
    description = req.description or job.get("suggested_description") or ""
    tags = req.tags or job.get("suggested_tags") or []

    job["status"] = "uploading"
    job["progress"] = "Uploading to YouTube Shorts..."

    try:
        res = uploader.upload_shorts(
            video_path=out_file,
            title=title,
            description=description,
            tags=tags,
            category_id=req.category_id,
            privacy_status=req.privacy_status
        )
        job["status"] = "completed"
        job["progress"] = "Published"
        job["youtube_url"] = res["url"]
        logger.info(f"Job {job_id} uploaded to YouTube: {res['url']}")
        return {
            "status": "success",
            "message": "Video uploaded successfully to YouTube",
            "youtube_url": res["url"],
            "video_id": res["video_id"],
            "privacy": res["privacy"]
        }
    except Exception as e:
        logger.exception(f"Upload failed for job {job_id}: {e}")
        job["status"] = "waiting_approval"
        job["error"] = f"Upload failed: {e}"
        job["progress"] = f"Upload error: {e}"
        raise HTTPException(status_code=500, detail=f"Upload error: {e}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
