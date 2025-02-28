azure_kinect = {
    "joint": {
        0: "PELVIS",
        1: "SPINE_NAVEL",
        2: "SPINE_CHEST",
        3: "NECK",
        4: "CLAVICLE_LEFT",
        5: "SHOULDER_LEFT",
        6: "ELBOW_LEFT",
        7: "WRIST_LEFT",
        8: "HAND_LEFT",
        9: "HANDTIP_LEFT",
        10: "THUMB_LEFT",
        11: "CLAVICLE_RIGHT",
        12: "SHOULDER_RIGHT",
        13: "ELBOW_RIGHT",
        14: "WRIST_RIGHT",
        15: "HAND_RIGHT",
        16: "HANDTIP_RIGHT",
        17: "THUMB_RIGHT",
        18: "HIP_LEFT",
        19: "KNEE_LEFT",
        20: "ANKLE_LEFT",
        21: "FOOT_LEFT",
        22: "HIP_RIGHT",
        23: "KNEE_RIGHT",
        24: "ANKLE_RIGHT",
        25: "FOOT_RIGHT",
        26: "HEAD",
        27: "NOSE",
        28: "EYE_LEFT",
        29: "EAR_LEFT",
        30: "EYE_RIGHT",
        31: "EAR_RIGHT",
    },
    "pair": [
        (0, 1), (1, 2), (2, 3),  # Spine
        (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (8, 10),  # Left arm + fingers
        (3, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (15, 17),  # Right arm + fingers
        (0, 18), (18, 19), (19, 20), (20, 21),  # Left leg
        (0, 22), (22, 23), (23, 24), (24, 25) , # Right leg
        (3, 26), (26, 27), (27, 28), (27, 30), (28, 29), (30, 31)
    ]
}

blazepose = {
    "joint": {
        0: "NOSE",
        1: "LEFT_EYE_INNER",
        2: "LEFT_EYE",
        3: "LEFT_EYE_OUTER",
        4: "RIGHT_EYE_INNER",
        5: "RIGHT_EYE",
        6: "RIGHT_EYE_OUTER",
        7: "LEFT_EAR",
        8: "RIGHT_EAR",
        9: "MOUTH_LEFT",
        10: "MOUTH_RIGHT",
        11: "LEFT_SHOULDER",
        12: "RIGHT_SHOULDER",
        13: "LEFT_ELBOW",
        14: "RIGHT_ELBOW",
        15: "LEFT_WRIST",
        16: "RIGHT_WRIST",
        17: "LEFT_PINKY",
        18: "RIGHT_PINKY",
        19: "LEFT_INDEX",
        20: "RIGHT_INDEX",
        21: "LEFT_THUMB",
        22: "RIGHT_THUMB",
        23: "LEFT_HIP",
        24: "RIGHT_HIP",
        25: "LEFT_KNEE",
        26: "RIGHT_KNEE",
        27: "LEFT_ANKLE",
        28: "RIGHT_ANKLE",
        29: "LEFT_HEEL",
        30: "RIGHT_HEEL",
        31: "LEFT_FOOT_INDEX",
        32: "RIGHT_FOOT_INDEX"
    },
    "pair": [
        (0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6),  # Eyes
        (7, 8),  # Ears
        (9, 10),  # Mouth
        (11, 12),  # Shoulders
        (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),  # Left arm
        (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),  # Right arm
        (23, 24),  # Hips
        (23, 25), (25, 27), (27, 29), (29, 31),  # Left leg
        (24, 26), (26, 28), (28, 30), (30, 32)   # Right leg
    ]
}
