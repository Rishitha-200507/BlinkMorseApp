import customtkinter as ctk
import sqlite3
import bcrypt
from tkinter import messagebox
import cv2
import mediapipe as mp
from mediapipe.python.solutions import face_mesh as mp_face_mesh
from PIL import Image
import time
import numpy as np
import pyttsx3
import threading
import nltk
import random
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
# 1. SETUP: DATABASE & NLP DICTIONARY
# ==========================================
def setup_database():
    conn = sqlite3.connect("morse_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

nltk.download('words', quiet=True)
from nltk.corpus import words

def calculate_EAR(eye_points, landmarks, w, h):
    p = [np.array([landmarks[pt].x * w, landmarks[pt].y * h]) for pt in eye_points]
    v1 = np.linalg.norm(p[1] - p[5])
    v2 = np.linalg.norm(p[2] - p[4])
    hor = np.linalg.norm(p[0] - p[3])
    return (v1 + v2) / (2.0 * hor)

# ==========================================
# 2. MAIN APPLICATION CLASS
# ==========================================
class BlinkMorseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Blink Morse - Learn Morse Code!")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("blue")

        self.current_user = None
        self.cap = None  
        self.app_mode = "dashboard" 

        # --- AUDIO SETUP ---
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150) 

        # --- MEDIAPIPE VARIABLES ---
        self.face_mesh = mp_face_mesh.FaceMesh(max_num_faces=3, refine_landmarks=True)
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        
        # --- METRICS & DICTIONARY ---
        self.english_words = [w.upper() for w in words.words() if len(w) > 1]
        
        self.MORSE_DICT = {
            ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
            "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
            "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
            ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
            "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
            "--..": "Z", ".-.-.-": ".", "--..--": ",", "..--..": "?",
            "-.-.--": "!", "-....-": "-", ".----.": "'", "---...": ":",
            ".-..-.": '"', "-..-.": "/"
        }
        self.LETTER_TO_MORSE = {v: k for k, v in self.MORSE_DICT.items()}
        self.ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.show_login_page()

    def speak_text(self, text):
        def run_tts():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        threading.Thread(target=run_tts, daemon=True).start()

    def clear_window(self):
        for widget in self.winfo_children(): widget.destroy()

    # ==========================================
    # 3. AUTHENTICATION 
    # ==========================================
    def show_login_page(self):
        self.clear_window()
        login_frame = ctk.CTkFrame(self, width=400, height=500, corner_radius=15)
        login_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        ctk.CTkLabel(login_frame, text="Blink Morse", font=("Roboto", 32, "bold")).pack(pady=(50, 30))
        self.username_entry = ctk.CTkEntry(login_frame, placeholder_text="Username", width=250, height=40)
        self.username_entry.pack(pady=10)
        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*", width=250, height=40)
        self.password_entry.pack(pady=10)
        ctk.CTkButton(login_frame, text="Login", command=self.login_user, width=250, height=40).pack(pady=(20, 10))
        ctk.CTkButton(login_frame, text="Create Account", command=self.register_user, fg_color="transparent", border_width=2, width=250, height=40).pack(pady=10)

    def register_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password: return
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            conn = sqlite3.connect("morse_database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Account created successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

    def login_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        conn = sqlite3.connect("morse_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
            self.current_user = username
            self.show_main_app()  
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    # ==========================================
    # 4. MAIN APP NAVIGATION
    # ==========================================
    def show_main_app(self):
        self.clear_window()
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) 
        ctk.CTkLabel(self.sidebar_frame, text="Blink Morse", font=("Roboto", 24, "bold")).grid(row=0, column=0, padx=20, pady=(30, 40))
        ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.view_dashboard, height=40).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Freestyle Mode", command=self.view_freestyle, height=40).grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Learning Mode", command=self.view_learning, height=40).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Logout", fg_color="#ab2c2c", hover_color="#852222", command=self.show_login_page, height=40).grid(row=5, column=0, padx=20, pady=20, sticky="s")
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.view_dashboard()

    def clear_main_frame(self):
        if hasattr(self, 'video_loop'): self.after_cancel(self.video_loop)
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        for widget in self.main_frame.winfo_children(): widget.destroy()

    # ==========================================
    # 5. DASHBOARD & DATA ANALYTICS
    # ==========================================
    def view_dashboard(self):
        self.app_mode = "dashboard"
        self.clear_main_frame()
        
        # Header
        ctk.CTkLabel(self.main_frame, text="Analytics Dashboard", font=("Roboto", 32, "bold")).pack(pady=(40, 5), anchor="w", padx=40)
        ctk.CTkLabel(self.main_frame, text=f"Welcome back, {self.current_user}. Track your Morse code mastery below.", font=("Roboto", 16)).pack(anchor="w", padx=40)

        # 1. Fetch Data using Pandas
        conn = sqlite3.connect("morse_database.db")
        query = "SELECT score, total, timestamp FROM quiz_scores WHERE username=? ORDER BY timestamp ASC"
        df = pd.read_sql_query(query, conn, params=(self.current_user,))
        conn.close()

        if df.empty:
            ctk.CTkLabel(self.main_frame, text="You haven't taken any quizzes yet!\nGo to Learning Mode to start tracking your progress.", 
                         font=("Roboto", 18, "italic"), text_color="gray").pack(pady=100)
            return

        # 2. Process Data
        df['accuracy'] = (df['score'] / df['total']) * 100
        df['quiz_number'] = range(1, len(df) + 1)
        
        total_quizzes = len(df)
        avg_accuracy = df['accuracy'].mean()
        best_score = f"{df['score'].max()}/{df.loc[df['score'].idxmax(), 'total']}"

        # 3. Top Stats Cards
        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=40, pady=30)
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Total Quizzes
        card1 = ctk.CTkFrame(stats_frame, corner_radius=10, fg_color="#1f538d")
        card1.grid(row=0, column=0, padx=10, sticky="nsew")
        ctk.CTkLabel(card1, text="Total Quizzes", font=("Roboto", 16)).pack(pady=(20, 5))
        ctk.CTkLabel(card1, text=f"{total_quizzes}", font=("Roboto", 36, "bold"), text_color="#00ffcc").pack(pady=(0, 20))

        # Card 2: Average Accuracy
        card2 = ctk.CTkFrame(stats_frame, corner_radius=10, fg_color="#1f538d")
        card2.grid(row=0, column=1, padx=10, sticky="nsew")
        ctk.CTkLabel(card2, text="Average Accuracy", font=("Roboto", 16)).pack(pady=(20, 5))
        ctk.CTkLabel(card2, text=f"{avg_accuracy:.1f}%", font=("Roboto", 36, "bold"), text_color="#00ffcc").pack(pady=(0, 20))

        # Card 3: Best Score
        card3 = ctk.CTkFrame(stats_frame, corner_radius=10, fg_color="#1f538d")
        card3.grid(row=0, column=2, padx=10, sticky="nsew")
        ctk.CTkLabel(card3, text="Best Score", font=("Roboto", 16)).pack(pady=(20, 5))
        ctk.CTkLabel(card3, text=f"{best_score}", font=("Roboto", 36, "bold"), text_color="#00ffcc").pack(pady=(0, 20))

        # 4. Generate Matplotlib Graph
        fig = Figure(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor('#2b2b2b') # Match CustomTkinter dark mode!
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')
        
        # Plot the line
        ax.plot(df['quiz_number'], df['accuracy'], marker='o', color='#00ffcc', linewidth=2, markersize=8)
        
        # Style the graph
        ax.set_title('Learning Mode Accuracy Over Time', color='white', fontsize=14, pad=15)
        ax.set_xlabel('Quiz Attempt', color='white')
        ax.set_ylabel('Accuracy (%)', color='white')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylim(-5, 105)
        
        # Ensure x-axis only shows whole numbers for quizzes (1, 2, 3...)
        from matplotlib.ticker import MaxNLocator
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        # 5. Embed Graph into CustomTkinter
        graph_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="gray15")
        graph_frame.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ==========================================
    # 6. FREESTYLE MODE 
    # ==========================================
    def view_freestyle(self):
        self.app_mode = "freestyle"
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.main_frame, text="Freestyle Mode", font=("Roboto", 32, "bold")).grid(row=0, column=0, pady=(20, 5), padx=40, sticky="w")
        
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40)
        content_frame.grid_columnconfigure(0, weight=3) 
        content_frame.grid_columnconfigure(1, weight=1) 

        self.video_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        self.video_frame.grid(row=0, column=0, pady=10, sticky="nsew")
        self.video_label = ctk.CTkLabel(self.video_frame, text="") 
        self.video_label.pack(pady=10)

        self.tabs = ctk.CTkTabview(content_frame, width=250, corner_radius=10)
        self.tabs.grid(row=0, column=1, pady=10, padx=(20, 0), sticky="nsew")
        tab_commands = self.tabs.add("Commands")
        tab_dict = self.tabs.add("Dictionary")

        commands_list = [(".. --", "Accept Guess"), (".....", "Delete Letter"), ("----", "Delete Word"), ("......", "Clear Screen")]
        for morse, action in commands_list:
            ctk.CTkLabel(tab_commands, text=f"{morse}", font=("Roboto", 18, "bold"), text_color="#00ffcc").pack(pady=(10, 0))
            ctk.CTkLabel(tab_commands, text=f"{action}", font=("Roboto", 14)).pack(pady=(0, 10))

        dict_scroll = ctk.CTkScrollableFrame(tab_dict, fg_color="transparent")
        dict_scroll.pack(fill="both", expand=True)
        for ascii_val in range(65, 91): 
            letter = chr(ascii_val)
            morse = self.LETTER_TO_MORSE.get(letter, "")
            ctk.CTkLabel(dict_scroll, text=f"{letter}   {morse}", font=("Roboto", 16, "bold")).pack(pady=2, anchor="w", padx=20)

        self.output_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="gray15")
        self.output_frame.grid(row=2, column=0, pady=(0, 20), padx=40, sticky="ew")
        self.ui_morse_label = ctk.CTkLabel(self.output_frame, text="Morse: ", font=("Roboto", 20, "bold"), text_color="#00ffcc")
        self.ui_morse_label.pack(pady=(10, 0))
        self.ui_prediction_label = ctk.CTkLabel(self.output_frame, text="Guess: ...", font=("Roboto", 20, "italic"), text_color="yellow")
        self.ui_prediction_label.pack(pady=5)
        self.ui_text_label = ctk.CTkLabel(self.output_frame, text="Text: ", font=("Roboto", 28, "bold"))
        self.ui_text_label.pack(pady=(5, 10))

        self.reset_metrics()
        self.cap = cv2.VideoCapture(0)
        self.update_frame() 

    # ==========================================
    # 7. LEARNING MODE 
    # ==========================================
    def view_learning(self):
        self.app_mode = "learning"
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.main_frame, text="Learning Mode: Flashcards", font=("Roboto", 32, "bold")).grid(row=0, column=0, pady=(20, 5), padx=40, sticky="w")
        
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40)
        content_frame.grid_columnconfigure(0, weight=2) 
        content_frame.grid_columnconfigure(1, weight=1) 

        self.video_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        self.video_frame.grid(row=0, column=0, pady=10, sticky="nsew")
        self.video_label = ctk.CTkLabel(self.video_frame, text="") 
        self.video_label.pack(pady=10)

        quiz_frame = ctk.CTkFrame(content_frame, corner_radius=10, fg_color="#1c4b82")
        quiz_frame.grid(row=0, column=1, pady=10, padx=(20, 0), sticky="nsew")
        
        self.quiz_score = 0
        self.quiz_total = 0
        self.target_letter = random.choice(self.ALPHABET)

        self.ui_score_label = ctk.CTkLabel(quiz_frame, text="Score: 0 / 0", font=("Roboto", 24, "bold"))
        self.ui_score_label.pack(pady=(30, 20))

        ctk.CTkLabel(quiz_frame, text="Blink the letter:", font=("Roboto", 18)).pack(pady=(10, 0))
        self.ui_target_label = ctk.CTkLabel(quiz_frame, text=self.target_letter, font=("Roboto", 80, "bold"), text_color="#00ffcc")
        self.ui_target_label.pack(pady=10)

        self.ui_feedback_label = ctk.CTkLabel(quiz_frame, text="Waiting for input...", font=("Roboto", 18, "italic"))
        self.ui_feedback_label.pack(pady=20)

        self.output_frame = ctk.CTkFrame(self.main_frame, height=80, corner_radius=10, fg_color="gray15")
        self.output_frame.grid(row=2, column=0, pady=(0, 20), padx=40, sticky="ew")
        self.ui_morse_label = ctk.CTkLabel(self.output_frame, text="Your Input: ", font=("Roboto", 24, "bold"), text_color="#00ffcc")
        self.ui_morse_label.pack(pady=20)

        save_btn = ctk.CTkButton(quiz_frame, text="Finish & Save Score", fg_color="#28a745", hover_color="#218838", command=self.save_quiz)
        save_btn.pack(side="bottom", pady=30)

        self.reset_metrics()
        self.cap = cv2.VideoCapture(0)
        self.update_frame() 

    def save_quiz(self):
        if self.quiz_total > 0:
            conn = sqlite3.connect("morse_database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO quiz_scores (username, score, total) VALUES (?, ?, ?)", 
                           (self.current_user, self.quiz_score, self.quiz_total))
            conn.commit()
            conn.close()
            messagebox.showinfo("Quiz Saved", f"Saved! You scored {self.quiz_score}/{self.quiz_total}.")
        self.view_dashboard()

    # ==========================================
    # 8. MASTER VIDEO LOOP 
    # ==========================================
    def reset_metrics(self):
        self.is_calibrated = False
        self.calibration_start_time = time.time()
        self.calibration_ears = []
        self.EAR_THRESHOLD = 0.0
        self.blink_start_time = 0
        self.is_blinking = False
        self.last_blink_end_time = time.time()
        self.current_morse = ""
        self.current_text = ""
        self.predicted_word = ""

    def update_frame(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                h_img, w_img, _ = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    if len(results.multi_face_landmarks) > 1:
                        cv2.rectangle(rgb_frame, (30, 10), (610, 50), (255, 0, 0), -1)
                        cv2.putText(rgb_frame, "WARNING: MULTIPLE FACES DETECTED", (60, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                        
                    face_landmarks = results.multi_face_landmarks[0] 
                    left_ear = calculate_EAR(self.LEFT_EYE, face_landmarks.landmark, w_img, h_img)
                    right_ear = calculate_EAR(self.RIGHT_EYE, face_landmarks.landmark, w_img, h_img)
                    avg_ear = (left_ear + right_ear) / 2.0

                    if not self.is_calibrated:
                        self.calibration_ears.append(avg_ear)
                        time_left = 5.0 - (time.time() - self.calibration_start_time)
                        if time_left > 0:
                            cv2.putText(rgb_frame, f"CALIBRATING... Keep eyes open: {int(time_left)}s", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                        else:
                            self.EAR_THRESHOLD = (sum(self.calibration_ears) / len(self.calibration_ears)) * 0.75
                            self.is_calibrated = True
                            self.last_blink_end_time = time.time()
                            if self.app_mode == "learning":
                                self.speak_text(f"Blink the letter {self.target_letter}")
                    
                    else:
                        if avg_ear < self.EAR_THRESHOLD:
                            if not self.is_blinking:
                                self.is_blinking = True
                                self.blink_start_time = time.time()
                        else:
                            if self.is_blinking:
                                self.is_blinking = False
                                blink_duration = time.time() - self.blink_start_time
                                self.last_blink_end_time = time.time()
                                
                                if blink_duration < 0.5: self.current_morse += "."
                                else: self.current_morse += "-"
                                
                                if self.app_mode == "freestyle": self.ui_morse_label.configure(text=f"Morse: {self.current_morse}")
                                elif self.app_mode == "learning": self.ui_morse_label.configure(text=f"Your Input: {self.current_morse}")

                        pause_time = time.time() - self.last_blink_end_time

                        if self.app_mode == "freestyle":
                            if pause_time > 2.0 and self.current_morse != "":
                                if self.current_morse == ".....":
                                    if len(self.current_text) > 0:
                                        self.current_text = self.current_text[:-1]
                                        if len(self.current_text) > 0 and self.current_text[-1] == " ": self.current_text = self.current_text[:-1] 
                                    self.predicted_word = ""
                                elif self.current_morse == "......":
                                    self.current_text = ""
                                    self.predicted_word = ""
                                elif self.current_morse == "----":
                                    if len(self.current_text.strip()) > 0:
                                        words = self.current_text.strip().split(" ")
                                        words.pop()
                                        self.current_text = " ".join(words) + " " if words else ""
                                    self.predicted_word = ""
                                elif self.current_morse == "..--":
                                    if self.predicted_word:
                                        words = self.current_text.strip().split(" ")
                                        if words: words.pop()
                                        self.current_text = " ".join(words) + " " + self.predicted_word + " " if words else self.predicted_word + " "
                                        self.speak_text(self.predicted_word)
                                        self.predicted_word = ""
                                else:
                                    letter = self.MORSE_DICT.get(self.current_morse, "")
                                    if letter:
                                        self.current_text += letter
                                        current_word = self.current_text.split(" ")[-1]
                                        self.predicted_word = ""
                                        if len(current_word) >= 2:
                                            matches = [w for w in self.english_words if w.startswith(current_word) and len(w) > len(current_word)]
                                            if matches: self.predicted_word = matches[0]
                                    
                                self.current_morse = ""
                                self.ui_morse_label.configure(text="Morse: ")
                                self.ui_prediction_label.configure(text=f"Guess: {self.predicted_word} (..--) to accept" if self.predicted_word else "Guess: ...")
                                self.ui_text_label.configure(text=f"Text: {self.current_text}")
                                self.last_blink_end_time = time.time() 

                            if pause_time > 4.0 and len(self.current_text) > 0 and self.current_text[-1] != " ":
                                words = self.current_text.split()
                                last_word = words[-1] if words else ""
                                self.current_text += " "
                                self.predicted_word = ""
                                if last_word: self.speak_text(last_word)
                                self.ui_prediction_label.configure(text="Guess: ...")
                                self.ui_text_label.configure(text=f"Text: {self.current_text}")
                                self.last_blink_end_time = time.time() 

                        elif self.app_mode == "learning":
                            if pause_time > 2.0 and self.current_morse != "":
                                correct_morse = self.LETTER_TO_MORSE[self.target_letter]
                                self.quiz_total += 1
                                if self.current_morse == correct_morse:
                                    self.quiz_score += 1
                                    self.ui_feedback_label.configure(text="Correct! 🎉", text_color="#00ffcc")
                                    self.speak_text("Correct")
                                else:
                                    self.ui_feedback_label.configure(text=f"Wrong! {self.target_letter} is {correct_morse}", text_color="#ff4444")
                                    self.speak_text("Incorrect")

                                self.ui_score_label.configure(text=f"Score: {self.quiz_score} / {self.quiz_total}")
                                self.target_letter = random.choice(self.ALPHABET)
                                self.ui_target_label.configure(text=self.target_letter)
                                self.current_morse = ""
                                self.ui_morse_label.configure(text="Your Input: ")
                                self.last_blink_end_time = time.time()

                        for pt in self.LEFT_EYE + self.RIGHT_EYE:
                            pos = face_landmarks.landmark[pt]
                            cv2.circle(rgb_frame, (int(pos.x * w_img), int(pos.y * h_img)), 2, (0, 255, 0), -1)

                img = Image.fromarray(rgb_frame)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
                self.video_label.configure(image=ctk_img)
                self.video_label.image = ctk_img

            self.video_loop = self.after(15, self.update_frame)

if __name__ == "__main__":
    setup_database()
    app = BlinkMorseApp()
    app.mainloop()