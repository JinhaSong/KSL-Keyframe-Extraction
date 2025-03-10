import os
import csv
import json



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