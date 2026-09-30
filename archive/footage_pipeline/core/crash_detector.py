import cv2
import numpy as np
import sys

def detect_crash_timestamp(video_path, start_time, duration):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
    
    max_diff = 0
    crash_time = start_time
    
    ret, prev_frame = cap.read()
    if not ret: return crash_time
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    current_time = start_time
    end_time = start_time + duration
    
    # We ignore the first second to avoid scene-cut flashes
    ignore_until = start_time + 1.0 
    
    while current_time < end_time:
        ret, frame = cap.read()
        if not ret: break
        
        current_time += 1.0 / fps
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference between consecutive frames
        diff = cv2.absdiff(prev_gray, gray)
        non_zero_count = np.count_nonzero(diff > 30) # threshold for significant change
        
        if current_time > ignore_until and non_zero_count > max_diff:
            max_diff = non_zero_count
            crash_time = current_time
            
        prev_gray = gray
        
    cap.release()
    return crash_time

def detect_finish_timestamp(video_path, start_time, duration, settle_threshold=8000):
    """
    Find when a run actually finishes: the last sustained drop into low motion
    within the window (vehicle landed/stopped), rather than the single biggest
    spike detect_crash_timestamp looks for -- for a successful run that spike is
    usually the launch, which is too early to call a winner.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)

    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        return start_time + duration
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    current_time = start_time
    end_time = start_time + duration
    samples = []

    while current_time < end_time:
        ret, frame = cap.read()
        if not ret: break

        current_time += 1.0 / fps
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(prev_gray, gray)
        non_zero_count = np.count_nonzero(diff > 30)
        samples.append((current_time, non_zero_count))

        prev_gray = gray

    cap.release()

    if not samples:
        return end_time

    # Scan backwards from the end: keep the earliest timestamp after which
    # motion never rises back above the settle threshold.
    settle_from = samples[-1][0]
    for t, motion in reversed(samples):
        if motion > settle_threshold:
            break
        settle_from = t

    return settle_from

if __name__ == '__main__':
    video = '/root/.gemini/antigravity-cli/scratch/raw_materials/Physics_Gaming/2026-09-25/beamng_test.mp4'
    # Test Scene 1: Orange Buggy (Start 176.65, Dur 15.0)
    print('Scanning Scene 1 (Orange Buggy)...')
    crash1 = detect_crash_timestamp(video, 176.65, 15.0)
    print(f'Detected Crash 1 at: {crash1:.2f}s (Relative: {crash1 - 176.65:.2f}s)')
    
    # Test Scene 2: Blue Sedan (Start 203.45, Dur 14.0)
    print('Scanning Scene 2 (Blue Sedan)...')
    crash2 = detect_crash_timestamp(video, 203.45, 14.0)
    print(f'Detected Crash 2 at: {crash2:.2f}s (Relative: {crash2 - 203.45:.2f}s)')

    # Test Scene 3: Monster Truck (Start 221.38, Dur 18.0)
    print('Scanning Scene 3 (Monster Truck)...')
    crash3 = detect_crash_timestamp(video, 221.38, 18.0)
    print(f'Detected Peak Action 3 at: {crash3:.2f}s (Relative: {crash3 - 221.38:.2f}s)')
