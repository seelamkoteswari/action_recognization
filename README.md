

# 🚀 Real-Time Human Action Recognition System

A web-based application that detects human actions in real-time using a webcam. Built with Flask, OpenCV, and MediaPipe, this project identifies basic human movements and stores user-specific action history.

---

## 📌 Features

- 🔐 User Authentication (Login & Register)
- 🎥 Live Webcam Streaming
- 🧍 Real-Time Pose Detection using MediaPipe
- ⚡ Action Recognition (Rule-based):
  - Standing
  - Sitting
  - Walking
  - Running
  - Jumping
  - Clapping
  - Waving
  - Hands Up / Down
- ▶️ Start / Stop Camera Control
- 🗂️ User-wise Action History
- ⏱️ Auto-save actions every 5 seconds

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask  
- **Computer Vision:** OpenCV, MediaPipe  
- **Database:** SQLite  
- **Frontend:** HTML, CSS, JavaScript  

---

## 📂 Project Structure
project/
│── app.py
│── requirements.txt
│── README.md
│── templates/
│ ├── login.html
│ ├── register.html
│ ├── dashboard.html
│ ├── history.html


---

## ▶️ Installation & Setup

### 1️⃣ Clone Repository
git clone https://github.com/seelamkoteswari/action_recognization.git
cd action_recognization


### 2️⃣ Install Dependencies
pip install -r requirements.txt


### 3️⃣ Run Application
python app.py


### 4️⃣ Open in Browser
http://127.0.0.1:5000/


---

## 🚀 How It Works

1. User logs into the system  
2. Webcam captures live video  
3. MediaPipe detects body landmarks  
4. Custom logic identifies actions  
5. Actions are displayed in real-time  
6. Every 5 seconds, actions are saved  
7. Users can view their action history  

---

## ⚠️ Limitations

- Detects only predefined actions  
- Rule-based logic (not AI/deep learning model)  
- Accuracy depends on lighting and camera quality  

---

## 🔮 Future Improvements

- Add timestamps to action history  
- Improve detection using deep learning models  
- Add analytics dashboard  
- Enhance UI/UX design  
- Deploy as a live web application  

---

## 👩‍💻 Author

**Koteswari Seelam**

---

## ⭐ Support

If you found this project helpful, please give it a ⭐ on GitHub!
