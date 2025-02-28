import os
import sys
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.keyframe_detection.fsc2 import *

def process_video(video_path, threshold):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    displacements = []
    frames = [frame]
    index = 0
    while True:
        print(f'\rframe: {index}', end="")
        ret, frame = cap.read()
        if not ret:
            break
        disp = calculate_angular_displacement(frames[-1], frame)
        displacements.append(disp)
        frames.append(frame)
        index = index + 1
    print()
    displacements = a_generator(displacements)
    smoothed_displacements = smooth_displacements(displacements)
    significant_frames = selector(smoothed_displacements, threshold)
    sequenced_frames = sequencer(significant_frames, displacements)
    final_frames = s_reduction(sequenced_frames, displacements)
    # final_frames = p_reduction(final_frames, video_path)

    cap.release()
    print(final_frames)
    # Plotting results
    plt.figure(figsize=(10, 5))
    plt.plot(smoothed_displacements, label='Angular Displacement')
    plt.scatter(final_frames, [smoothed_displacements[i] for i in final_frames], color='red', label='Keyframes')
    plt.title('Keyframe Extraction')
    plt.xlabel('Frame Index')
    plt.ylabel('Angular Displacement')
    plt.legend()
    plt.show()
    return final_frames


# Use the function
video_path = 'C:\\Users\\JinhaSong\\Documents\\drive\\Study\\803_ELAN_Keyframe_o1\\ELAN_TEST\\MKV\\2701.003.C.mkv'
threshold = 6.45  # Set your own threshold based on your data
keyframes = process_video(video_path, threshold=1)