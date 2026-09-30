import os
from typing import List, Tuple
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector, AdaptiveDetector

class SceneAnalyzer:
    """Frame-accurate scene and action boundary detection."""
    
    @staticmethod
    def detect_scenes(
        video_path: str,
        threshold: float = 27.0,
        min_scene_len_sec: float = 1.0
    ) -> List[Tuple[float, float]]:
        """
        Detect scenes and return list of (start_sec, end_sec) tuples.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
            
        video = open_video(video_path)
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=int(video.frame_rate * min_scene_len_sec)))
        
        scene_manager.detect_scenes(video)
        scene_list = scene_manager.get_scene_list()
        
        results = []
        for scene in scene_list:
            start_sec = scene[0].get_seconds()
            end_sec = scene[1].get_seconds()
            results.append((start_sec, end_sec))
            
        return results
