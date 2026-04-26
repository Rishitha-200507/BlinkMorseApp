import cv2
import mediapipe as mp
import numpy as np
import json
import time
from xgboost import XGBClassifier

# Load files
with open("label_map.json", "r") as f:
    label_map = json.load(f)

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

text = ""

last_pred = ""
stable_start = time.time()
captured_letter = ""

CONFIDENCE_THRESHOLD = 0.75

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    pred = ""
    conf = 0

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

            probs = model.predict_proba(X)[0]

            pred_id = np.argmax(probs)

            conf = probs[pred_id]

            # Ignore weak confidence
            if conf >= CONFIDENCE_THRESHOLD:
                pred = label_map[str(pred_id)]
            else:
                pred = ""

    now = time.time()

    # Stable prediction
    if pred == last_pred and pred != "":

        if now - stable_start > 1.2:

            if captured_letter != pred:
                text += pred
                captured_letter = pred

    else:
        stable_start = now
        captured_letter = ""
        last_pred = pred

    # Keyboard
    key = cv2.waitKey(1) & 0xFF

    if key == 32:
        text += " "

    if key == 8:
        text = text[:-1]

    if key == 27:
        break

    # Display
    if pred != "":
        show = f"{pred} ({int(conf*100)}%)"
    else:
        show = "..."

    cv2.putText(
        frame,
        f"Prediction: {show}",
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.putText(
        frame,
        f"Text: {text}",
        (20,80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255,255,255),
        2
    )

    cv2.putText(
        frame,
        "SPACE=Gap | BACKSPACE=Delete",
        (20,120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0,255,255),
        2
    )

    cv2.imshow("Live Sign Translator", frame)

cap.release()
cv2.destroyAllWindows()