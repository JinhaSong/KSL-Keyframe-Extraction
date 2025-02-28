import os
import csv
import json

def generate_file_paths(root_dir, mkv_filename):
    mkv_path = os.path.join(root_dir, "MKV", mkv_filename)
    json_path = os.path.join(root_dir, "SKELETON", mkv_filename.replace('.mkv','.json'))
    eaf_path = os.path.join(root_dir, "ELAN", mkv_filename.replace('.mkv', '.eaf'))
    csv_path = os.path.join(root_dir, "ELAN", mkv_filename.replace('.mkv', '.csv'))
    tsconfig_path = os.path.join(root_dir, "ELAN", mkv_filename.replace('.mkv', '_tsconf.xml'))

    return mkv_path, json_path, eaf_path, csv_path, tsconfig_path

def save_data_csv(csv_path, metadata):
    timeline = metadata['timeline']
    norm_handtip_disp = metadata['handtip_disp']
    norm_ang_acc = metadata['norm_ang_acc']
    try:
        time_disp = [list(x) for x in list(zip(timeline, norm_handtip_disp, norm_ang_acc))]

        with open(csv_path, 'w') as f:
            write = csv.writer(f)
            write.writerows(time_disp)

        return True
    except:
        print(f"ERROR: cannot save csv {os.path.basename(csv_path)})")
        return False

def save_csv_velacc(csv_path, metadata):
    timeline = metadata['timeline']
    norm_ang_acc_orin = metadata['norm_ang_acc_orin']
    norm_ang_vel = metadata['norm_ang_vel']
    try:
        time_disp = [list(x) for x in list(zip(timeline, norm_ang_acc_orin, norm_ang_vel))]

        with open(csv_path, 'w') as f:
            write = csv.writer(f)
            write.writerows(time_disp)

        return True
    except:
        print(f"ERROR: cannot save csv {os.path.basename(csv_path)})")
        return False

def open_json(file_name) :
    with open(file_name) as f:
        data = json.load(f)
    return data

def save_json(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except:
        print(f"ERROR: cannot save json {os.path.basename(file_path)}")