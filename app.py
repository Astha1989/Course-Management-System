from flask import Flask, render_template, request, redirect, url_for, session
import json, os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATA_DIR = 'data'

# ---------------------- HELPERS ----------------------

def load_data(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(os.path.join(DATA_DIR, filename), 'w') as f:
        json.dump(data, f, indent=4)

# ---------------------- CORE ROUTES ----------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_data('users.json')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['user'] = username
            session['role'] = users[username]['role']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'], role=session['role'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------------------- ADMIN: MAINTAIN STUDENTS ----------------------

@app.route('/admin/students', methods=['GET', 'POST'])
def manage_students():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    students = load_data('students.json')
    if request.method == 'POST':
        sid = request.form['id']
        name = request.form['name']
        cls = request.form['class']
        email = request.form['email']
        students[sid] = {'name': name, 'class': cls, 'email': email}
        save_data('students.json', students)
    return render_template('manage_students.html', students=students)

@app.route('/admin/students/delete/<sid>')
def delete_student(sid):
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    students = load_data('students.json')
    students.pop(sid, None)
    save_data('students.json', students)
    return redirect(url_for('manage_students'))

# ---------------------- ADMIN: MAINTAIN FACULTY ----------------------

@app.route('/admin/faculty', methods=['GET', 'POST'])
def manage_faculty():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    faculty = load_data('faculty.json')
    if request.method == 'POST':
        fid = request.form['id']
        name = request.form['name']
        dept = request.form['department']
        email = request.form['email']
        faculty[fid] = {'name': name, 'department': dept, 'email': email}
        save_data('faculty.json', faculty)
    return render_template('manage_faculty.html', faculty=faculty)

@app.route('/admin/faculty/delete/<fid>')
def delete_faculty(fid):
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    faculty = load_data('faculty.json')
    faculty.pop(fid, None)
    save_data('faculty.json', faculty)
    return redirect(url_for('manage_faculty'))

# ---------------------- ADMIN: MAINTAIN COURSES ----------------------

@app.route('/admin/courses', methods=['GET', 'POST'])
def manage_courses():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    courses = load_data('courses.json')
    if request.method == 'POST':
        cid = request.form['id']
        name = request.form['name']
        dept = request.form['department']
        instructor = request.form['instructor']
        courses[cid] = {'name': name, 'department': dept, 'instructor': instructor}
        save_data('courses.json', courses)
    return render_template('manage_courses.html', courses=courses)

@app.route('/admin/courses/delete/<cid>')
def delete_course(cid):
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    courses = load_data('courses.json')
    courses.pop(cid, None)
    save_data('courses.json', courses)
    return redirect(url_for('manage_courses'))

# ---------------------- STUDENT FUNCTIONALITIES ----------------------

@app.route('/student/download')
def student_download():
    if session.get('role') != 'student':
        return redirect(url_for('dashboard'))
    materials = load_data('materials.json')
    return render_template('student_download.html', materials=materials)

@app.route('/student/submit', methods=['GET', 'POST'])
def student_submit():
    if session.get('role') != 'student':
        return redirect(url_for('dashboard'))
    submissions = load_data('submissions.json')
    if request.method == 'POST':
        course = request.form['course']
        student = session['user']
        content = request.form['content']
        submissions.setdefault(course, {})[student] = content
        save_data('submissions.json', submissions)
    return render_template('student_submit.html')

@app.route('/student/attendance')
def student_attendance():
    if session.get('role') != 'student':
        return redirect(url_for('dashboard'))
    attendance = load_data('attendance.json')
    student = session['user']
    return render_template('student_attendance.html', attendance=attendance.get(student, {}))

@app.route('/student/classmates')
def student_classmates():
    if session.get('role') != 'student':
        return redirect(url_for('dashboard'))
    students = load_data('students.json')
    return render_template('student_classmates.html', students=students)

# ---------------------- FACULTY FUNCTIONALITIES ----------------------

@app.route('/faculty/upload_material', methods=['GET', 'POST'])
def faculty_upload_material():
    if session.get('role') != 'faculty':
        return redirect(url_for('dashboard'))
    materials = load_data('materials.json')
    if request.method == 'POST':
        course = request.form['course']
        title = request.form['title']
        content = request.form['content']
        materials.setdefault(course, []).append({'title': title, 'content': content})
        save_data('materials.json', materials)
    return render_template('faculty_upload_material.html')

@app.route('/faculty/grade', methods=['GET', 'POST'])
def faculty_grade():
    if session.get('role') != 'faculty':
        return redirect(url_for('dashboard'))
    submissions = load_data('submissions.json')
    if request.method == 'POST':
        course = request.form['course']
        student = request.form['student']
        grade = request.form['grade']
        submissions.setdefault(course, {}).setdefault('grades', {})[student] = grade
        save_data('submissions.json', submissions)
    return render_template('faculty_grade.html', submissions=submissions)

@app.route('/faculty/upload_assignment', methods=['GET', 'POST'])
def faculty_upload_assignment():
    if session.get('role') != 'faculty':
        return redirect(url_for('dashboard'))
    assignments = load_data('assignments.json')
    if request.method == 'POST':
        course = request.form['course']
        title = request.form['title']
        description = request.form['description']
        assignments.setdefault(course, []).append({'title': title, 'description': description})
        save_data('assignments.json', assignments)
    return render_template('faculty_upload_assignment.html')

@app.route('/faculty/average')
def faculty_avg_perf():
    if session.get('role') != 'faculty':
        return redirect(url_for('dashboard'))
    submissions = load_data('submissions.json')
    course_averages = {}
    for course, content in submissions.items():
        grades = content.get('grades', {})
        if grades:
            avg = sum(int(v) for v in grades.values()) / len(grades)
            course_averages[course] = round(avg, 2)
    return render_template('faculty_avg_perf.html', averages=course_averages)

@app.route('/faculty/reports')
def faculty_reports():
    if session.get('role') != 'faculty':
        return redirect(url_for('dashboard'))
    attendance = load_data('attendance.json')
    submissions = load_data('submissions.json')
    return render_template('faculty_reports.html', attendance=attendance, submissions=submissions)

# ---------------------- RUN APP ----------------------

if __name__ == '__main__':
    app.run(debug=True)

