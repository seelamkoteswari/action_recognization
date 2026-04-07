from flask import Flask, render_template, request, redirect, session, Response, jsonify
import sqlite3
import cv2
import mediapipe as mp
import time
import numpy as np

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT
                )""")

    c.execute("""CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    action TEXT
                )""")

    conn.commit()
    conn.close()

init_db()

# ================= MEDIAPIPE =================
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

camera = cv2.VideoCapture(0)
camera_on = False   # start OFF
last_saved_time = 0

# ================= ACTION =================
def get_action(landmarks):
    ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
    rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
    lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y
    rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y
    lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
    rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y
    lk = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y
    rk = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y

    if lw < ls and rw < rs:
        return "Hands Up"
    elif lw < ls or rw < rs:
        return "Hand Raised"
    elif lh > lk and rh > rk:
        return "Sitting"
    elif abs(ls - lh) < 0.15:
        return "Standing"
    elif lh < lk:
        return "Bending"
    elif abs(lk - rk) > 0.1:
        return "Running"
    elif abs(lk - rk) > 0.05:
        return "Walking"
    elif lk < lh and rk < rh:
        return "Jumping"
    elif abs(lw - rw) < 0.03:
        return "Clapping"
    elif lw < ls and rw > rs:
        return "Waving"
    elif lw > lh and rw > rh:
        return "Hands Down"
    else:
        return "Unknown"

# ================= VIDEO =================
def generate_frames(username):
    global last_saved_time

    while True:
        try:
            if camera_on:
                success, frame = camera.read()

                if not success:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "Camera Error", (150, 250),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    frame = cv2.resize(frame, (640, 480))

                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    result = pose.process(image)

                    action = "No Person"

                    if result.pose_landmarks:
                        landmarks = result.pose_landmarks.landmark
                        action = get_action(landmarks)

                        mp_draw.draw_landmarks(
                            frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                        # 🔥 SAVE EVERY 5 SECONDS
                        current_time = time.time()

                        if current_time - last_saved_time > 5:
                            print("Saving:", username, action)  # debug

                            conn = sqlite3.connect("database.db")
                            c = conn.cursor()
                            c.execute("INSERT INTO history (username, action) VALUES (?, ?)",
                                      (username, action))
                            conn.commit()
                            conn.close()

                            last_saved_time = current_time

                    cv2.putText(frame, f'Action: {action}', (10, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            else:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera OFF", (180, 250),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)

            if not ret:
                continue

            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        except Exception as e:
            print("ERROR:", e)
            continue

# ================= ROUTES =================

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    user = request.form['username']
    pwd = request.form['password']

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
    data = c.fetchone()
    conn.close()

    if data:
        session['user'] = user
        return redirect('/dashboard')
    return "Invalid credentials"

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html')

@app.route('/video')
def video():
    if 'user' not in session:
        return "Unauthorized"

    return Response(generate_frames(session['user']),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera')
def start_camera():
    global camera_on
    camera_on = True
    return jsonify({"status": "started"})

@app.route('/stop_camera')
def stop_camera():
    global camera_on
    camera_on = False
    return jsonify({"status": "stopped"})

@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT action FROM history WHERE username=? ORDER BY id DESC LIMIT 20",
              (session['user'],))
    
    data = c.fetchall()
    conn.close()

    return render_template('history.html', data=data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)