import os
import cv2
import mediapipe as mp
import pandas as pd

dataset_path = "asl_dataset"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

data = []

classes = os.listdir(dataset_path)

for label in classes:

    folder = os.path.join(dataset_path, label)

    if not os.path.isdir(folder):
        continue

    for file in os.listdir(folder):

        path = os.path.join(folder, file)

        img = cv2.imread(path)

        if img is None:
            continue

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        result = hands.process(rgb)

        if result.multi_hand_landmarks:

            for hand in result.multi_hand_landmarks:

                row = []

                for lm in hand.landmark:
                    row.extend([lm.x, lm.y, lm.z])

                row.append(label)

                data.append(row)

print("Total Samples:", len(data))

columns = []

for i in range(21):
    columns += [f"x{i}", f"y{i}", f"z{i}"]

columns.append("target")

df = pd.DataFrame(data, columns=columns)

df.to_csv("sign_data.csv", index=False)

print("sign_data.csv created successfully!")