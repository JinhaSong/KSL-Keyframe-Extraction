import os
import sys
import cv2
import json

from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.draw import draw_limb
from cfg.base import base_dir

def create_limb_video(video_path, json_path, output_path, data_type="azure_kinect"):
    with open(json_path, 'r') as file:
        data = json.load(file)

    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    writer = cv2.VideoWriter(output_path, fourcc, frame_rate, (frame_width, frame_height))

    if not cap.isOpened():
        print('Cannot open video file')
    else:
        index = 0
        while True:
            ret, frame = cap.read()
            if ret:
                joint_data = data['frames'][index]
                if joint_data['bodies']:
                    frame = draw_limb(frame, joint_data, data_type=data_type)

                writer.write(frame)
                index += 1
            else:
                break

        cap.release()
        writer.release()

if __name__ == '__main__':
    # data_type = "azure_kinect"
    data_type = "blazepose"
    # dir_name = 'SKELETON'
    dir_name = 'SKELETON_BLAZEPOSE'
    base_dir = "C:\\Users\\JinhaSong\\Documents\\github\\JinhaSong\\KSLKeyframeExtraction\\data\\NIKL_Korean_Sign_Language_Annotated_Corpus_2024_v1.0\\MP4, eaf\\VDMT1524021007"

    video_dir = os.path.join(base_dir, 'MKV')
    json_dir = os.path.join(base_dir, dir_name)
    output_dir = os.path.join(base_dir, 'SKELETON_VIDEO', data_type)
    os.makedirs(output_dir, exist_ok=True)

    video_names = os.listdir(video_dir)
    video_ext = ".mp4"

    for video_name in tqdm(video_names):
        # video_name = '2622.003.C.mkv'
        json_name = video_name.replace(video_ext, '.json')

        video_path = os.path.join(video_dir, video_name)
        json_path = os.path.join(json_dir, json_name)
        output_path = os.path.join(output_dir, video_name.replace(video_ext, '.mp4'))

        create_limb_video(video_path, json_path, output_path, data_type)