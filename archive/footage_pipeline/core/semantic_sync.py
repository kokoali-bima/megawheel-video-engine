import os
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
from fastembed import TextEmbedding, ImageEmbedding

class SemanticSyncEngine:
    """CLIP-based semantic alignment of narration sentences to detected video scenes."""

    TEXT_MODEL = "Qdrant/clip-ViT-B-32-text"
    IMAGE_MODEL = "Qdrant/clip-ViT-B-32-vision"
    # Default fastembed cache_dir falls back to a tempfile.gettempdir() path, which is
    # /tmp here -- tmpfs, wiped on every reboot. Pin it under /root so the ~580MB CLIP
    # weights survive a restart instead of forcing a slow re-download on the next job.
    CACHE_DIR = os.path.expanduser("~/.cache/fastembed")

    _text_model = None
    _image_model = None

    @classmethod
    def get_text_model(cls) -> TextEmbedding:
        if cls._text_model is None:
            cls._text_model = TextEmbedding(model_name=cls.TEXT_MODEL, cache_dir=cls.CACHE_DIR)
        return cls._text_model

    @classmethod
    def get_image_model(cls) -> ImageEmbedding:
        if cls._image_model is None:
            cls._image_model = ImageEmbedding(model_name=cls.IMAGE_MODEL, cache_dir=cls.CACHE_DIR)
        return cls._image_model

    @staticmethod
    def extract_scene_thumbnail(video_path: str, start_sec: float, end_sec: float, output_file: str) -> str:
        """Grab a single representative frame from the midpoint of a scene."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Video not found: {video_path}")

        midpoint = start_sec + (end_sec - start_sec) / 2
        cap.set(cv2.CAP_PROP_POS_MSEC, midpoint * 1000)
        ok, frame = cap.read()
        cap.release()
        if not ok:
            raise RuntimeError(f"Could not read frame at {midpoint:.2f}s from {video_path}")

        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        cv2.imwrite(output_file, frame)
        return output_file

    @classmethod
    def embed_scenes(
        cls,
        video_path: str,
        scenes: List[Tuple[float, float]],
        thumb_dir: str = "/tmp/scene_thumbs"
    ) -> np.ndarray:
        """Extract one thumbnail per scene and return their CLIP image embeddings."""
        thumbs = [
            cls.extract_scene_thumbnail(video_path, start, end, os.path.join(thumb_dir, f"scene_{i:03d}.jpg"))
            for i, (start, end) in enumerate(scenes)
        ]
        model = cls.get_image_model()
        return np.array(list(model.embed(thumbs)))

    @classmethod
    def embed_sentences(cls, sentences: List[str]) -> np.ndarray:
        """Return CLIP text embeddings for each narration sentence."""
        model = cls.get_text_model()
        return np.array(list(model.embed(sentences)))

    @staticmethod
    def align_monotonic(similarity: np.ndarray) -> List[int]:
        """
        Assign each sentence (row) to a scene (column) preserving footage order --
        sentence i+1 is never assigned to an earlier scene than sentence i. This fits
        a fixed-timeline source (one gameplay/dashcam video) where narration must
        follow the action as it actually happens, not a free B-roll pick.
        similarity: [n_sentences, n_scenes] cosine similarity matrix.
        Returns scene index per sentence.
        """
        n, m = similarity.shape
        if n == 0 or m == 0:
            raise ValueError("Need at least one sentence and one scene to align")

        dp = np.full((n, m), -np.inf)
        back = np.zeros((n, m), dtype=int)
        dp[0] = similarity[0]

        for i in range(1, n):
            best_score, best_j = -np.inf, 0
            for j in range(m):
                if dp[i - 1, j] > best_score:
                    best_score, best_j = dp[i - 1, j], j
                dp[i, j] = best_score + similarity[i, j]
                back[i, j] = best_j

        path = [int(np.argmax(dp[-1]))]
        for i in range(n - 1, 0, -1):
            path.append(back[i, path[-1]])
        path.reverse()
        return path

    @classmethod
    def sync_narration_to_scenes(
        cls,
        video_path: str,
        scenes: List[Tuple[float, float]],
        sentences: List[str],
        thumb_dir: str = "/tmp/scene_thumbs"
    ) -> List[Dict[str, Any]]:
        """
        Match each narration sentence to the scene it best describes, in footage order.
        Returns a list aligned with `sentences`: sentence, scene_index, scene_start,
        scene_end, score.
        """
        scene_vecs = cls.embed_scenes(video_path, scenes, thumb_dir)
        sentence_vecs = cls.embed_sentences(sentences)

        scene_norms = scene_vecs / np.linalg.norm(scene_vecs, axis=1, keepdims=True)
        sentence_norms = sentence_vecs / np.linalg.norm(sentence_vecs, axis=1, keepdims=True)
        similarity = sentence_norms @ scene_norms.T

        scene_indices = cls.align_monotonic(similarity)

        results = []
        for i, scene_idx in enumerate(scene_indices):
            start, end = scenes[scene_idx]
            results.append({
                "sentence": sentences[i],
                "scene_index": scene_idx,
                "scene_start": start,
                "scene_end": end,
                "score": float(similarity[i, scene_idx])
            })
        return results

    @staticmethod
    def fit_scene_to_duration(
        scene_start: float,
        scene_end: float,
        target_duration_sec: float,
        hold_last_frame: bool = True
    ) -> Dict[str, float]:
        """
        Fit a matched scene's timing to a narration segment's exact TTS duration.
        Trims to the scene's centered window if it's longer than needed. If it's
        shorter, reports a hold_sec to freeze the last frame (see
        VideoCompositor.render_shorts_segment's hold_sec) rather than speed-ramping
        unrelated footage, which looks wrong more often than a freeze does.
        """
        scene_len = scene_end - scene_start
        if scene_len >= target_duration_sec:
            trim_in = scene_start + (scene_len - target_duration_sec) / 2
            return {"video_in": trim_in, "duration": target_duration_sec, "hold_sec": 0.0}

        hold_sec = target_duration_sec - scene_len if hold_last_frame else 0.0
        return {"video_in": scene_start, "duration": scene_len, "hold_sec": hold_sec}
