import xml.etree.ElementTree as ET

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

    h = root.find("./TIER/[@TIER_ID='Change Points']")
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




def update_elan(eaf_path, csv_path, tsconfig_path, time_disp, changepoints):
    tree = ET.parse(eaf_path)
    root = tree.getroot()

    h = root.find("HEADER")
    media = ET.SubElement(h, "LINKED_FILE_DESCRIPTOR", attrib={"LINK_URL": csv_path})
    h = root.find("HEADER")
    media = ET.SubElement(h, "LINKED_FILE_DESCRIPTOR", attrib={"LINK_URL": tsconfig_path})

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

    h = root.find("./TIER/[@TIER_ID='Change Points']")
    for idx, val in enumerate(changepoints):
        annot_id = str(val) + "changepoint"
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