#!/usr/bin/python3
import os
from flask import Flask, render_template, request, redirect
import sqlite3

# Database name 
DATABASE_NAME            = 'grid.db'    # name of the database
TABLE_CLASSROOMS         = 'classrooms' # name of the table to classrooms
TABLE_TEACHERS           = 'teachers'   # name of the table to teachers
TABLE_MATTERS            = 'matters'    # name of the table to matters
TABLE_TEACHER_MATTERS    = 'teacher_matters' # name of the table to teacher matters
TABLE_CLASSROOM_TEACHERS = 'classroom_teachers' # name of the table to classroom teachers

# Array with all tables
tables = [TABLE_CLASSROOMS, TABLE_TEACHERS, TABLE_MATTERS,TABLE_TEACHER_MATTERS, TABLE_CLASSROOM_TEACHERS]

# Define app
app = Flask(__name__)

# Index page
@app.route('/')
def index():
    # Read record classrooms
    with sqlite3.connect(DATABASE_NAME) as _db:
        # Query classrooms
        cursor = _db.execute('SELECT id, name, grade FROM classrooms;')
        classrooms = list(cursor)
        cursor.close()
    return render_template('index.html',classrooms=classrooms)

# Teacheas page
@app.route('/teachers')
def teachers():
    # Read recorded teachers
    with sqlite3.connect(DATABASE_NAME) as _db:
        # Query teachers
        cursor = _db.execute('SELECT id, name FROM teachers;')
        teachers = list(cursor)
        cursor.close()
    return render_template('teachers.html',teachers=teachers)

# Matters page
@app.route('/matters')
def matters():
    # Read recorded matters
    with sqlite3.connect(DATABASE_NAME)  as _db:
        # Query matters
        cursor = _db.execute('SELECT id, name FROM matters;')
        # Turn to list
        matters = list(cursor)
        cursor.close()
    return render_template('matters.html',matters=matters)
# Teacher's matters
@app.route('/teacher_matters')
def teacher_matters():
    # Get teacher id
    teacher_id = request.args.get("id")
    # Get teacher name
    teacher_name = request.args.get("name")
    # Connect to main database
    with sqlite3.connect(DATABASE_NAME) as _db:
        cursor = _db.cursor()
        # Get teacher's matters
        cursor.execute('SELECT id, matter_id FROM teacher_matters WHERE teacher_id = ' + teacher_id)
        matters = list(cursor)
        named_matters = []
        # Get matters names
        for matter in matters:
            name = list(cursor.execute('SELECT name FROM ' + TABLE_MATTERS + ' WHERE id = %d'%(matter[1])))[0][0]
            named_matter = [*matter, name]
            named_matters.append(named_matter)
        matters = named_matters
        # Get school's matters
        cursor.execute('SELECT id, name FROM matters')
        school_matters = list(cursor)
        cursor.close()
    return render_template('teacher_matters.html',matters=matters,teacher_id=teacher_id,teacher_name=teacher_name,school_matters=school_matters)

# Classroom's teachers
@app.route("/classroom_teachers")
def classroom_teachers():
    # Get classroom id
    classroom_id = request.args.get('classroom_id')
    # Get classroom name
    classroom_name = request.args.get('classroom_name')
    # Connect to main database
    with sqlite3.connect(DATABASE_NAME) as _db:
        cursor = _db.cursor()
        # Get classroom teachers
        cursor.execute('SELECT id, teacher_id FROM ' + TABLE_CLASSROOM_TEACHERS + ' WHERE classroom_id = ' + classroom_id)
        teachers = list(cursor)
        # Get teachers names
        named_teachers = []
        for teacher in teachers:
            name = list(cursor.execute('SELECT name FROM teachers WHERE id = %d'%(teacher[1])))[0][0]
            named_teacher = [*teacher, name]
            named_teachers.append(named_teacher)
        teachers = named_teachers
        # Get school's teachers
        cursor = _db.execute('SELECT id, name FROM teachers')
        school_teachers = list(cursor)
        cursor.close()
    return render_template('classroom_teachers.html',classroom_name=classroom_name,classroom_id=classroom_id,teachers=teachers,school_teachers=school_teachers)

# Add some thing in some table 
@app.route('/add',methods=['GET','POST'])
def add():
    # Add something in the sql database
    table = request.args.get("table")
    # Add classroom
    if table == TABLE_CLASSROOMS:
        # Get classroom name
        name = request.form.get("name")
        # Get classroom grade
        grade = request.form.get("grade")
        # Record classroom information
        with sqlite3.connect(DATABASE_NAME) as _db:
            _db.execute('INSERT INTO ' + TABLE_CLASSROOMS + '(name, grade) VALUES (\'%s\', %s);'%(name, grade))
        return redirect('/')
    # Add teacher
    elif table == TABLE_TEACHERS:
        # Get teacher name
        name = request.form.get('name')
        # Record teacher information
        with sqlite3.connect(DATABASE_NAME) as _db:
            _db.execute('INSERT INTO ' + TABLE_TEACHERS + '(name) VALUES (\'%s\');'%(name))
        return redirect('/teachers')
    # Add matter
    elif table == TABLE_MATTERS:
        # Get matter name
        name = request.form.get('name')
        # Record matter 
        with sqlite3.connect(DATABASE_NAME) as _db:
            _db.execute('INSERT INTO ' + TABLE_MATTERS + '(name) VALUES (\'%s\')'%(name))
        return redirect('/matters')
    # Set matter to some teacher
    elif table == TABLE_TEACHER_MATTERS:
        # Get teacher id
        teacher_id = request.args.get("teacher_id")
        # Get teacher name
        teacher_name = request.args.get("teacher_name")
        # Get matter id
        matter_id = request.form.get("matter_id")
        # Record teacher matter
        with sqlite3.connect(DATABASE_NAME) as _db:
            _db.execute('INSERT INTO ' + TABLE_TEACHER_MATTERS + '(teacher_id, matter_id) VALUES (%s, %s)'%(teacher_id, matter_id))
        return redirect('/teacher_matters?id=' + teacher_id + '&name=' + teacher_name)
    # Set teacher to some classroom
    elif table == TABLE_CLASSROOM_TEACHERS:
        # Get classroom id
        classroom_id = request.args.get("classroom_id")
        # Get classroom name
        classroom_name = request.args.get("classroom_name")
        # Get teacher id
        teacher_id = request.form.get("teacher")
        # Record classroom teacher
        with sqlite3.connect(DATABASE_NAME) as _db:
            _db.execute('INSERT INTO ' + TABLE_CLASSROOM_TEACHERS + '(classroom_id, teacher_id) VALUES (%s,%s)'%(classroom_id, teacher_id))
        return redirect('/classroom_teachers?classroom_name=' + classroom_name + '&classroom_id=' + classroom_id)
    return redirect('/')

# Remove some thing in some table
@app.route('/remove')
def remove():
    # Remove something 
    table = request.args.get('table')
    _id = request.args.get('id')
    # Ensure if table exists
    if table in tables:
        with sqlite3.connect(DATABASE_NAME) as _db:
            _db.execute('DELETE FROM ' + table + ' WHERE id = %s'%(_id))
    if table == TABLE_TEACHERS:
        return redirect('/teachers')
    elif table == TABLE_MATTERS:
        return redirect('/matters')
    elif table == TABLE_TEACHER_MATTERS:
        # Get teacher id
        teacher_id = request.args.get("teacher_id")
        # Get teacher name
        teacher_name = request.args.get("teacher_name")
        return redirect('/teacher_matters?id=' + teacher_id + '&name=' + teacher_name)
    elif table == TABLE_CLASSROOM_TEACHERS:
        # Get classroom id
        classroom_id = request.args.get("classroom_id")
        # Get classroom name
        classroom_name = request.args.get("classroom_name")
        return  redirect('/classroom_teachers?classroom_name=' + classroom_name + '&classroom_id=' + classroom_id)
    return redirect('/')

# Execute the program
if __name__ == '__main__':
    # Create grid's tables
    with sqlite3.connect(DATABASE_NAME) as _db:
        # Create classroom's table
        _db.execute('CREATE TABLE IF NOT EXISTS ' + TABLE_CLASSROOMS + '(id INTEGER NOT NULL, name TEXT, grade INTEGER, PRIMARY KEY(id));')
        # Create teacher's table 
        _db.execute('CREATE TABLE IF NOT EXISTS ' + TABLE_TEACHERS + '(id INTEGER NOT NULL, name TEXT, PRIMARY KEY(id));')
        # Create matter's table 
        _db.execute('CREATE TABLE IF NOT EXISTS ' + TABLE_MATTERS + '(id INTEGER NOT NULL, name TEXT, PRIMARY KEY(id));')
        # Create teacher matters table
        _db.execute('CREATE TABLE IF NOT EXISTS ' + TABLE_TEACHER_MATTERS + '(id INTEGER NOT NULL,teacher_id INTEGER NOT NULL, matter_id INTEGER NOT NULL, PRIMARY KEY(id), FOREIGN KEY(teacher_id) REFERENCES teachers(id), FOREIGN KEY(matter_id) REFERENCES matters(id));')
        # Create classroom teachers table
        _db.execute('CREATE TABLE IF NOT EXISTS ' + TABLE_CLASSROOM_TEACHERS + '(id INTEGER NOT NULL,classroom_id INTEGER NOT NULL, teacher_id INTEGER NOT NULL, PRIMARY KEY(id), FOREIGN KEY(classroom_id) REFERENCES classrooms(id), FOREIGN KEY(teacher_id) REFERENCES teachers(id))')
    # Run app
    #app.run(host=os.environ['LOCAL_IP'],debug=False) # Visible to local wifi
    app.run(debug=True)
