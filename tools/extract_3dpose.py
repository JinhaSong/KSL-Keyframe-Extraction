import os
import sys
import cv2
import json
import mediapipe as mp
from tqdm import tqdm

from tools.test_fsc2 import video_path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cfg.base import base_dir
from util.file import save_json


def process_video(video_path, json_path, pose_model):
    cap = cv2.VideoCapture(video_path)
    output_json = {"frames": []}

    index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        else:
            try:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame.flags.writeable = False
                results = pose_model.process(frame)

                frame_data = {
                    "bodies": [{
                        "body_id": 1,
                        "confidence_level": [],
                        "joint_positions": [],
                        "joint_orientations": []
                    }],
                    "frame_id": index,
                    "num_bodies": 1 if results.pose_landmarks else 0,
                    "timestamp_usec": int(cv2.getTickCount() / cv2.getTickFrequency() * 1e6)
                }
                if results.pose_landmarks:
                    for landmark in results.pose_landmarks.landmark:
                        frame_data["bodies"][0]["joint_positions"].append([
                            landmark.x,
                            landmark.y,
                            landmark.z
                        ])

                output_json["frames"].append(frame_data)
            except:
                print(video_path, os.path.exists(video_path), cap.isOpened(), ret, index)

            index += 1

    save_json(json_path, output_json)
    cap.release()


if __name__ == '__main__':
    mp_pose = mp.solutions.pose
    pose_model = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=2)

    base_dir = "C:\\Users\\JinhaSong\\Documents\\github\\JinhaSong\\KSLKeyframeExtraction\\data\\NIKL_Korean_Sign_Language_Annotated_Corpus_2024_v1.0\\MP4, eaf\\VDMT1524021007"
    video_dir = os.path.join(base_dir, 'MKV')
    video_ext = ".mkv"
    output_dir = os.path.join(base_dir, 'SKELETON_BLAZEPOSE')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_names = os.listdir(video_dir)
    video_paths = sorted([os.path.join(video_dir, video_name) for video_name in os.listdir(video_dir)])
    json_paths = sorted([os.path.join(output_dir, video_name.replace(video_ext, ".json")) for video_name in os.listdir(video_dir)])

    for i, video_path in tqdm(enumerate(video_paths), total=len(video_paths)):
        process_video(video_path, json_paths[i], pose_model)


