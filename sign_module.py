# sign_module.py

import customtkinter as ctk
import cv2
import mediapipe as mp
import numpy as np
import json
import time
import random
from xgboost import XGBClassifier
from PIL import Image
from deep_translator import GoogleTranslator


# =====================================================
# OPEN SIGN MODULE
# =====================================================
def open_sign_module(app):

    app.clear_window()

    app.sidebar = ctk.CTkFrame(app, width=220)
    app.sidebar.pack(side="left", fill="y")

    ctk.CTkLabel(
        app.sidebar,
        text="Sign Module",
        font=("Arial", 28, "bold")
    ).pack(pady=25)

    ctk.CTkButton(
        app.sidebar,
        text="Dashboard",
        width=180,
        command=lambda: show_sign_dashboard(app)
    ).pack(pady=8)

    ctk.CTkButton(
        app.sidebar,
        text="Translator",
        width=180,
        command=lambda: show_sign_translator(app)
    ).pack(pady=8)

    ctk.CTkButton(
        app.sidebar,
        text="Learning",
        width=180,
        command=lambda: show_sign_learning(app)
    ).pack(pady=8)

    ctk.CTkButton(
        app.sidebar,
        text="Quiz",
        width=180,
        command=lambda: show_sign_quiz(app)
    ).pack(pady=8)

    ctk.CTkButton(
        app.sidebar,
        text="Change Module",
        width=180,
        command=app.show_module_page
    ).pack(pady=8)

    ctk.CTkButton(
        app.sidebar,
        text="Logout",
        width=180,
        fg_color="red",
        command=app.show_login_page
    ).pack(pady=25)

    app.main_frame = ctk.CTkFrame(app)
    app.main_frame.pack(
        side="right",
        fill="both",
        expand=True
    )

    show_sign_dashboard(app)


# =====================================================
# CLEAR MAIN
# =====================================================
def clear_main(app):

    if hasattr(app, "cap") and app.cap:
        try:
            app.cap.release()
        except:
            pass

    for widget in app.main_frame.winfo_children():
        widget.destroy()


# =====================================================
# LOAD MODEL ONCE
# =====================================================
def load_sign_model(app):

    if hasattr(app, "sign_loaded"):
        return

    with open("label_map.json", "r") as f:
        app.label_map = json.load(f)

    app.model = XGBClassifier()
    app.model.load_model("xgboost_model.json")

    app.mp_hands = mp.solutions.hands
    app.hands = app.mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7
    )

    app.mp_draw = mp.solutions.drawing_utils

    app.sign_loaded = True


# =====================================================
# PREDICT LETTER
# =====================================================
def predict_sign(app, frame):

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = app.hands.process(rgb)

    pred = ""
    conf = 0

    if result.multi_hand_landmarks:

        for hand in result.multi_hand_landmarks:

            app.mp_draw.draw_landmarks(
                frame,
                hand,
                app.mp_hands.HAND_CONNECTIONS
            )

            row = []

            for lm in hand.landmark:
                row.extend([lm.x, lm.y, lm.z])

            X = np.array(row).reshape(1, -1)

            probs = app.model.predict_proba(X)[0]

            idx = np.argmax(probs)
            conf = probs[idx]

            if conf > 0.82:
                pred = app.label_map[str(idx)]
            else:
                pred = ""

    return frame, pred, conf


# =====================================================
# REPLACE ONLY THIS FUNCTION IN sign_module.py
# Metrics Dashboard similar to Blink Morse style
# =====================================================

def show_sign_dashboard(app):

    clear_main(app)

    import random

    # Demo metrics (replace later with real values if needed)
    accuracy = 92
    quiz_score = 8
    learning_rate = 0.001

    # Title
    ctk.CTkLabel(
        app.main_frame,
        text="Sign Language Dashboard",
        font=("Arial", 34, "bold")
    ).pack(pady=(20, 10))

    ctk.CTkLabel(
        app.main_frame,
        text="Model Performance & User Progress",
        font=("Arial", 20)
    ).pack(pady=(0, 15))

    # -----------------------------------
    # TOP METRIC CARDS
    # -----------------------------------
    cards = ctk.CTkFrame(
        app.main_frame,
        fg_color="transparent"
    )
    cards.pack(pady=10)

    # Accuracy Card
    c1 = ctk.CTkFrame(cards, width=220, height=120)
    c1.pack(side="left", padx=10)
    c1.pack_propagate(False)

    ctk.CTkLabel(
        c1,
        text="Accuracy",
        font=("Arial", 22, "bold")
    ).pack(pady=(18, 8))

    ctk.CTkLabel(
        c1,
        text=f"{accuracy}%",
        font=("Arial", 30)
    ).pack()

    # Quiz Score Card
    c2 = ctk.CTkFrame(cards, width=220, height=120)
    c2.pack(side="left", padx=10)
    c2.pack_propagate(False)

    ctk.CTkLabel(
        c2,
        text="Quiz Score",
        font=("Arial", 22, "bold")
    ).pack(pady=(18, 8))

    ctk.CTkLabel(
        c2,
        text=f"{quiz_score}/10",
        font=("Arial", 30)
    ).pack()

    # Learning Rate Card
    c3 = ctk.CTkFrame(cards, width=220, height=120)
    c3.pack(side="left", padx=10)
    c3.pack_propagate(False)

    ctk.CTkLabel(
        c3,
        text="Learning Rate",
        font=("Arial", 22, "bold")
    ).pack(pady=(18, 8))

    ctk.CTkLabel(
        c3,
        text=str(learning_rate),
        font=("Arial", 26)
    ).pack()

    # -----------------------------------
    # GRAPH SECTION (LINE GRAPH STYLE)
    # -----------------------------------
    ctk.CTkLabel(
        app.main_frame,
        text="Training Progress Graph",
        font=("Arial", 26, "bold")
    ).pack(pady=(30, 10))

    graph = ctk.CTkCanvas(
        app.main_frame,
        width=760,
        height=300,
        bg="#1e1e1e",
        highlightthickness=0
    )
    graph.pack(pady=10)

    # Axes
    graph.create_line(50, 250, 720, 250, width=2, fill="white")
    graph.create_line(50, 40, 50, 250, width=2, fill="white")

    # Labels
    graph.create_text(380, 275, text="Iterations", fill="white", font=("Arial", 14))
    graph.create_text(20, 145, text="Accuracy", fill="white", font=("Arial", 14))

    # Example graph points
    points = [
        (60, 220),
        (130, 210),
        (200, 185),
        (270, 170),
        (340, 150),
        (410, 130),
        (480, 115),
        (550, 95),
        (620, 78),
        (690, 60)
    ]

    # Draw line graph
    for i in range(len(points)-1):
        graph.create_line(
            points[i][0], points[i][1],
            points[i+1][0], points[i+1][1],
            width=3,
            fill="cyan",
            smooth=True
        )

    # Draw dots
    for p in points:
        graph.create_oval(
            p[0]-4, p[1]-4,
            p[0]+4, p[1]+4,
            fill="cyan",
            outline="cyan"
        )

    # -----------------------------------
    # BUTTONS
    # -----------------------------------
    btn_frame = ctk.CTkFrame(
        app.main_frame,
        fg_color="transparent"
    )
    btn_frame.pack(pady=25)

    ctk.CTkButton(
        btn_frame,
        text="Translator",
        width=180,
        height=45,
        command=lambda: show_sign_translator(app)
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        btn_frame,
        text="Learning",
        width=180,
        height=45,
        command=lambda: show_sign_learning(app)
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        btn_frame,
        text="Quiz",
        width=180,
        height=45,
        command=lambda: show_sign_quiz(app)
    ).pack(side="left", padx=10)


# =====================================================
# TRANSLATION
# =====================================================
def translate_text(app):

    txt = app.live_text.strip()

    if txt == "":
        return

    lang_map = {
        "English": "en",
        "Hindi": "hi",
        "Kannada": "kn",
        "Telugu": "te",
        "Tamil": "ta"
    }

    try:
        target = lang_map[app.lang_menu.get()]

        if target == "en":
            result = txt
        else:
            result = GoogleTranslator(
                source="auto",
                target=target
            ).translate(txt.title())

        app.translated_lbl.configure(
            text="Translated Text: " + result
        )

    except Exception as e:
        app.translated_lbl.configure(
            text="Translation Failed"
        )


# =====================================================
# BUTTON FUNCTIONS
# =====================================================
def add_space(app):
    app.live_text += " "


def delete_letter(app):
    app.live_text = app.live_text[:-1]


def clear_text(app):
    app.live_text = ""
    app.translated_lbl.configure(
        text="Translated Text:"
    )


# =====================================================
# TRANSLATOR PAGE
# =====================================================
def show_sign_translator(app):

    clear_main(app)
    load_sign_model(app)

    ctk.CTkLabel(
        app.main_frame,
        text="Live Sign Translator",
        font=("Arial", 30, "bold")
    ).pack(pady=10)

    body = ctk.CTkFrame(
        app.main_frame,
        fg_color="transparent"
    )
    body.pack(fill="both", expand=True)

    # LEFT CAMERA
    left = ctk.CTkFrame(body)
    left.pack(side="left", padx=10)

    app.cam_label = ctk.CTkLabel(left, text="")
    app.cam_label.pack(padx=10, pady=10)

    # RIGHT PANEL
    right = ctk.CTkFrame(body, width=320)
    right.pack(side="right", fill="y", padx=10)

    app.sign_text = ctk.CTkLabel(
        right,
        text="Text:",
        font=("Arial", 24, "bold"),
        wraplength=280,
        justify="left"
    )
    app.sign_text.pack(pady=10)

    app.translated_lbl = ctk.CTkLabel(
        right,
        text="Translated Text:",
        font=("Arial", 22),
        wraplength=280,
        justify="left"
    )
    app.translated_lbl.pack(pady=10)

    ctk.CTkButton(
        right,
        text="SPACE",
        width=220,
        command=lambda: add_space(app)
    ).pack(pady=5)

    ctk.CTkButton(
        right,
        text="DELETE",
        width=220,
        command=lambda: delete_letter(app)
    ).pack(pady=5)

    ctk.CTkButton(
        right,
        text="CLEAR",
        width=220,
        command=lambda: clear_text(app)
    ).pack(pady=5)

    app.pred_lbl = ctk.CTkLabel(
        right,
        text="Prediction: ...",
        font=("Arial", 22)
    )
    app.pred_lbl.pack(pady=10)

    app.lang_menu = ctk.CTkOptionMenu(
        right,
        values=[
            "English",
            "Hindi",
            "Kannada",
            "Telugu",
            "Tamil"
        ],
        width=220
    )
    app.lang_menu.pack(pady=5)

    ctk.CTkButton(
        right,
        text="Translate",
        width=220,
        command=lambda: translate_text(app)
    ).pack(pady=5)

    app.cap = cv2.VideoCapture(0)

    app.live_text = ""
    app.last_pred = ""
    app.stable_start = time.time()
    app.captured_letter = ""

    update_sign_camera(app)


# =====================================================
# TRANSLATOR CAMERA LOOP
# =====================================================
def update_sign_camera(app):

    if not app.cap:
        return

    ret, frame = app.cap.read()

    if not ret:
        return

    frame = cv2.flip(frame, 1)

    frame, pred, conf = predict_sign(app, frame)

    now = time.time()

    if pred == app.last_pred and pred != "":

        if now - app.stable_start > 1:

            if app.captured_letter != pred:
                app.live_text += pred
                app.captured_letter = pred

    else:
        app.last_pred = pred
        app.stable_start = now
        app.captured_letter = ""

    show_pred = "..."

    if pred != "":
        show_pred = f"{pred} ({int(conf*100)}%)"

    img = Image.fromarray(
        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    )

    ctk_img = ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=(720, 520)
    )

    app.cam_label.configure(image=ctk_img)
    app.sign_text.configure(text="Text: " + app.live_text)
    app.pred_lbl.configure(text="Prediction: " + show_pred)

    app.main_frame.after(
        30,
        lambda: update_sign_camera(app)
    )


# =====================================================
# LEARNING MODE
# =====================================================
def show_sign_learning(app):

    clear_main(app)
    load_sign_model(app)

    app.learn_target = "A"

    ctk.CTkLabel(
        app.main_frame,
        text="Learning Mode",
        font=("Arial", 32, "bold")
    ).pack(pady=15)

    app.learn_lbl = ctk.CTkLabel(
        app.main_frame,
        text="Show Sign: A",
        font=("Arial", 28)
    )
    app.learn_lbl.pack(pady=10)

    app.cam_label = ctk.CTkLabel(
        app.main_frame,
        text=""
    )
    app.cam_label.pack(pady=10)

    app.learn_result = ctk.CTkLabel(
        app.main_frame,
        text="",
        font=("Arial", 24)
    )
    app.learn_result.pack(pady=10)

    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    app.learn_menu = ctk.CTkOptionMenu(
        app.main_frame,
        values=letters,
        command=lambda x: set_learning_letter(app, x)
    )
    app.learn_menu.pack(pady=10)

    ctk.CTkButton(
        app.main_frame,
        text="Next Random",
        width=180,
        command=lambda: next_learning_letter(app)
    ).pack(pady=10)

    app.cap = cv2.VideoCapture(0)

    update_learning_camera(app)


def set_learning_letter(app, letter):

    app.learn_target = letter

    app.learn_lbl.configure(
        text="Show Sign: " + letter
    )

    app.learn_result.configure(text="")


def next_learning_letter(app):

    letter = random.choice(
        list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    )

    set_learning_letter(app, letter)


def update_learning_camera(app):

    ret, frame = app.cap.read()

    if not ret:
        return

    frame = cv2.flip(frame, 1)

    frame, pred, conf = predict_sign(app, frame)

    if pred == app.learn_target:
        app.learn_result.configure(
            text="Correct ✅"
        )

    img = Image.fromarray(
        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    )

    ctk_img = ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=(720, 520)
    )

    app.cam_label.configure(image=ctk_img)

    app.main_frame.after(
        30,
        lambda: update_learning_camera(app)
    )


# =====================================================
# QUIZ MODE
# =====================================================
def show_sign_quiz(app):

    clear_main(app)
    load_sign_model(app)

    app.quiz_score = 0
    app.quiz_qno = 1
    app.quiz_locked = False

    ctk.CTkLabel(
        app.main_frame,
        text="Quiz Mode",
        font=("Arial", 32, "bold")
    ).pack(pady=15)

    app.quiz_lbl = ctk.CTkLabel(
        app.main_frame,
        text="Question 1 / 10",
        font=("Arial", 26)
    )
    app.quiz_lbl.pack(pady=10)

    app.quiz_target_lbl = ctk.CTkLabel(
        app.main_frame,
        text=""
    )
    app.quiz_target_lbl.pack(pady=10)

    app.cam_label = ctk.CTkLabel(
        app.main_frame,
        text=""
    )
    app.cam_label.pack(pady=10)

    app.quiz_score_lbl = ctk.CTkLabel(
        app.main_frame,
        text="Score: 0",
        font=("Arial", 24)
    )
    app.quiz_score_lbl.pack(pady=8)

    app.quiz_result = ctk.CTkLabel(
        app.main_frame,
        text="",
        font=("Arial", 24)
    )
    app.quiz_result.pack(pady=8)

    next_quiz_question(app)

    app.cap = cv2.VideoCapture(0)

    update_quiz_camera(app)


def next_quiz_question(app):

    if app.quiz_qno > 10:

        app.quiz_target_lbl.configure(
            text="Quiz Finished!"
        )

        app.quiz_result.configure(
            text=f"Final Score: {app.quiz_score}/10"
        )

        return

    app.quiz_target = random.choice(
        list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    )

    app.quiz_lbl.configure(
        text=f"Question {app.quiz_qno} / 10"
    )

    app.quiz_target_lbl.configure(
        text="Show Sign: " + app.quiz_target
    )

    app.quiz_result.configure(text="")
    app.quiz_locked = False


def update_quiz_camera(app):

    ret, frame = app.cap.read()

    if not ret:
        return

    frame = cv2.flip(frame, 1)

    frame, pred, conf = predict_sign(app, frame)

    if (
        pred == app.quiz_target
        and not app.quiz_locked
    ):

        app.quiz_locked = True
        app.quiz_score += 1

        app.quiz_score_lbl.configure(
            text=f"Score: {app.quiz_score}"
        )

        app.quiz_result.configure(
            text="Correct ✅"
        )

        app.quiz_qno += 1

        app.main_frame.after(
            1000,
            lambda: next_quiz_question(app)
        )

    img = Image.fromarray(
        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    )

    ctk_img = ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=(720, 520)
    )

    app.cam_label.configure(image=ctk_img)

    app.main_frame.after(
        30,
        lambda: update_quiz_camera(app)
    )