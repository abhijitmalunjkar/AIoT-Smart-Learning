from flask import Flask, request, jsonify, render_template, redirect, url_for, Response
from flask_cors import CORS
import sqlite3
import random
import numpy as np
import csv
from io import StringIO
from datetime import datetime
import threading
from sklearn.linear_model import SGDRegressor

app = Flask(__name__)
CORS(app)

DB_NAME = "school.db"

# --- 1. INITIALIZE ML MODEL ---
ml_engine = SGDRegressor(max_iter=1000, tol=1e-3, warm_start=True, learning_rate='adaptive', eta0=0.1)
X_initial = np.array([[0.25, 0.1, 0.0], [0.75, 0.5, 0.4], [0.1, 0.05, 0.0], [1.0, 1.0, 1.0]])
y_initial = np.array([10, 5, 15, 2]) 
ml_engine.fit(X_initial, y_initial)

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, current_complexity INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS performance_logs (id INTEGER PRIMARY KEY, student_id INTEGER, subject TEXT, complexity INTEGER, time_taken REAL, hesitation REAL, fidget_score INTEGER, is_correct BOOLEAN, timestamp TEXT)''')
    
    c.execute("SELECT COUNT(*) FROM students")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO students (name, current_complexity) VALUES ('Demo Student', 5)")
    conn.commit()
    conn.close()

init_db()

# --- 3. MULTI-SUBJECT GENERATOR ---
def generate_question(subject, complexity_score):
    complexity = max(2, min(int(complexity_score), 20)) 
    
    if subject == "math":
        operator = "+" if complexity < 10 else random.choice(["+", "-"])
        if operator == "+":
            a = random.randint(1, max(1, complexity - 1))
            b = random.randint(1, max(1, complexity - a))
            return {"q": f"{a} + {b} = ?", "a": a + b, "type": "numpad", "emojis": "🍎 " * a + " +  🍎 " * b, "complexity": complexity}
        else:
            a = random.randint(2, complexity)
            b = random.randint(1, a - 1)
            return {"q": f"{a} - {b} = ?", "a": a - b, "type": "numpad", "emojis": "🚗 " * a + " -  🚗 " * b, "complexity": complexity}
            
    elif subject == "alphabet":
        letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return {"q": f"Draw the letter: {letter}", "a": letter, "type": "draw", "emojis": "✍️ 🔤", "complexity": complexity}
        
    elif subject == "shapes":
        shapes = ["Circle 🔴", "Line ➖", "Square 🟩", "Triangle 🔺", "Rectangle 🟦", "Star ⭐", "Hexagon 🛑", "Diamond 🔶"]
        shape = random.choice(shapes)
        return {"q": f"Draw a {shape}", "a": shape, "type": "draw", "emojis": "✍️ 🎨", "complexity": complexity}


# --- 4. TEACHER ADMIN DASHBOARD ROUTES ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['student_name']
        c.execute("INSERT INTO students (name, current_complexity) VALUES (?, 5)", (name,))
        conn.commit()
        return redirect(url_for('admin'))
    
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    c.execute('''SELECT s.name, p.subject, p.time_taken, p.hesitation, p.fidget_score, p.is_correct, p.timestamp, p.complexity 
                 FROM performance_logs p JOIN students s ON p.student_id = s.id ORDER BY p.id DESC LIMIT 50''')
    logs = c.fetchall()
    conn.close()
    return render_template('admin.html', students=students, logs=logs)


# --- MISSING ROUTE RESTORED: CSV EXPORT ---
@app.route('/export')
def export_csv():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT s.name, p.subject, p.complexity, p.time_taken, p.hesitation, p.fidget_score, p.is_correct, p.timestamp 
                 FROM performance_logs p JOIN students s ON p.student_id = s.id ORDER BY p.id DESC''')
    rows = c.fetchall()
    conn.close()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student Name', 'Subject', 'Complexity Level', 'Time Taken (s)', 'Hesitation (s)', 'Fidget Score', 'Correct Answer', 'Timestamp'])
    cw.writerows(rows)
    output = si.getvalue()
    
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=student_aiot_report.csv"})


# --- MISSING ROUTE RESTORED: CHART.JS GRAPH API ---
@app.route('/api/progress/<int:student_id>')
def get_progress(student_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT complexity, is_correct, timestamp FROM performance_logs WHERE student_id = ? ORDER BY id ASC", (student_id,))
    rows = c.fetchall()
    conn.close()
    
    # Package data cleanly for the Chart.js frontend
    data = [{"attempt": i+1, "complexity": r[0], "is_correct": r[1]} for i, r in enumerate(rows)]
    return jsonify(data)


# --- 5. STUDENT EDGE DEVICE ROUTES ---
@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/api/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name FROM students")
    students = [{"id": row[0], "name": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(students)

@app.route('/api/start/<int:student_id>/<subject>', methods=['GET'])
def start_session(student_id, subject):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT current_complexity FROM students WHERE id = ?", (student_id,))
    complexity = c.fetchone()[0]
    conn.close()
    question = generate_question(subject, complexity)
    return jsonify({"level": f"C-{question['complexity']}", "question": question})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    student_id = data['student_id']
    subject = data['subject']
    is_correct = data['is_correct']
    time_taken = data['time_taken']
    hesitation = data['hesitation']
    fidget_score = data['fidget_score']
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT current_complexity FROM students WHERE id = ?", (student_id,))
    current_complexity = c.fetchone()[0]
    
    # ML Normalization
    norm_time = min(time_taken / 20.0, 1.0)
    norm_hesitation = min(hesitation / 10.0, 1.0)
    norm_fidget = min(fidget_score / 10.0, 1.0)
    X_new = np.array([[norm_time, norm_hesitation, norm_fidget]])
    
    if is_correct: target_y = current_complexity + 1.0 + (1.0 / max(0.1, norm_time)) 
    else: target_y = current_complexity - 1.0 - norm_fidget - norm_hesitation

    ml_engine.partial_fit(X_new, np.array([target_y]))
    predicted_complexity = ml_engine.predict(X_new)[0]
    
    jump = max(-2, min(2, round(predicted_complexity - current_complexity)))
    if is_correct and jump <= 0: jump = 1
    elif not is_correct and jump >= 0: jump = -1
        
    new_complexity = max(2, min(int(current_complexity + jump), 20))
    insight = f"Adjusted {jump} levels to Complexity: {new_complexity}"

    c.execute("UPDATE students SET current_complexity = ? WHERE id = ?", (new_complexity, student_id))
    c.execute("INSERT INTO performance_logs (student_id, subject, complexity, time_taken, hesitation, fidget_score, is_correct, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
              (student_id, subject, current_complexity, time_taken, hesitation, fidget_score, is_correct, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    
    next_q = generate_question(subject, new_complexity)
    return jsonify({"insight": insight, "new_level": f"C-{next_q['complexity']}", "next_question": next_q})


# --- 6. DUAL STACK SERVER THREADING ---
if __name__ == '__main__':
    print("\n🚀 Starting AIoT Dual-Stack Server with HTTPS...")
    
    def run_ipv4():
        app.run(host='0.0.0.0', port=5000, ssl_context='adhoc', debug=False, use_reloader=False)

    def run_ipv6():
        app.run(host='::', port=5001, ssl_context='adhoc', debug=False, use_reloader=False)

    threading.Thread(target=run_ipv4).start()
    run_ipv6()