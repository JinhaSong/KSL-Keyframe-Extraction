import numpy as np
import scipy.ndimage
import json
from scipy.signal import argrelmin, argrelmax

from util.file import save_data_csv, open_json


def min_max_norm_list(dataset):
    norm_list = list()
    if isinstance(dataset, list):
        min_value = min(dataset)
        max_value = max(dataset)

        for value in dataset:
            tmp = (value - min_value) / (max_value - min_value)
            norm_list.append(tmp)
    return norm_list

def min_max_norm(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

def cast_list(test_list, data_type):
    return list(map(data_type, test_list))

def extract_changepoint(json_path, min_thres=0.35, minor_thres=0.1, adj_local_thres=15, disp_sigma=1.0, acc_sigma=1.0, minor_max_thres=0.2, ang_acc_thres=2, pose_type="azure_kinect") :
    r_handtip, l_handtip = get_handtip_joint_data(json_path)
    strong_cp, weak_cp, handtip_disp, handtip_disp_gauss_filtered, norm_handtip_disp, ang_acc_orin, ang_vel, ang_acc_disp_gauss_filtered, ang_acc_local_max, norm_ang_acc = changepoint_detector(
        r_handtip,
        min_thres,
        minor_thres,
        adj_local_thres,
        disp_sigma,
        acc_sigma,
        minor_max_thres,
        ang_acc_thres,
        pose_type=pose_type
    )
    if pose_type=="blazepose":
        data = open_json(json_path)
        timeline = get_timeline_from_frameid(data)

        time_disp = [list(x) for x in list(zip(timeline, ang_vel, ang_acc_orin))]
    else:
        data = open_json(json_path)
        timeline = get_timeline_zero_start(data)

        time_disp = [list(x) for x in list(zip(timeline, norm_handtip_disp, norm_ang_acc))]


    metadata = {
        'timeline': timeline,
        'time_disp': time_disp,
        'strong_cp': strong_cp,
        'weak_cp': weak_cp,
        'handtip_disp': handtip_disp,
        'handtip_disp_gauss_filtered': handtip_disp_gauss_filtered,
        'ang_acc_orin': ang_acc_orin,
        'ang_acc_disp_gauss_filtered': ang_acc_disp_gauss_filtered,
        'ang_acc_local_max': ang_acc_local_max,
        'ang_vel': ang_vel,
        'norm_handtip_disp': norm_handtip_disp,
        'norm_handtip_dips_gauss_filtered': min_max_norm(handtip_disp_gauss_filtered),
        'norm_ang_acc_disp_gauss_filtered': min_max_norm(ang_acc_disp_gauss_filtered),
        'norm_ang_acc': norm_ang_acc,
        'norm_ang_acc_orin': min_max_norm(ang_acc_orin),
        'norm_ang_vel': min_max_norm(ang_vel),
    }
    return metadata

def get_timeline_zero_start(data) :
    timeline = []
    for i in range(len(data['frames'])):
        timeline.append(data['frames'][i]['timestamp_usec'])
        
    time_start = timeline[0] #; print(time_start)
    timeline = list(map(lambda i : i - time_start, timeline ))
    timeline = list(map(lambda i : int(i/1000), timeline))

    return timeline


def get_timeline_from_frameid(data, fps=30):
    timeline = []
    for i in range(len(data['frames'])):
        frame_time_seconds = data['frames'][i]["frame_id"] / fps
        timeline.append(frame_time_seconds)

    time_start = timeline[0]
    timeline = [int((time - time_start) * 1000) for time in timeline]

    return timeline

def get_handtip_joint_data(json_path, pose_type="azure_kinect"):
    data = open_json(json_path)

    jp_dict = {}
    for i in range(len(data['frames'])):
        jp_dict[i] = data['frames'][i]['bodies'][0]['joint_positions']
        print(jp_dict[i])

    jp_list=list(jp_dict.values())
    print(jp_list)
    jp_array=np.array(jp_list)

    if pose_type == "azure_kinect":
        r_handtip_joint_idx = 16
        # r_hand_joint_idx = 15
        # r_wrist_joint_idx = 14
        # r_elbow_joint_idx = 13
        # r_shoulder_joint_idx = 12
        # r_clavicle_joint_idx = 11

        l_handtip_joint_idx = 9
        # l_hand_joint_idx = 8
        # l_wrist_joint_idx = 7
        # l_elbow_joint_idx = 6
        # l_shoulder_joint_idx = 5
        # l_clavicle_joint_idx = 4

        # head_joint_idx = 26
        # spine_chest_joint_idx = 2

        r_handtip = jp_array[:,r_handtip_joint_idx,:]
        # r_hand = jp_array[:,r_hand_joint_idx,:]
        # r_wrist = jp_array[:,r_wrist_joint_idx,:]
        # r_elbow = jp_array[:,r_elbow_joint_idx,:]
        # r_shoulder = jp_array[:,r_shoulder_joint_idx,:]
        # r_clavicle = jp_array[:,r_clavicle_joint_idx,:]

        l_handtip = jp_array[:,l_handtip_joint_idx,:]
        # l_hand = jp_array[:,l_hand_joint_idx,:]
        # l_wrist = jp_array[:,l_wrist_joint_idx,:]
        # l_elbow = jp_array[:,l_elbow_joint_idx,:]
        # l_shoulder = jp_array[:,l_shoulder_joint_idx,:]
        # l_clavicle = jp_array[:,l_clavicle_joint_idx,:]

        # head = jp_array[:,head_joint_idx,:]
        # spine_chest = jp_array[:,spine_chest_joint_idx,:]
    elif pose_type == "blazepose":
        r_handtip_joint_idx = 20
        l_handtip_joint_idx = 19

        r_handtip = jp_array[:, r_handtip_joint_idx, :]
        l_handtip = jp_array[:, l_handtip_joint_idx, :]
    else:
        r_handtip = None
        l_handtip = None

    return r_handtip, l_handtip

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def calculate_ang_acc(vec_arr):
    ang_acc = []
    for i in range(len(vec_arr)):
        if i==0 or np.array_equal(vec_arr[i], (0, 0, 0)) or np.array_equal(vec_arr[i - 1], (0, 0, 0)):
            ang_acc.append(0)
        else:
            ang = angle_between(vec_arr[i], vec_arr[i - 1])
            ang_acc.append(ang)
    return ang_acc

def calculate_displacement_vector(j_arr, pose_type="blazepose"):
    disp_vec = []

    if pose_type == "azure_kinect":
        min_val = np.min(j_arr, axis=(0))
        max_val = np.max(j_arr, axis=(0))
        j_arr = (j_arr - min_val) / (max_val - min_val)

    for i in range(len(j_arr)):
        if i == 0:
            disp_vec.append(np.array([0, 0, 0]))
        else:
            disp_vector = j_arr[i] - j_arr[i-1]
            disp_vec.append(disp_vector)

    return disp_vec

def calculate_displacement(j_arr):
    disp = []
    for i in range(len(j_arr)):
        if i==0:
            disp.append(0)
        else:
            disp_vector = np.array([j_arr[i][0] - j_arr[i-1][0], j_arr[i][1] - j_arr[i-1][1], j_arr[i][2] - j_arr[i-1][2]])
            disp.append(np.linalg.norm(disp_vector))
    return disp

def find_min_max(vals, mms, thres):
    total_max_value = np.max(vals)
    last_min = None
    for (frame, kind) in mms:
        if kind =='min':
            last_min = frame
            continue
        if (kind=='max') and (vals[frame] > total_max_value*thres) and last_min:
            break
    return last_min

def find_zero(vals, start_frame):
    for i, v in enumerate(vals[start_frame:]):
        if v == 0:
            return i+start_frame

def calc_filtered_local_min(displacement_array, min_thres, minor_thres, adj_local_thres, minor_max_thres, verbose=False):
    displacement_local_min = argrelmin(displacement_array)[0]
    displacement_local_max = argrelmax(displacement_array)[0]

    max_value = np.max(displacement_array)
    if verbose: print('Maximum displacement:', max_value)

    if verbose: print('LocalMin:', displacement_local_min)
    displacement_local_min = remove_boundary(displacement_local_min, len(displacement_array))
    if verbose: print('LocalMin after removeBoundary:', displacement_local_min)

    displacement_local_min_minor_max_filtered = filter_minor_max(displacement_local_min, displacement_local_max, displacement_array, minor_max_thres)
    if verbose: print('Filtered at filterMinorMax:', np.setdiff1d(displacement_local_min, displacement_local_min_minor_max_filtered, assume_unique=True))
    if verbose: print('LocalMin after filterMinorMax:', displacement_local_min_minor_max_filtered)

    min_filter = displacement_array[displacement_local_min_minor_max_filtered] <= max_value * min_thres
    displacement_local_min_filtered = displacement_local_min_minor_max_filtered[min_filter]
    if verbose: print('LocalMin after min_filter', displacement_local_min_filtered)
    
    displacement_local_min_filtered = filter_minor_min(displacement_local_min_filtered, displacement_local_max, displacement_array, minor_thres, adj_local_thres)
    if verbose: print('LocalMin after filterMinorMin', displacement_local_min_filtered)

    weak_cp = np.setdiff1d(displacement_local_min_minor_max_filtered, displacement_local_min_filtered, assume_unique=True)
    return displacement_local_min_filtered, weak_cp

def find_adjacent_max_idxs(min_i, max_arr):
    for i in range(len(max_arr) - 1):
        if (max_arr[i] < min_i) and (min_i < max_arr[i + 1]):
            return (max_arr[i], max_arr[i + 1])
    return None

def remove_boundary(min_arr, data_length):
    bound = np.array([0, data_length-1])
    min = np.setdiff1d(min_arr, bound)

    return min

def filter_minor_max(min_arr, max_arr, val_arr, minor_max_thres, verbose=False):
    total_max = np.max(val_arr)
    thres = total_max * minor_max_thres

    new_min_arr = []
    for idx, minimum in enumerate(min_arr):
        maxes = find_adjacent_max_idxs(minimum, max_arr)
        if (maxes and (val_arr[maxes[0]] < thres) and (val_arr[maxes[1]] < thres)) \
            or (idx==0 and maxes == None) or (idx == len(min_arr) - 1 and maxes == None):
            adj_max_str = ''
            if maxes and verbose: adj_max_str = f', Adjacent Max Values:{val_arr[maxes[0]]}, {val_arr[maxes[1]]}'
            if verbose:print(f'filterMinorMax Min index:{minimum}'+adj_max_str)
        else:
            new_min_arr.append(minimum)

    first_adj_max_idxs = find_adjacent_max_idxs(new_min_arr[0], max_arr)
    if (first_adj_max_idxs == None) or (val_arr[first_adj_max_idxs[0]] < thres):
        new_min_arr.pop(0)

    last_adj_max_idxs = find_adjacent_max_idxs(new_min_arr[-1], max_arr)
    if (last_adj_max_idxs == None) or (val_arr[last_adj_max_idxs[1]] < thres):
        new_min_arr.pop()

    return np.array(new_min_arr)

def filter_minor_min(min_arr, max_arr, val_arr, thres, adj_local_thres, verbose=False):
    total_max = np.max(val_arr)
    thres = total_max * thres
    if verbose: print(f'Threshold_value:{thres}')
    new_min_arr = []
    for idx, minimum in enumerate(min_arr):
        minval = val_arr[minimum]
        maxes = find_adjacent_max_idxs(minimum, max_arr)
        l_min = None
        l_val = None
        if (idx > 0):
            l_min = min_arr[idx - 1]
            l_val = val_arr[l_min]
        
        r_min = None
        r_val = None
        if (idx < len(min_arr)-1):
            r_min = min_arr[idx + 1]
            r_val = val_arr[r_min]

        if maxes and ( ((val_arr[maxes[0]] - minval < thres) and (l_min) and (l_val <= minval) and (minimum - l_min < adj_local_thres))
            or ((val_arr[maxes[1]] - minval < thres) and (r_min) and (r_val <= minval) and (r_min - minimum < adj_local_thres))):
            if verbose: print(f'filterMinorMin Min index:{minimum}, Min Value:{minval}, Adjacent Max Values:{val_arr[maxes[0]]}, {val_arr[maxes[1]]}, Difference:{val_arr[maxes[0]] - minval}, {val_arr[maxes[1]] - minval}')
            if l_min and verbose:
                print(f'filterMinorMin left_min:{l_min}, left_minval:{l_val}, {l_val<=minval}, {(minimum - l_min < adj_local_thres)}')
            if r_min and verbose:
                print(f'filterMinorMin right_min:{r_min}, right_minval:{r_val}, {r_val<=minval}, {(r_min - minimum < adj_local_thres)}')
            continue
        else:
            new_min_arr.append(minimum)

    return np.array(new_min_arr)

def find_significant_maxs(min_arr, max_arr, val_arr):
    mins = [(i, 'min') for i in min_arr]
    maxs = [(i, 'max') for i in max_arr]
    mms = mins + maxs
    mms.sort(key=lambda element : element[0])
    new_max_arr = []

    sig_max = None
    sig_value = 0
    for (frame, kind) in mms:
        if kind =='min':
            if sig_max:
                new_max_arr.append(sig_max)
            sig_max = None
            sig_value = 0
        else:
            if sig_value <= val_arr[frame]:
                sig_max = frame
                sig_value = val_arr[frame]
    new_max_arr.append(sig_max)
    return new_max_arr

def find_closest(val, alist):
    diff = 10000
    closest = None
    for aaf in alist:
        new_diff = abs(val-aaf)
        if new_diff>diff:
            break
        else:
            closest = aaf
            diff = new_diff
    return closest

def calculate_velocity(positions, time_steps):
    velocities = np.linalg.norm(np.diff(positions, axis=0), axis=1) / np.diff(time_steps)
    velocities = np.insert(velocities, 0, 0)
    return velocities

def calculate_acceleration(velocities, time_steps):
    accelerations = np.diff(velocities) / np.diff(time_steps[:-1])
    accelerations = np.insert(accelerations, 0, accelerations[0])
    accelerations = np.append(accelerations, accelerations[-1])
    return accelerations


def find_changepoint_aug_acc(strong_cp, weak_cp , ang_acc_local_max, ang_acc_thres):
    weak2strong = []
    for weak in weak_cp:
        close_ang_acc_local_max = find_closest(weak, ang_acc_local_max)
        if abs(weak - close_ang_acc_local_max) <= ang_acc_thres:
            weak2strong.append(weak)
    if weak2strong:
        strong_cp = np.concatenate((strong_cp, weak2strong), axis=None)
        strong_cp.sort()
        weak_cp = np.setdiff1d(weak_cp, weak2strong, assume_unique=True)

    strong_cp = cast_list(list(strong_cp), int)
    weak_cp = cast_list(list(weak_cp), int)

    return strong_cp, weak_cp


def find_changepoint_velacc(velocities, accelerations, ratio=0.2):
    velocity_min_indices = argrelmin(velocities)[0]
    acceleration_max_indices = argrelmax(accelerations)[0]
    acceleration_min_indices = argrelmin(accelerations)[0]

    changepoints = []
    for v_min_idx in velocity_min_indices:
        # 가장 가까운 가속도 극대와 극소 인덱스 찾기
        nearest_max_idx = min(filter(lambda x: x > v_min_idx, acceleration_max_indices),
                              key=lambda x: abs(x - v_min_idx), default=None)
        nearest_min_idx = min(filter(lambda x: x > v_min_idx, acceleration_min_indices),
                              key=lambda x: abs(x - v_min_idx), default=None)

        if nearest_max_idx is None or nearest_min_idx is None:
            continue

        # 해당 구간의 가속도 최소값과 최대값 사이에서 ratio에 따른 가속도 값 계산
        acc_max = accelerations[nearest_max_idx]
        acc_min = accelerations[nearest_min_idx]
        target_acc_value = acc_min + (acc_max - acc_min) * ratio

        # 조건 확인: 속도 최소 지점의 가속도가 target_acc_value 이상이면 changepoint로 선정
        if accelerations[v_min_idx] >= target_acc_value:
            changepoints.append(v_min_idx)
    return changepoints, []

def changepoint_detector(handtip, min_thres=0.35, minor_thres=0.1, adj_local_thres=15, disp_sigma=1.0, acc_sigma=2.5, minor_max_thres=0.2, ang_acc_thres=2, pose_type="azure_kinect", fps=30):
    handtip_gauss_filtered = scipy.ndimage.gaussian_filter1d(handtip, disp_sigma, axis=0)
    handtip_disp = np.array(calculate_displacement(handtip_gauss_filtered))

    handtip_vector = calculate_displacement_vector(handtip_gauss_filtered, pose_type)
    frame_interval = 1 / fps
    time_steps = np.arange(0, len(handtip_vector) * frame_interval, frame_interval)
    ang_vel = calculate_velocity(handtip_vector, time_steps)
    ang_acc_orin = calculate_acceleration(ang_vel[:-1], time_steps)
    ang_acc_disp_gauss_filtered = scipy.ndimage.gaussian_filter1d(ang_acc_orin, acc_sigma)
    ang_acc_local_max = argrelmax(ang_acc_disp_gauss_filtered)[0]

    if pose_type=="azure_kinect":
        handtip_disp_gauss_filtered = scipy.ndimage.gaussian_filter1d(handtip_disp, disp_sigma)
        strong_cp, weak_cp = calc_filtered_local_min(handtip_disp_gauss_filtered, min_thres, minor_thres, adj_local_thres, minor_max_thres, False)
        strong_cp, weak_cp = find_changepoint_aug_acc(strong_cp, weak_cp , ang_acc_local_max, ang_acc_thres)
    elif pose_type=="blazepose":
        handtip_disp_gauss_filtered = handtip_disp
        strong_cp, weak_cp = find_changepoint_velacc(ang_vel, ang_acc_orin)
    else:
        handtip_disp_gauss_filtered = handtip_disp
        strong_cp, weak_cp = find_changepoint_velacc(ang_vel, ang_acc_orin)

    norm_handtip_disp = min_max_norm_list(list(handtip_disp))
    norm_ang_acc = min_max_norm_list(list(ang_acc_disp_gauss_filtered))

    return strong_cp, weak_cp, handtip_disp, handtip_disp_gauss_filtered, norm_handtip_disp, ang_acc_orin, ang_vel, ang_acc_disp_gauss_filtered, ang_acc_local_max, norm_ang_acc