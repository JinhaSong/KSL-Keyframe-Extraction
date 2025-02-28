import os
import sys

import numpy as np
from matplotlib import pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cfg.base import base_dir
from util.file import *
from util.elan import generate_init_eaf, generation_conf
from model.keyframe_detection.changepoint_detect import extract_changepoint


def min_max_norm(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

def plot_data(title, metadata_ak, metadata_bp):
    plt.figure(figsize=(10, 5))
    plt.title(title)

    # 데이터 추출 및 정규화
    norm_handtip_disp_ak = min_max_norm(metadata_ak["handtip_disp"])
    norm_ang_acc_disp_gauss_filtered_ak = min_max_norm(metadata_ak["ang_acc_disp_gauss_filtered"])
    norm_ang_acc_orin_ak = min_max_norm(metadata_ak["ang_acc_orin"])
    norm_ang_vel_ak = min_max_norm(metadata_ak["ang_vel"])

    norm_handtip_disp_bp = min_max_norm(metadata_bp["handtip_disp"])
    norm_ang_acc_disp_gauss_filtered_bp = min_max_norm(metadata_bp["ang_acc_disp_gauss_filtered"])
    norm_ang_acc_orin_bp = min_max_norm(metadata_bp["ang_acc_orin"])
    norm_ang_vel_bp = min_max_norm(metadata_bp["ang_vel"])

    index_ak = list(range(len(norm_handtip_disp_ak)))
    index_bp = list(range(len(norm_handtip_disp_bp)))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))  # 두 개의 서브플롯 생성
    fig.suptitle(title)

    # ax1.plot(index_ak, norm_handtip_disp_ak, color='red', label='Handtip Displacement AK')
    # ax1.plot(index_ak, norm_ang_acc_disp_gauss_filtered_ak, color='green', label='Gaussian Filtered Angular Acc AK')
    ax1.plot(index_ak, norm_ang_acc_orin_ak, color='blue', label='Original Angular Acc AK')
    ax1.plot(index_ak, norm_ang_vel_ak, color='orange', label='Angular Velocity AK')
    ax1.scatter(metadata_ak["strong_cp"], [norm_ang_acc_orin_ak[i] for i in metadata_ak["strong_cp"]], color='blue', marker='o', label='Strong Changepoints AK')
    ax1.set_title('AK Data Normalized')
    ax1.set_xlabel('Frame Index')
    ax1.set_ylabel('Normalized Values')
    ax1.legend()
    ax1.grid(True)

    # ax2.plot(index_bp, norm_handtip_disp_bp, color='red', label='Handtip Displacement BP')
    ax2.plot(index_bp, norm_ang_acc_disp_gauss_filtered_bp, color='green', label='Gaussian Filtered Angular Acc BP')
    # ax2.plot(index_bp, norm_ang_acc_orin_bp, color='blue', label='Original Angular Acc BP')
    ax2.plot(index_bp, norm_ang_vel_bp, color='orange', label='Angular Velocity BP')
    ax2.scatter(metadata_bp["strong_cp"], [norm_ang_acc_disp_gauss_filtered_bp[i] for i in metadata_bp["strong_cp"]], color='blue', marker='x', label='Strong Changepoints BP')
    ax2.set_title('BP Data Normalized')
    ax2.set_xlabel('Frame Index')
    ax2.set_ylabel('Normalized Values')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # 서브플롯 간격 조정
    plt.show()

def generate_keyframe_elan(video_path, eaf_path, csv_path, tsconfig_path, json_ak_path, json_bp_path):
    metadata_ak = extract_changepoint(json_ak_path,  min_thres=0.35, minor_thres=0.1, adj_local_thres=15, disp_sigma=1.0, acc_sigma=1.0, minor_max_thres=0.2, ang_acc_thres=2, pose_type="azure_kinect")
    metadata_bp = extract_changepoint(json_bp_path, min_thres=0.35, minor_thres=0.1, adj_local_thres=15, disp_sigma=3, acc_sigma=1.0, minor_max_thres=0.2, ang_acc_thres=2, pose_type="blazepose")

    # plot_data_with_changepoints('Handtip Displacement', metadata_ak, metadata_bp)
    plot_data('Angular Acceleration', metadata_ak, metadata_bp)

    print("azure_kinect", metadata_ak["strong_cp"], metadata_ak["weak_cp"])
    print("blazepose", metadata_bp["strong_cp"], metadata_bp["weak_cp"])

    # generate_init_eaf(mkv_path, eaf_path, csv_path, tsconfig_path, metadata, method='changepoint')
    # save_data_csv(csv_path, metadata)
    # generation_conf(eaf_path, csv_path)

    return

if __name__ == '__main__':
    root_dir = base_dir
    video_dir = os.path.join(root_dir, "MKV")
    elan_dir = os.path.join(root_dir, "ELAN")
    json_ak_dir = os.path.join(root_dir, "SKELETON")
    json_bp_dir = os.path.join(root_dir, "SKELETON_BLAZEPOSE")

    video_name = "5977.003.C.mkv"
    video_path = os.path.join(video_dir, video_name)
    json_ak_path = os.path.join(json_ak_dir, video_name.replace(".mkv", ".json"))
    json_bp_path = os.path.join(json_bp_dir, video_name.replace(".mkv", ".json"))
    eaf_path = os.path.join(elan_dir, video_name.replace(".mkv", ".eaf"))
    csv_path = os.path.join(elan_dir, video_name.replace(".mkv", ".csv"))
    tsconfig_path = os.path.join(elan_dir, video_name.replace(".mkv", ".tsconfig"))

    generate_keyframe_elan(video_path, eaf_path,  csv_path, tsconfig_path, json_ak_path, json_bp_path)