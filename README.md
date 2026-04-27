# AI-Powered Multimodal Learning and Communication System

An intelligent desktop application that combines **Sign Language Learning** and **Blink Morse Interaction** into one platform using Artificial Intelligence, Computer Vision, and Machine Learning.

This project is designed as an **interactive learning system** to help users understand alternative communication methods, practice sign language, explore blink-based coded inputs, and experience real-time AI recognition.

---

# 🚀 Features

## 🔹 Sign Language Module
- Real-time A-Z hand sign recognition using webcam
- Word formation from predicted letters
- Multilingual translation:
  - English
  - Hindi
  - Kannada
  - Telugu
  - Tamil
- Learning Mode for alphabet practice
- Quiz Mode for interactive testing
- Confidence score display
- Dashboard with metrics and training graph

## 🔹 Blink Morse Module
- Eye blink detection using webcam
- Morse code generation from blink patterns
- Text conversion
- Security-oriented blink pattern concept
- Alternative human-computer interaction demo

---

# 🧠 Technologies Used

| Category | Tools / Frameworks |
|--------|-------------------|
| Language | Python |
| Computer Vision | OpenCV |
| Landmark Detection | MediaPipe |
| Machine Learning | XGBoost |
| GUI | CustomTkinter |
| Translation | Deep Translator |
| Data Processing | NumPy, JSON |

---

# 🏗️ System Architecture

```text
Webcam Input
   ↓
OpenCV Frame Capture
   ↓
MediaPipe Landmark Detection
   ↓
Machine Learning Model (XGBoost)
   ↓
Prediction Output
   ↓
UI Display / Translation / Quiz / Dashboard