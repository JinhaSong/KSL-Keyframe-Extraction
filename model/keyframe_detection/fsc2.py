# Keyframe Extraction Algorithm for Continuous Sign-Language Videos Using Angular Displacement and Sequence Check Metrics

import cv2
import numpy as np


def calculate_angular_displacement(prev_frame, curr_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    return np.sum(angle)

# A-Generator: Aggregates angular displacements
def a_generator(displacements):
    return np.array(displacements)

# Selector: Identifies significant changes
def selector(displacements, threshold=0.01):  # 임계값 조정
    selected = [i for i, val in enumerate(displacements) if val > threshold]
    return selected

# Sequencer: Ensures temporal continuity among selected frames
def sequencer(selected_indices, displacements):
    return [idx for idx in selected_indices if displacements[idx] > np.mean(displacements)]

# S-Reduction: Further refines the selection by filtering isolated keyframes
def s_reduction(selected_frames, displacements):
    return [f for f in selected_frames if f > 0 and f < len(displacements) - 1
            and displacements[f] > displacements[f - 1] and displacements[f] > displacements[f + 1]]

# P-Reduction: Pixel-level refinement (optional for simplification here)
def p_reduction(frames, video_path):
    cap = cv2.VideoCapture(video_path)
    retained_frames = []
    last_frame = None
    for i, frame_idx in enumerate(sorted(frames)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            continue
        if last_frame is not None:
            diff = cv2.absdiff(last_frame, frame)
            if np.mean(diff) < 10:  # Example threshold
                retained_frames.append(frame_idx)
        last_frame = frame
    cap.release()
    return retained_frames

def smooth_displacements(displacements, window_size=10):
    smoothed = np.convolve(displacements, np.ones(window_size) / window_size, mode='valid')
    return np.concatenate([displacements[:window_size-1], smoothed])