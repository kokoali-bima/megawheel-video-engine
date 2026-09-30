from core.scene_detector import SceneAnalyzer
import sys
scenes = SceneAnalyzer.detect_scenes(sys.argv[1], threshold=27.0, min_scene_len_sec=2.0)
for i, s in enumerate(scenes):
    print(f'Scene {i+1}: {s[0]:.2f} - {s[1]:.2f} (Dur: {s[1]-s[0]:.2f})')
