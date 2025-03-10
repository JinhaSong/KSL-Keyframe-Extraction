import os
import sys

import numpy as np
from matplotlib import pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cfg.base import base_dir
from util.file import *
from util.elan import *
from model.keyframe_detection.changepoint_detect import extract_changepoint


def plot_data(metadata):
    plt.figure(figsize=(10, 5))

    norm_handtip_disp = metadata["norm_handtip_disp"]
    norm_ang_acc_disp_gauss_filtered = metadata["norm_ang_acc_disp_gauss_filtered"]
    norm_ang_acc_orin = metadata["norm_ang_acc_orin"]
    norm_ang_vel = metadata["norm_ang_vel"][:500]
    index = list(range(len(norm_ang_vel)))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(24, 12))

    # ax1.plot(index, norm_ang_acc_disp_gauss_filtered, color='green', label='Angular Acc')
    # ax1.scatter(metadata["strong_cp"], [norm_ang_acc_disp_gauss_filtered[i] for i in metadata["strong_cp"]], color='blue', marker='o', label='Changepoints')
    # ax1.set_title('Angular Acceleration')
    # ax1.set_xlabel('Frame Index')
    # ax1.set_ylabel('Normalized Values')
    # ax1.legend()
    # ax1.grid(True)

    strong_cp = [cp for cp in metadata["strong_cp"] if cp < 500]
    strong_cp_val = [norm_ang_vel[cp] for cp in strong_cp]

    ax2.plot(index, norm_ang_vel, color='orange', label='Angular Velocity')
    ax2.scatter(strong_cp, strong_cp_val, color='blue', marker='o', label='Changepoints')
    ax2.set_title('Angular Velocity')
    ax2.set_xlabel('Frame Index')
    ax2.set_ylabel('Normalized Values')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    return plt

def generate_keyframe_elan(eaf_path, tsconfig_path, video_path_A, csv_path_A, json_path_A, plt_path_A):
    metadata_A = extract_changepoint(json_path_A, min_thres=0.35, minor_thres=0.1, adj_local_thres=15, disp_sigma=3, acc_sigma=1.0, minor_max_thres=0.2, ang_acc_thres=2, pose_type="blazepose")
    # metadata_B = extract_changepoint(json_path_B, min_thres=0.35, minor_thres=0.1, adj_local_thres=15, disp_sigma=3, acc_sigma=1.0, minor_max_thres=0.2, ang_acc_thres=2, pose_type="blazepose")

    plt = plot_data(metadata_A)
    plt.savefig(plt_path_A)

    update_elan(eaf_path, csv_path_A, tsconfig_path, metadata_A["time_disp"], metadata_A["strong_cp"])
    # update_elan(eaf_path, csv_path_B, tsconfig_path, metadata_B["time_disp"], metadata_B["strong_cp"])
    save_csv_velacc(csv_path_A, metadata_A)
    # save_csv_velacc(csv_path_B, metadata_B)
    # save_tsconf_mulcsv(eaf_path, csv_path_A, csv_path_B)

    return

if __name__ == '__main__':
    root_dir = "C:/Users/JinhaSong/Documents/github/JinhaSong/KSLKeyframeExtraction/data/NIKL_Korean_Sign_Language_Annotated_Corpus_2024_v1.0/test"
    # root_dir = base_dir
    video_dir = os.path.join(root_dir, "MKV")
    elan_dir = os.path.join(root_dir, "ELAN")
    json_ak_dir = os.path.join(root_dir, "SKELETON")
    json_dir = os.path.join(root_dir, "SKELETON_BLAZEPOSE")

    # video_name = "5977.003.C.mkv"
    # video_path = os.path.join(video_dir, video_name)
    # json_path = os.path.join(json_dir, video_name.replace(".mkv", ".json"))
    # eaf_path = os.path.join(elan_dir, video_name.replace(".mkv", ".eaf"))
    # csv_path = os.path.join(elan_dir, video_name.replace(".mkv", ".csv"))
    # tsconfig_path = os.path.join(elan_dir, video_name.replace(".mkv", ".tsconfig"))
    # plt_path = os.path.join(elan_dir, video_name.replace(".mkv", ".png"))

    eaf_path = os.path.join(root_dir, "VDMT1524021007.eaf")
    tsconfig_path = os.path.join(root_dir, "VDMT1524021007_tsconf.xml")
    video_path_A = os.path.join(root_dir, "KSLSL10GLt.mp4")
    json_path_A = os.path.join(root_dir, "KSLSL10GLt.json")
    csv_path_A = os.path.join(root_dir, "VDMT1524021007.csv")
    plt_path_A = os.path.join(root_dir,  "KSLSL10GLt.png")

    generate_keyframe_elan(eaf_path, tsconfig_path, video_path_A, csv_path_A, json_path_A, plt_path_A)