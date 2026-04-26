import cv2
import pandas as pd
import os
import mediapipe.python.solutions.hands as mp_hands

# Use direct import to bypass potential attribute errors
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.1)

DATA_DIR = './asl_dataset'
data_list = []

print("--- Starting Extraction ---")

if not os.path.exists(DATA_DIR):
    print(f"Error: Folder '{DATA_DIR}' not found!")
else:
    for label in sorted(os.listdir(DATA_DIR)):
        folder_path = os.path.join(DATA_DIR, label)
        if not os.path.isdir(folder_path): continue
        
        print(f"Processing Letter: {label}...")
        for img_name in os.listdir(folder_path):
            img = cv2.imread(os.path.join(folder_path, img_name))
            if img is None: continue
                
            results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    coords = [lm.x for lm in hand_landmarks.landmark] + \
                             [lm.y for lm in hand_landmarks.landmark] + \
                             [lm.z for lm in hand_landmarks.landmark]
                    coords.append(label)
                    data_list.append(coords)

    if data_list:
        cols = [f'x{i}' for i in range(21)] + [f'y{i}' for i in range(21)] + [f'z{i}' for i in range(21)] + ['target']
        pd.DataFrame(data_list, columns=cols).to_csv('sign_data.csv', index=False)
        print(f"\nSUCCESS! Created sign_data.csv with {len(data_list)} rows.")