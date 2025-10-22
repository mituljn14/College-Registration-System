from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'student'

mysql = MySQL(app)

# ---------------- LOGIN PAGE ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid Username or Password!', 'danger')

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ---------------- Home (after login) ----------------
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


# ---------------- Professor routes ----------------
@app.route('/professor', methods=['GET', 'POST'])
def professor():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        search_name = request.form['search_name'].lower()
        cur.execute("SELECT * FROM professor WHERE LOWER(name) = %s", (search_name,))
    else:
        cur.execute("SELECT * FROM professor")

    data = cur.fetchall()
    cur.close()
    return render_template('professor.html', professors=data)


# ---------------- Department routes ----------------
@app.route('/department', methods=['GET', 'POST'])
def department():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        search_name = request.form['search_name'].lower()
        cur.execute("""
            SELECT d.dep_id, d.name, p.name
            FROM department d
            LEFT JOIN professor p ON d.professor_id = p.professor_id
            WHERE LOWER(d.name) = %s
        """, (search_name,))
    else:
        cur.execute("""
            SELECT d.dep_id, d.name, p.name
            FROM department d
            LEFT JOIN professor p ON d.professor_id = p.professor_id
        """)

    data = cur.fetchall()
    cur.close()
    return render_template('department.html', departments=data)


# ---------------- Student routes ----------------
@app.route('/student', methods=['GET', 'POST'])
def student():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    message = ""

    if request.method == 'POST' and 'search_name' in request.form:
        search_name = request.form['search_name'].strip().lower()
        cur.execute("SELECT * FROM student WHERE LOWER(name) LIKE %s", ('%' + search_name + '%',))
    else:
        cur.execute("SELECT * FROM student")

    users = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM student")
    student_count = cur.fetchone()[0]
    cur.close()
    return render_template('student.html', users=users, student_count=student_count, message=message)


# ---------------- Add Student ----------------
@app.route('/add_student', methods=['POST'])
def add_student():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    prn = int(request.form['prn'])
    name = request.form['name']
    email = request.form['email']
    gpa = float(request.form['gpa']) if request.form['gpa'] else None
    year = int(request.form['year']) if request.form['year'] else None
    panel = request.form['panel']
    mobile_no = request.form['mobile_no']
    blood_group = request.form['blood_group']
    branch = request.form['branch']

    cur.callproc('InsertStudent', [prn, name, email, gpa, year, panel, mobile_no, blood_group, branch])
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('student'))


# ---------------- Courses ----------------
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        course_id = request.form['course_id']
        title = request.form['title']
        description = request.form['description']
        dep_id = request.form['dep_id']

        cur.callproc('InsertCourse', (course_id, title, description, dep_id))
        mysql.connection.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('courses'))

    cur.execute("SELECT * FROM course")
    courses = cur.fetchall()
    return render_template('courses.html', courses=courses)


@app.route('/delete_course/<int:course_id>')
def delete_course(course_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM course WHERE course_id = %s", (course_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('courses'))


# ---------------- Semester ----------------
@app.route('/semester', methods=['GET', 'POST'])
def semester():
    if 'username' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        search_branch = request.form['search_branch'].lower()
        cursor.execute("""
            SELECT sem_id, sem_number, start_date, end_date, branch_name
            FROM semester
            WHERE LOWER(branch_name) = %s
        """, (search_branch,))
    else:
        cursor.execute("""
            SELECT sem_id, sem_number, start_date, end_date, branch_name
            FROM semester
        """)

    semesters = cursor.fetchall()
    cursor.close()
    return render_template('semester.html', semesters=semesters)


# ---------------- Enrollment ----------------
@app.route('/enrollments', methods=['GET', 'POST'])
def enrollment():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        search_prn = request.form.get('search_prn')
        search_course = request.form.get('search_course')

        query = """
            SELECT e.enrollment_id, s.prn, s.name, c.title, e.enroll_date
            FROM enrollment e
            JOIN student s ON e.prn = s.prn
            JOIN course c ON e.course_id = c.course_id
            WHERE (%s IS NULL OR s.prn = %s)
            AND (%s IS NULL OR c.title LIKE %s)
        """
        cur.execute(query, (search_prn, search_prn, search_course, f"%{search_course}%" if search_course else None))
    else:
        query = """
            SELECT e.enrollment_id, s.prn, s.name, c.title, e.enroll_date
            FROM enrollment e
            JOIN student s ON e.prn = s.prn
            JOIN course c ON e.course_id = c.course_id
        """
        cur.execute(query)

    enrollments = cur.fetchall()
    cur.close()
    return render_template('enrollment.html', enrollments=enrollments)


# ---------------- Main ----------------
if __name__ == '__main__':
    app.run(debug=True, port=8000)
