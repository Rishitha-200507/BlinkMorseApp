import cv2
import mediapipe as mp
import numpy as np
import json
from xgboost import XGBClassifier

# Load label map
with open("label_map.json", "r") as f:
    label_map = json.load(f)

# Load model
model = XGBClassifier()
model.load_model("xgboost_model.json")

# MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    pred = ""

    if result.multi_hand_landmarks:

        for hand in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            row = []

            for lm in hand.landmark:
                row.extend([lm.x, lm.y, lm.z])

            X = np.array(row).reshape(1, -1)

            pred_id = model.predict(X)[0]

            pred = label_map[str(pred_id)]

    cv2.putText(
        frame,
        f"Prediction: {pred}",
        (20,50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.imshow("Sign Test", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()