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


@app.route('/professor', methods=['GET', 'POST'])
def professor():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Use DictCursor to fetch results as dictionaries (e.g., prof['name'])
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        # Improved search: using LIKE for partial matches
        search_name = request.form['search_name'].strip().lower()
        search_term = '%' + search_name + '%'

        cur.execute("""
            SELECT p.professor_id, p.name, p.email, d.name AS department_name
            FROM professor p
            LEFT JOIN department d ON p.dep_id = d.dep_id
            WHERE LOWER(p.name) LIKE %s
            ORDER BY p.name
        """, (search_term,))
    else:
        # Fetch all professors, joining to get the department name
        cur.execute("""
            SELECT p.professor_id, p.name, p.email, d.name AS department_name
            FROM professor p
            LEFT JOIN department d ON p.dep_id = d.dep_id
            ORDER BY p.professor_id DESC
        """)

    data = cur.fetchall()
    cur.close()
    return render_template('professor.html', professors=data)

@app.route('/add_professor', methods=['POST'])
def add_professor():
    if 'username' not in session:
        return redirect(url_for('login'))

    professor_id = request.form.get('professor_id')
    name = request.form.get('name')
    email = request.form.get('email')
    dep_id = request.form.get('dep_id') or None  # Optional department

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO professor (professor_id, name, email, dep_id)
            VALUES (%s, %s, %s, %s)
        """, (professor_id, name, email, dep_id))
        mysql.connection.commit()
        flash("✅ Professor added successfully!", "success")
    except MySQLdb.IntegrityError:
        flash("❌ Professor ID or Email already exists.", "danger")
    finally:
        cur.close()

    return redirect(url_for('professor'))

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

@app.route('/delete_student', methods=['POST'])
def delete_student():
    if 'username' not in session:
        return redirect(url_for('login'))

    prn = int(request.form['prn'])

    cur = mysql.connection.cursor()
    cur.callproc('DeleteStudent', [prn])
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

@app.route('/professor_attendance/<int:professor_id>', methods=['GET', 'POST'])
def professor_attendance(professor_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get professor
    cur.execute("SELECT * FROM professor WHERE professor_id = %s", (professor_id,))
    professor = cur.fetchone()
    if not professor:
        flash('Professor not found.', 'danger')
        cur.close()
        return redirect(url_for('home'))

    # Get courses taught by professor
    cur.execute("""
        SELECT c.course_id, c.title
        FROM course c
        JOIN teaches t ON c.course_id = t.course_id
        WHERE t.professor_id = %s
        ORDER BY c.title
    """, (professor_id,))
    courses = cur.fetchall()

    # ✅ Initialize search_query for both GET and POST
    search_query = request.args.get('search', '').strip()

    # Get students, filtered by Panel or PRN if search exists
    if search_query:
        cur.execute("""
            SELECT s.prn, s.name, s.panel, s.branch, s.email, s.year, s.attendance_percentage
            FROM student s
            WHERE s.professor_id = %s
            AND (s.panel LIKE %s OR CAST(s.prn AS CHAR) LIKE %s)
            ORDER BY s.prn ASC
        """, (professor_id, f"%{search_query}%", f"%{search_query}%"))
    else:
        cur.execute("""
            SELECT s.prn, s.name, s.panel, s.branch, s.email, s.year, s.attendance_percentage
            FROM student s
            WHERE s.professor_id = %s
            ORDER BY s.prn ASC
        """, (professor_id,))
    students = cur.fetchall()

    # Handle POST: attendance submission
    if request.method == 'POST':
        attendance_date = request.form.get('attendance_date')
        course_id = request.form.get('course_id')

        if not attendance_date or not course_id:
            flash('Please select a course and date.', 'warning')
            cur.close()
            return redirect(url_for('professor_attendance', professor_id=professor_id))

        try:
            # Insert new session
            cur.execute("""
                INSERT INTO attendance_session (course_id, professor_id, session_date, session_time)
                VALUES (%s, %s, %s, NOW())
            """, (course_id, professor_id, attendance_date))
            mysql.connection.commit()

            session_id = cur.lastrowid

            # Insert attendance for each student
            for s in students:
                prn = s['prn']
                status = 'Present' if request.form.get(f'status_{prn}') else 'Absent'
                cur.execute("""
                    INSERT INTO attendance_record (session_id, prn, status)
                    VALUES (%s, %s, %s)
                """, (session_id, prn, status))

            mysql.connection.commit()
            flash('Attendance saved successfully!', 'success')

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error saving attendance: {e}', 'danger')

        finally:
            cur.close()

        return redirect(url_for('professor_attendance', professor_id=professor_id))

    cur.close()
    return render_template('professor_attendance.html',
                           professor=professor,
                           students=students,
                           courses=courses,
                           search_query=search_query)


# ---------------- Main ----------------
if __name__ == '__main__':
    app.run(debug=True, port=8000)
