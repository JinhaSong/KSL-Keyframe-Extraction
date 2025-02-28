import cv2
import mediapipe as mp
from cfg.pose import azure_kinect as pose_ak
from cfg.pose import blazepose as pose_bp
from cfg.draw import azure_kinect_dk as draw

def draw_limb(image, joint_data, data_type="azure_kinect"):
    if data_type == "azure_kinect":
        image = draw_limb_azure_kinect(image, joint_data)
    elif data_type == "blazepose":
        image = draw_limb_blazepose(image, joint_data)
    else:
        image = draw_limb_azure_kinect(image, joint_data)
    return image

def draw_limb_azure_kinect(image, joint_data):
    body = joint_data['bodies'][0]
    joints = body['joint_positions']

    points = []
    for idx, position in enumerate(joints):
        x = int(position[0] * draw["scale_x"] + draw["offset_x"])
        y = int(position[1] * draw["scale_y"] + draw["offset_y"])
        points.append((x, y))
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)

    for start, end in pose_ak["pair"]:
        if start < len(points) and end < len(points):
            cv2.line(image, points[start], points[end], (255, 0, 0), 2)

    return image

def draw_limb_blazepose(image, joint_data):
    body = joint_data['bodies'][0]
    joints = body['joint_positions']

    points = []
    for idx, position in enumerate(joints):
        x = int(position[0] * image.shape[1])
        y = int(position[1] * image.shape[0])
        points.append((x, y))
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)  # 관절 그리기

    for start, end in pose_bp["pair"]:
        if start < len(points) and end < len(points):
            cv2.line(image, points[start], points[end], (255, 0, 0), 2)

    return image

