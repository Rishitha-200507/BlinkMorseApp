# ==========================================
# BLINK MORSE AI APP - CLEAN FULL BUILD
# PART 1 of FULL CODE
# Paste this first in app.py
# ==========================================

import code
from pdb import run
from unittest import result

import customtkinter as ctk
import sqlite3
import bcrypt
from tkinter import messagebox
import cv2
from PIL import Image
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import random
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import win32com.client
# ------------------------------------------
# APP SETTINGS
# ------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ------------------------------------------
# DATABASE
# ------------------------------------------
def setup_database():

    conn = sqlite3.connect("blinkmorse.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password BLOB
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS morse_scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        score INTEGER,
        total INTEGER
    )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------
# MAIN APP
# ------------------------------------------
class BlinkMorseApp(ctk.CTk):

    def __init__(self):
        super().__init__()


        self.title("Blink Morse AI App")
        self.geometry("1400x900")

        self.current_user = None
        self.cap = None

        self.show_login_page()

    # --------------------------------------
    # CLEAR WINDOW
    # --------------------------------------
    def clear_window(self):

        if self.cap:
            try:
                self.cap.release()
            except:
                pass

        for widget in self.winfo_children():
            widget.destroy()


    # --------------------------------------
    # SPEAK
    # --------------------------------------
    def speak(self, text):

        if str(text).strip() == "":
            return

        def run():
            try:
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Rate = 0
                speaker.Volume = 100
                speaker.Speak(str(text))
            except:
                pass

        threading.Thread(
            target=run,
            daemon=True
        ).start()   
    # --------------------------------------
    # LOGIN PAGE
    # --------------------------------------
    def show_login_page(self):

        self.clear_window()

        frame = ctk.CTkFrame(self, width=420, height=520)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            frame,
            text="Blink Morse AI",
            font=("Arial", 34, "bold")
        ).pack(pady=35)

        self.login_user = ctk.CTkEntry(
            frame,
            width=300,
            placeholder_text="Username"
        )
        self.login_user.pack(pady=10)

        self.login_pass = ctk.CTkEntry(
            frame,
            width=300,
            show="*",
            placeholder_text="Password"
        )
        self.login_pass.pack(pady=10)

        ctk.CTkButton(
            frame,
            text="Login",
            width=300,
            command=self.login_action
        ).pack(pady=20)

        ctk.CTkButton(
            frame,
            text="Create Account",
            width=300,
            command=self.show_register_page
        ).pack()

    # --------------------------------------
    # REGISTER PAGE
    # --------------------------------------
    def show_register_page(self):

        self.clear_window()

        frame = ctk.CTkFrame(self, width=420, height=560)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            frame,
            text="Create Account",
            font=("Arial", 32, "bold")
        ).pack(pady=30)

        self.reg_user = ctk.CTkEntry(
            frame,
            width=300,
            placeholder_text="Username"
        )
        self.reg_user.pack(pady=10)

        self.reg_pass = ctk.CTkEntry(
            frame,
            width=300,
            show="*",
            placeholder_text="Password"
        )
        self.reg_pass.pack(pady=10)

        self.reg_confirm = ctk.CTkEntry(
            frame,
            width=300,
            show="*",
            placeholder_text="Confirm Password"
        )
        self.reg_confirm.pack(pady=10)

        ctk.CTkButton(
            frame,
            text="Register",
            width=300,
            command=self.register_action
        ).pack(pady=20)

        ctk.CTkButton(
            frame,
            text="Back",
            width=300,
            command=self.show_login_page
        ).pack()

    # --------------------------------------
    # REGISTER ACTION
    # --------------------------------------
    def register_action(self):

        user = self.reg_user.get().strip()
        pwd = self.reg_pass.get().strip()
        con = self.reg_confirm.get().strip()

        if user == "" or pwd == "":
            messagebox.showerror("Error", "Fill all fields")
            return

        if pwd != con:
            messagebox.showerror("Error", "Passwords do not match")
            return

        hashed = bcrypt.hashpw(
            pwd.encode(),
            bcrypt.gensalt()
        )

        try:
            conn = sqlite3.connect("blinkmorse.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users(username,password) VALUES (?,?)",
                (user, hashed)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Account Created")
            self.show_login_page()

        except:
            messagebox.showerror("Error", "Username exists")

    # --------------------------------------
    # LOGIN ACTION
    # --------------------------------------
    def login_action(self):

        user = self.login_user.get().strip()
        pwd = self.login_pass.get().strip()

        conn = sqlite3.connect("blinkmorse.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (user,)
        )

        row = cursor.fetchone()
        conn.close()

        if row and bcrypt.checkpw(
            pwd.encode(),
            row[0]
        ):
            self.current_user = user
            self.show_module_page()
        else:
            messagebox.showerror(
                "Error",
                "Invalid Login"
            )

    # --------------------------------------
    # MODULE PAGE
    # --------------------------------------
    def show_module_page(self):

        self.clear_window()

        frame = ctk.CTkFrame(self, width=650, height=620)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            frame,
            text=f"Welcome {self.current_user}",
            font=("Arial", 34, "bold")
        ).pack(pady=35)

        ctk.CTkButton(
            frame,
            text="Morse Blink Module",
            width=380,
            height=80,
            command=self.open_morse_module
        ).pack(pady=20)

        ctk.CTkButton(
            frame,
            text="Sign Language Module",
            width=380,
            height=80,
            fg_color="green",
            command=self.open_sign_module
        ).pack(pady=20)


        ctk.CTkButton(
            frame,
            text="Logout",
            width=250,
            fg_color="red",
            command=self.show_login_page
        ).pack(pady=30)

    # --------------------------------------
    # OPEN MORSE
    # --------------------------------------
    def open_morse_module(self):

        self.clear_window()

        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar,
            text="Morse Blink",
            font=("Arial", 28, "bold")
        ).pack(pady=25)

        ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            width=180,
            command=self.show_dashboard
        ).pack(pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Freestyle",
            width=180,
            command=self.show_freestyle
        ).pack(pady=10)

        ctk.CTkButton(
             self.sidebar,
             text="Learning Quiz",
             width=180,
             command=self.show_learning_quiz
        ).pack(pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Change Module",
            width=180,
            command=self.show_module_page
        ).pack(pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Logout",
            width=180,
            fg_color="red",
            command=self.show_login_page
        ).pack(pady=30)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.show_dashboard()

    # ==========================================
# PART 2 of FULL CODE
# Paste BELOW Part 1 in same app.py
# ==========================================

    # --------------------------------------
    # CLEAR MAIN FRAME
    # --------------------------------------
    
    def clear_main(self):
        

        self.page_active = False

        if self.cap:
            try:
                self.cap.release()
            except:
                pass

        for w in self.main_frame.winfo_children():
            w.destroy()

    # --------------------------------------
    # DASHBOARD
    # --------------------------------------
    def show_dashboard(self):
        self.clear_main()

        conn = sqlite3.connect("blinkmorse.db")
        cur = conn.cursor()

        cur.execute("""
        SELECT score,total
        FROM morse_scores
        WHERE username=?
        ORDER BY id DESC
        LIMIT 1
        """, (self.current_user,))
        recent = cur.fetchone()

        cur.execute("""
        SELECT MAX(score)
        FROM morse_scores
        WHERE username=?
        """, (self.current_user,))
        best = cur.fetchone()

        cur.execute("""
        SELECT SUM(score),SUM(total)
        FROM morse_scores
        WHERE username=?
        """, (self.current_user,))
        sums = cur.fetchone()

        cur.execute("""
        SELECT score
        FROM morse_scores
        WHERE username=?
        ORDER BY id ASC
        """, (self.current_user,))
        graph_scores = cur.fetchall()

        conn.close()

        rs = recent[0] if recent else 0
        rt = recent[1] if recent else 0
        bs = best[0] if best[0] else 0

        if sums and sums[1]:
            acc = int((sums[0]/sums[1])*100)
        else:
            acc = 0

        ctk.CTkLabel(
            self.main_frame,
            text="Dashboard",
            font=("Arial",34,"bold")
        ).pack(pady=20)

        row = ctk.CTkFrame(self.main_frame)
        row.pack(pady=10)

        cards = [
            ("Recent Score", f"{rs}/{rt}"),
            ("Accuracy", f"{acc}%"),
            ("Best Score", f"{bs}/10")
        ]

        for title,val in cards:

            box = ctk.CTkFrame(row,width=220,height=130)
            box.pack(side="left", padx=15)

            ctk.CTkLabel(box,text=title).pack(pady=15)
            ctk.CTkLabel(
            box,
            text=val,
            font=("Arial",28,"bold")
        ).pack()

    # -------------------------
    # GRAPH
    # -------------------------
        if graph_scores:

            values = [x[0] for x in graph_scores]
            attempts = list(range(1, len(values)+1))

            fig = plt.Figure(figsize=(20,12), dpi=100)
            ax = fig.add_subplot(111)

            ax.bar(attempts, values)
            ax.set_title("Quiz Scores")
            ax.set_xlabel("Attempt")
            ax.set_ylabel("Score")

            canvas = FigureCanvasTkAgg(
                fig,
                master=self.main_frame
            )
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

        else:

            ctk.CTkLabel(
            self.main_frame,
            text="No quiz data yet"
        ).pack(pady=30)

    # --------------------------------------
    # FREESTYLE PAGE
    # --------------------------------------
    def show_freestyle(self):

        self.clear_main()
        self.page_active = True

        self.is_calibrated = False
        self.calibration_start = time.time()
        self.calibration_values = []

        self.blinking = False
        self.blink_start = 0
        self.last_blink_end = time.time()

        self.current_morse = ""
        self.current_word = ""
        self.full_text = ""
        self.symbol_time = time.time()

        self.letter_processed = False
        self.word_processed = False

        self.morse_dict = {
            "A": ".-", "B": "-...", "C": "-.-.",
            "D": "-..", "E": ".", "F": "..-.",
            "G": "--.", "H": "....", "I": "..",
            "J": ".---", "K": "-.-", "L": ".-..",
            "M": "--", "N": "-.", "O": "---",
            "P": ".--.", "Q": "--.-", "R": ".-.",
            "S": "...", "T": "-", "U": "..-",
            "V": "...-", "W": ".--", "X": "-..-",
            "Y": "-.--", "Z": "--.."
        }

        self.reverse_dict = {
            v:k for k,v in self.morse_dict.items()
        }

        ctk.CTkLabel(
            self.main_frame,
            text="Freestyle Mode",
            font=("Arial", 30, "bold")
        ).pack(pady=10)

        top = ctk.CTkFrame(self.main_frame)
        top.pack(fill="both", expand=True)

        self.cam_label = ctk.CTkLabel(top, text="")
        self.cam_label.pack(side="left", padx=10)

        right = ctk.CTkScrollableFrame(top, width=320)
        right.pack(side="right", fill="y")

        ctk.CTkLabel(
            right,
            text="Commands",
            font=("Arial", 22, "bold")
        ).pack(pady=10)

        cmds = [
            (".....", "Delete Letter"),
            ("----", "Delete Word"),
            ("..--", "Accept Guess"),
            (".", "Short Blink"),
            ("-", "Long Blink"),
            ("Pause >2 sec", "Letter End"),
            ("Pause >4 sec", "Speak Word")
        ]

        for a,b in cmds:
            ctk.CTkLabel(
                right,
                text=f"{a} = {b}"
            ).pack(anchor="w")

        ctk.CTkLabel(
            right,
            text="Dictionary",
            font=("Arial", 22, "bold")
        ).pack(pady=10)

        for k,v in self.morse_dict.items():
            ctk.CTkLabel(
                right,
                text=f"{k} = {v}"
            ).pack(anchor="w")

        self.status_lbl = ctk.CTkLabel(
            self.main_frame,
            text="Calibrating..."
        )
        self.status_lbl.pack()

        self.morse_lbl = ctk.CTkLabel(
            self.main_frame,
            text="Morse:",
            font=("Arial", 22, "bold")
        )
        self.morse_lbl.pack()

        self.text_lbl = ctk.CTkLabel(
            self.main_frame,
            text="Text:",
            font=("Arial", 28, "bold")
        )
        self.text_lbl.pack()

        self.guess_lbl = ctk.CTkLabel(
            self.main_frame,
            text="Guess Word:"
        )
        self.guess_lbl.pack()

        self.cap = cv2.VideoCapture(0)

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=3,
            refine_landmarks=True
        )

        self.LEFT = [33,160,158,133,153,144]
        self.RIGHT = [362,385,387,263,373,380]

        self.update_freestyle()

# ==========================================
# PART 3 of FULL CODE
# Paste BELOW Part 2 in same app.py
# ==========================================

    # --------------------------------------
    # GUESS WORD
    # --------------------------------------
    def show_guess(self):

        if not hasattr(self, "guess_lbl"):
            return

        if not self.guess_lbl.winfo_exists():
            return

        words = [
        "HELLO","HELP","HOME",
        "GOOD","GO","COME",
        "CALL","CLASS","COLLEGE"
    ]

        typed = self.current_word.upper()

        if typed == "":
            self.guess_lbl.configure(
                text="Guess Word:"
            )
            return

        arr = []

        for w in words:
            if w.startswith(typed):
                arr.append(w)

        self.guess_lbl.configure(
            text="Guess Word: " + " / ".join(arr[:3])
        )
    # --------------------------------------
    # FREESTYLE CAMERA LOOP
    # --------------------------------------
    def update_freestyle(self):

        if not hasattr(self, "page_active") or not self.page_active:
            return

        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()

        if not ret:
            return

        frame = cv2.resize(frame, (640,480))

        frame = cv2.flip(frame, 1)

        h, w, _ = frame.shape

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        result = self.face_mesh.process(rgb)

# ---------------------------------
# MULTIPLE FACE CHECK (SAFE FIX)
# ---------------------------------
        if result.multi_face_landmarks:

            if len(result.multi_face_landmarks) > 1:

                self.status_lbl.configure(
                    text="⚠ Only one face allowed"
            )

            self.blinking = False
            self.blink_start = 0

            img = Image.fromarray(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )

            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(640,480)
            )

            self.cam_label.configure(image=ctk_img)

            self.after(40, self.update_freestyle)
            return


        if result.multi_face_landmarks:

            face = result.multi_face_landmarks[0]

            def EAR(ids):

                pts = []

                for i in ids:

                    x = int(face.landmark[i].x * w)
                    y = int(face.landmark[i].y * h)

                    pts.append((x, y))

                    cv2.circle(
                        frame,
                        (x, y),
                        2,
                        (0,255,0),
                        -1
                    )

                p = np.array(pts)

                v1 = np.linalg.norm(p[1]-p[5])
                v2 = np.linalg.norm(p[2]-p[4])
                hor = np.linalg.norm(p[0]-p[3])

                return (v1+v2)/(2*hor)

            ear = (EAR(self.LEFT)+EAR(self.RIGHT))/2

            now = time.time()

            # Calibration = 5 sec
            if not self.is_calibrated:

                self.calibration_values.append(ear)

                left = 5 - int(now-self.calibration_start)

                self.status_lbl.configure(
                    text=f"Calibrating... {left}s"
                )

                if now-self.calibration_start > 5:

                    self.threshold = np.mean(
                        self.calibration_values
                    ) * 0.75

                    self.is_calibrated = True

                    self.status_lbl.configure(
                        text="Ready"
                    )

            else:

                # Eye closed
                if ear < self.threshold:

                    if not self.blinking:
                        self.blinking = True
                        self.blink_start = now

                else:

                    if self.blinking:

                        self.blinking = False

                        dur = now - self.blink_start
                        self.blink_start = 0
                        self.last_blink_end = now

                        if dur < 0.5:
                            self.current_morse += "."
                        else:
                            self.current_morse += "-"

                        self.letter_processed = False
                        self.word_processed = False

                        self.morse_lbl.configure(
                            text="Morse: " + self.current_morse
                        )

                gap = now-self.last_blink_end

                # Process after 2 sec
                                # Process after 2 sec
                if gap > 2 and self.current_morse != "" and not self.letter_processed:

                    code = self.current_morse

                    # delete letter
                    if code == ".....":

                        if len(self.current_word) > 0:
                            self.current_word = self.current_word[:-1]

                        

                    # delete word
                    elif code == "----":

                        self.current_word = ""

                        
                    # accept guess
                    elif code == "..--":

                        guess_text = self.guess_lbl.cget("text")

                        guess = guess_text.replace(
                            "Guess Word: ",
                            ""
                        ).split("/")[0].strip()

                        if guess == "":
                            guess = self.current_word

                        if guess != "":

                            self.full_text += guess + " "

                            

                        self.current_word = ""

                        self.show_guess()

                        

                    # normal letter
                    else:

                        letter = self.reverse_dict.get(
                            code, ""
                        )

                        if letter != "":
                            self.current_word += letter

                    self.text_lbl.configure(
                        text="Text: " +
                        self.full_text +
                        self.current_word
                    )

                    self.show_guess()

                    self.current_morse = ""

                    self.last_blink_end = time.time()

                    self.morse_lbl.configure(
                        text="Morse:"
                    )

                    self.letter_processed = True

                # Complete word after 4 sec
                if gap > 4 and self.current_word != "" and not self.word_processed:

                    word = self.current_word

                    self.full_text += word + " "

                    self.text_lbl.configure(
                        text="Text: " + self.full_text
                    )

                    self.speak(word)

                    self.current_word = ""

                    self.word_processed = True
                    self.last_blink_end = time.time()

        img = Image.fromarray(
            cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )
        )

        ctk_img = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(640,480)
        )

        if self.blinking and (now - self.blink_start) > 2:
            self.blinking = False
            self.blink_start = 0

        self.cam_label.configure(
            image=ctk_img
        )

        self.after(
            40,
            self.update_freestyle
        )

        

    # --------------------------------------
    # LEARNING QUIZ PAGE
    # --------------------------------------
    def show_learning_quiz(self):

        self.clear_main()

        self.quiz_total = 10
        self.quiz_index = 0
        self.quiz_score = 0

        self.current_word = ""
        self.current_morse = ""

        self.quiz_mode = ctk.StringVar(value="Letters")

        ctk.CTkLabel(
            self.main_frame,
            text="Learning Quiz",
            font=("Arial", 30, "bold")
        ).pack(pady=15)

        body = ctk.CTkFrame(self.main_frame)
        body.pack(fill="both", expand=True, padx=15, pady=10)

        # LEFT CAMERA
        left = ctk.CTkFrame(body)
        left.pack(side="left", fill="both", expand=True, padx=10)

        self.cam_label = ctk.CTkLabel(
            left,
            text=""
        )
        self.cam_label.pack(pady=20)

        # RIGHT PANEL
        right = ctk.CTkFrame(body, width=320)
        right.pack(side="right", fill="y", padx=10)

        ctk.CTkOptionMenu(
            right,
            values=["Letters","Words","Sentences"],
            variable=self.quiz_mode
        ).pack(pady=10)

        self.quiz_lbl = ctk.CTkLabel(
            right,
            text="Question 1 / 10",
            font=("Arial",20,"bold")
        )
        self.quiz_lbl.pack(pady=10)

        self.question_lbl = ctk.CTkLabel(
            right,
            text="HELLO",
            font=("Arial",28,"bold")
        )
        self.question_lbl.pack(pady=15)

        self.answer_lbl = ctk.CTkLabel(
            right,
            text="Your Answer:"
        )
        self.answer_lbl.pack(pady=10)

        self.result_lbl = ctk.CTkLabel(
            right,
            text=""
        )
        self.result_lbl.pack(pady=10)

        ctk.CTkButton(
            right,
            text="Check",
            command=self.check_quiz_answer
        ).pack(pady=5)

        ctk.CTkButton(
            right,
            text="Next",
            command=self.next_quiz_question
        ).pack(pady=5)

        self.score_lbl = ctk.CTkLabel(
            right,
            text="Score: 0 / 10"
        )
        self.score_lbl.pack(pady=15)

        self.status_lbl = ctk.CTkLabel(
            self.main_frame,
            text="Ready"
        )
        self.status_lbl.pack(pady=5)

        self.morse_lbl = ctk.CTkLabel(
            self.main_frame,
            text="Morse:"
        )
        self.morse_lbl.pack()

        self.text_lbl = ctk.CTkLabel(
            self.main_frame,
            text="Text:"
        )
        self.text_lbl.pack()

        # start quiz
        self.next_quiz_question()
        self.prepare_quiz_camera()
        self.update_quiz_camera()

    # --------------------------------------
    # NEXT QUESTION
    # --------------------------------------
    def next_quiz_question(self):

        import random

        if self.quiz_index >= self.quiz_total:
            self.finish_quiz()
            return

        self.quiz_index += 1

        self.current_word = ""
        self.current_morse = ""

        self.answer_lbl.configure(text="Your Answer:")
        self.result_lbl.configure(text="")
        self.text_lbl.configure(text="Text:")

        self.quiz_lbl.configure(
            text=f"Question {self.quiz_index} / {self.quiz_total}"
        )

        letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        words = [
            "HELLO","HELP","YES",
            "NO","HOME","WATER"
        ]

        sentences = [
            "HELLO WORLD",
            "GOOD MORNING",
            "THANK YOU"
        ]

        mode = self.quiz_mode.get()

        if mode == "Letters":
            self.target_answer = random.choice(letters)

        elif mode == "Words":
            self.target_answer = random.choice(words)

        else:
            self.target_answer = random.choice(sentences)

        self.question_lbl.configure(
            text="Blink: " + self.target_answer
        )

        self.after(
        300,
        lambda: self.speak(
            "Blink " + self.target_answer
            )
        )

    def prepare_quiz_camera(self):

        self.cap = cv2.VideoCapture(0)

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True
        )

        self.LEFT = [33,160,158,133,153,144]
        self.RIGHT = [362,385,387,263,373,380]

        self.is_calibrated = False
        self.calibration_start = time.time()
        self.calibration_values = []

        self.blinking = False
        self.blink_start = 0
        self.last_blink_end = time.time()

        self.current_morse = ""
        self.current_word = ""

    def update_quiz_camera(self):

        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()

        if not ret:
            self.after(30, self.update_quiz_camera)
            return

        frame = cv2.flip(frame, 1)

        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self.face_mesh.process(rgb)

        if result.multi_face_landmarks:

            face = result.multi_face_landmarks[0]

            def EAR(ids):

                pts = []

                for i in ids:
                    x = int(face.landmark[i].x * w)
                    y = int(face.landmark[i].y * h)

                    pts.append((x, y))

                    cv2.circle(frame, (x, y), 2, (0,255,0), -1)

                p = np.array(pts)

                v1 = np.linalg.norm(p[1]-p[5])
                v2 = np.linalg.norm(p[2]-p[4])
                hor = np.linalg.norm(p[0]-p[3])

                return (v1+v2)/(2*hor)

            ear = (EAR(self.LEFT)+EAR(self.RIGHT))/2
            now = time.time()

            # -------------------
            # Calibration
            # -------------------
            if not self.is_calibrated:

                self.calibration_values.append(ear)

                left = max(0, 5 - int(now-self.calibration_start))

                self.status_lbl.configure(
                    text=f"Calibrating... {left}s"
                )

                if now-self.calibration_start > 5:

                    self.threshold = np.mean(
                        self.calibration_values
                    ) * 0.75

                    self.is_calibrated = True

                    self.status_lbl.configure(
                        text="Ready"
                    )

            else:

                # eye closed
                if ear < self.threshold:

                    if not self.blinking:
                        self.blinking = True
                        self.blink_start = now

                else:

                    if self.blinking:

                        self.blinking = False

                        dur = now-self.blink_start
                        self.last_blink_end = now

                        if dur < 0.5:
                            self.current_morse += "."
                        else:
                            self.current_morse += "-"

                        self.morse_lbl.configure(
                            text="Morse: " + self.current_morse
                        )

                gap = now-self.last_blink_end

                # process letter after 2 sec
                if gap > 2 and self.current_morse != "":

                    letter = self.reverse_dict.get(
                        self.current_morse, ""
                    )

                    if letter != "":
                        self.current_word += letter

                    self.answer_lbl.configure(
                        text="Your Answer: " + self.current_word
                    )

                    self.text_lbl.configure(
                        text="Text: " + self.current_word
                    )

                    self.current_morse = ""

                    self.morse_lbl.configure(
                        text="Morse:"
                    )

        img = Image.fromarray(
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )

        ctk_img = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(760,520)
        )

        self.cam_label.configure(image=ctk_img)

        self.after(15, self.update_quiz_camera)


    # --------------------------------------
    # CHECK ANSWER
    # --------------------------------------
    def check_quiz_answer(self):

        
        ans = self.current_word.strip().upper()
        target = self.target_answer.strip().upper()

        if ans == target:

            self.quiz_score += 1

            self.result_lbl.configure(
                text="Correct",
                text_color="green"
            )
            self.speak("Correct")



        else:

            self.result_lbl.configure(
                text="Wrong",
                text_color="red"
            )
            self.speak("Wrong")

           

        self.score_lbl.configure(
            text=f"Score: {self.quiz_score} / {self.quiz_total}"
        )


    # --------------------------------------
    # FINISH QUIZ
    # --------------------------------------
    def finish_quiz(self):

        conn = sqlite3.connect("blinkmorse.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO morse_scores(username,score,total)
        VALUES(?,?,?)
        """, (
            self.current_user,
            self.quiz_score,
            self.quiz_total
        ))

        conn.commit()
        conn.close()

        self.question_lbl.configure(
            text="Quiz Finished"
        )

        self.result_lbl.configure(
            text=f"Final Score: {self.quiz_score}/{self.quiz_total}"
        )

    

    # --------------------------------------
    # QUIZ CAMERA LOOP
    # --------------------------------------
    def update_learning_frame(self):

        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()

        if not ret:
            return

        frame = cv2.flip(frame, 1)

        h, w, _ = frame.shape

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        result = self.face_mesh.process(rgb)

        if result.multi_face_landmarks:

            face = result.multi_face_landmarks[0]

            def EAR(ids):

                pts = []

                for i in ids:

                    x = int(face.landmark[i].x * w)
                    y = int(face.landmark[i].y * h)

                    pts.append((x, y))

                    cv2.circle(
                        frame,
                        (x, y),
                        2,
                        (0,255,0),
                        -1
                    )

                p = np.array(pts)

                v1 = np.linalg.norm(p[1]-p[5])
                v2 = np.linalg.norm(p[2]-p[4])
                hor = np.linalg.norm(p[0]-p[3])

                return (v1+v2)/(2*hor)

            ear = (EAR(self.LEFT)+EAR(self.RIGHT))/2

            now = time.time()

            # Calibration
            if not self.is_calibrated:

                self.calibration_values.append(ear)

                left = 5 - int(now-self.calibration_start)

                self.status_lbl.configure(
                    text=f"Calibrating... {left}s"
                )

                if now-self.calibration_start > 5:

                    self.threshold = np.mean(
                        self.calibration_values
                    ) * 0.75

                    self.is_calibrated = True

                    self.status_lbl.configure(
                        text="Ready"
                    )

            else:

                if ear < self.threshold:

                    if not self.blinking:
                        self.blinking = True
                        self.blink_start = now

                else:

                    if self.blinking:

                        self.blinking = False

                        dur = now-self.blink_start
                        self.last_blink_end = now

                        if dur < 0.5:
                            self.current_morse += "."
                        else:
                            self.current_morse += "-"

                        self.morse_lbl.configure(
                            text="Morse: " + self.current_morse
                        )

                gap = now-self.last_blink_end

                # process letter
                if gap > 2 and self.current_morse != "":

                    letter = self.reverse_dict.get(
                        self.current_morse, ""
                    )

                    if letter != "":
                        self.current_word += letter

                    self.answer_lbl.configure(
                        text="Your Answer: " + self.current_word
                    )

                    self.text_lbl.configure(
                        text="Text: " + self.current_word
                    )

                    self.current_morse = ""

                    self.morse_lbl.configure(
                        text="Morse:"
                    )

        img = Image.fromarray(
            cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )
        )

        ctk_img = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(640,480)
        )

        self.cam_label.configure(
            image=ctk_img
        )

        self.after(
            15,
            self.update_learning_frame
        )    

    def open_sign_module(self):

        from sign_module import open_sign_module

        open_sign_module(self)

# ------------------------------------------
# RUN APP
# ------------------------------------------
if __name__ == "__main__":

    setup_database()

    app = BlinkMorseApp()

    app.mainloop()