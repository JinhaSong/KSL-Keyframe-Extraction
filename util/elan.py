import os
import csv
import xml.etree.ElementTree as ET

import pympi

from cfg.base import init_tsconf_path, init_pfsx_path, init_eaf_path


def generate_init_eaf(mkv_path, eaf_path, csv_path, tsconfig_path, metadata, method='changepoint'):
    if method == 'changepoint':
        generate_init_eaf_changepoint(mkv_path, eaf_path, csv_path, tsconfig_path, metadata['strong_cp'], metadata['weak_cp'], metadata['time_disp'])
    else:
        pass

def generate_init_eaf_changepoint(mkv_file, eaf_path, csv_path, tsconfig_path, strong_cp, weak_cp, time_disp):
    tree = ET.parse(init_eaf_path)
    root = tree.getroot()

    mkv_path = "file:///" + mkv_file
    csv_path = "file:///" + csv_path
    tsconfig_path = "file:///" + tsconfig_path
    eaf_file = eaf_path

    h = root.find("HEADER")
    media = ET.SubElement(h, "MEDIA_DESCRIPTOR", attrib={"MEDIA_URL": mkv_path})
    h = root.find("HEADER")
    media = ET.SubElement(h, "LINKED_FILE_DESCRIPTOR", attrib={"LINK_URL": csv_path})
    h = root.find("HEADER")
    media = ET.SubElement(h, "LINKED_FILE_DESCRIPTOR", attrib={"LINK_URL": tsconfig_path})

    h = root.find("TIME_ORDER")
    timelist = [row[0] for row in time_disp]
    for idx, val in enumerate(strong_cp):
        if (timelist[val] > 70):
            timevalue_start = timelist[val] - 60
        else:
            timevalue_start = 0
        timeslotid_start = str(val) + "S"
        timevalue_end = timelist[val]
        timeslotid_end = str(val) + "E"

        timeorder = ET.SubElement(h, "TIME_SLOT", dict(TIME_SLOT_ID=timeslotid_start, TIME_VALUE=str(timevalue_start)))
        timeorder = ET.SubElement(h, "TIME_SLOT", dict(TIME_SLOT_ID=timeslotid_end, TIME_VALUE=str(timevalue_end)))

    for idx, val in enumerate(weak_cp):
        if (timelist[val] > 70):
            timevalue_start = timelist[val] - 60
        else:
            timevalue_start = 0
        timeslotid_start = str(val) + "S"
        timevalue_end = timelist[val]
        timeslotid_end = str(val) + "E"

        timeorder = ET.SubElement(h, "TIME_SLOT", dict(TIME_SLOT_ID=timeslotid_start, TIME_VALUE=str(timevalue_start)))
        timeorder = ET.SubElement(h, "TIME_SLOT", dict(TIME_SLOT_ID=timeslotid_end, TIME_VALUE=str(timevalue_end)))

    h = root.find("./TIER/[@TIER_ID='Changepoint']")
    for idx, val in enumerate(strong_cp):
        annot_id = str(val) + "strong"
        timeslot_ref1 = str(val) + "S"
        timeslot_ref2 = str(val) + "E"
        annot = ET.SubElement(h, "ANNOTATION")
        alignable = ET.SubElement(annot, "ALIGNABLE_ANNOTATION",
                                  dict(ANNOTATION_ID=annot_id, TIME_SLOT_REF1=timeslot_ref1,
                                       TIME_SLOT_REF2=timeslot_ref2))
        anntval = ET.SubElement(alignable, "ANNOTATION_VALUE")
        anntval.text = annot_id

    for idx, val in enumerate(weak_cp):
        annot_id = str(val) + "weak"
        timeslot_ref1 = str(val) + "S"
        timeslot_ref2 = str(val) + "E"
        annot = ET.SubElement(h, "ANNOTATION")
        alignable = ET.SubElement(annot, "ALIGNABLE_ANNOTATION",
                                  dict(ANNOTATION_ID=annot_id, TIME_SLOT_REF1=timeslot_ref1,
                                       TIME_SLOT_REF2=timeslot_ref2))
        anntval = ET.SubElement(alignable, "ANNOTATION_VALUE")
        anntval.text = annot_id

    # ET.indent(tree, '   ')
    final = ET.ElementTree(root)
    final.write(eaf_file)

def save_eaf(eaf_path, csv_path, tsconfig_path, time_disp, changepoints):
    tree = ET.parse(eaf_path)
    root = tree.getroot()

    h = root.find("HEADER")
    media = ET.SubElement(h, "LINKED_FILE_DESCRIPTOR", attrib={"LINK_URL": "file://" + csv_path})
    h = root.find("HEADER")
    media = ET.SubElement(h, "LINKED_FILE_DESCRIPTOR", attrib={"LINK_URL": "file://" + tsconfig_path})

    h = root.find("TIME_ORDER")
    timelist = [row[0] for row in time_disp]
    for idx, val in enumerate(changepoints):
        if (timelist[val] > 70):
            timevalue_start = timelist[val] - 60
        else:
            timevalue_start = 0
        timeslotid_start = str(val) + "S"
        timevalue_end = timelist[val]
        timeslotid_end = str(val) + "E"

        timeorder = ET.SubElement(h, "TIME_SLOT", dict(TIME_SLOT_ID=timeslotid_start, TIME_VALUE=str(timevalue_start)))
        timeorder = ET.SubElement(h, "TIME_SLOT", dict(TIME_SLOT_ID=timeslotid_end, TIME_VALUE=str(timevalue_end)))

    h = root.find("./TIER/[@TIER_ID='Changepoint']")
    for idx, val in enumerate(changepoints):
        annot_id = str(val) + "strong"
        timeslot_ref1 = str(val) + "S"
        timeslot_ref2 = str(val) + "E"
        annot = ET.SubElement(h, "ANNOTATION")
        alignable = ET.SubElement(annot, "ALIGNABLE_ANNOTATION",
                                  dict(ANNOTATION_ID=annot_id, TIME_SLOT_REF1=timeslot_ref1,
                                       TIME_SLOT_REF2=timeslot_ref2))
        anntval = ET.SubElement(alignable, "ANNOTATION_VALUE")
        anntval.text = annot_id

    # ET.indent(tree, '   ')
    final = ET.ElementTree(root)
    final.write(eaf_path)


def update_elan(eaf_path, csv_path, tsconfig_path, time_disp, changepoints):
    eaf = pympi.Elan.Eaf(eaf_path)

    for linked_file in eaf.get_linked_files():
        if 'csv' in linked_file:
            eaf.remove_linked_file(linked_file)
        if 'tsconf' in linked_file:
            eaf.remove_linked_file(linked_file)
    eaf.add_linked_file(csv_path, relpath='./', mimetype='text/csv')
    eaf.add_linked_file(tsconfig_path, relpath='./', mimetype='application/xml')

    # 시간 슬롯과 티어 설정
    if 'Changepoint' in eaf.get_tier_names():
        eaf.remove_tier('Changepoint')
    eaf.add_tier('Changepoint')

    # Add timeslots and annotations for changepoints
    for cp in changepoints:
        start_time = time_disp[cp] - 1000 if cp > 3 else 0  # Adjust start time
        end_time = time_disp[cp]
        start_ts = eaf.add_time_slot(start_time)
        end_ts = eaf.add_time_slot(end_time)
        eaf.add_annotation('Changepoint', start_ts, end_ts, value=f'CP{cp}')

    # 파일 저장
    eaf.to_file(eaf_path.replace('.eaf', '_updated.eaf'))
def save_tsconf(eaf_path, csv_path):
    tsconfig_file = eaf_path.replace('.eaf', "_tsconf.xml")

    tree = ET.parse(init_tsconf_path)
    root = tree.getroot()

    h = root.find("tracksource")
    h.set('source-url', "file:///" + csv_path)
    final = ET.ElementTree(root)
    final.write(tsconfig_file)

    pfsx_file = eaf_path.replace('.eaf', ".pfsx")
    tree = ET.parse(init_pfsx_path)
    root = tree.getroot()
    final = ET.ElementTree(root)
    final.write(pfsx_file)

    return

def save_tsconf_mulcsv(eaf_path, csv_path_A, csv_path_B):
    tsconfig_file = eaf_path.replace('.eaf', "_tsconf.xml")

    tree = ET.parse(init_tsconf_path)
    root = tree.getroot()

    h = root.find("tracksource")
    h.set('source-url', "file:///" + csv_path_A)
    h.set('source-url', "file:///" + csv_path_B)
    final = ET.ElementTree(root)
    final.write(tsconfig_file)

    pfsx_file = eaf_path.replace('.eaf', ".pfsx")
    tree = ET.parse(init_pfsx_path)
    root = tree.getroot()
    final = ET.ElementTree(root)
    final.write(pfsx_file)

    return

def generate_file_paths(root_dir, mkv_filename):
    mkv_path = os.path.join(root_dir, "MKV", mkv_filename)
    json_path = os.path.join(root_dir, "SKELETON", mkv_filename.replace('.mkv','.json'))
    eaf_path = os.path.join(root_dir, "ELAN", mkv_filename.replace('.mkv', '.eaf'))
    csv_path = os.path.join(root_dir, "ELAN", mkv_filename.replace('.mkv', '.csv'))
    tsconfig_path = os.path.join(root_dir, "ELAN", mkv_filename.replace('.mkv', '_tsconfig.xml'))

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
