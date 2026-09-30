import cv2, os, json, base64

def extract_frames_for_ai(video_path: str, interval_sec: int = 2):
    print(f'Mengekstrak frame dari {video_path} setiap {interval_sec} detik...')
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval_sec)
    frames_data = []
    frame_count = 0
    success, frame = cap.read()
    while success and len(frames_data) < 5:
        if frame_count % frame_interval == 0:
            timestamp = frame_count / fps
            frame_resized = cv2.resize(frame, (640, 360))
            _, buffer = cv2.imencode('.jpg', frame_resized)
            print(f'[+] Frame diekstrak pada detik {timestamp:.2f}')
            frames_data.append(timestamp)
        success, frame = cap.read()
        frame_count += 1
    cap.release()
    print('\n[SIMULASI AI] Mengirim frame ke Gemini Vision API...')
    print('Hasil Analisis AI (Simulasi Prototype):')
    mock_ai_result = [
        {'timestamp': 0.0, 'car': 'Blue Bus', 'status': 'Melaju'},
        {'timestamp': 2.0, 'car': 'Blue Bus', 'status': 'Terbang/Jatuh'},
        {'timestamp': 4.0, 'car': 'Blue Bus', 'status': 'Hancur/Menabrak'}
    ]
    print(json.dumps(mock_ai_result, indent=2))
    print('\n>>> Skrip otomatis memicu efek suara FAIL tepat di detik 4.0!')
    
if __name__ == '__main__':
    extract_frames_for_ai('/root/.gemini/antigravity-cli/scratch/raw_materials/Physics_Gaming/2026-09-25/beamng_test.mp4')
