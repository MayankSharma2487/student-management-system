from flask import Flask, redirect, url_for, request,session,g,flash
from flask.templating import render_template
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
import os,sqlite3
from sqlite3 import IntegrityError



app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)



@app.teardown_appcontext
def close_databse(error):
    if hasattr(g,'studentdatabase_db'):
        g.studentdatabase_db.close()




def get_current_user():
    user = None
    if 'user' in session:
        user = session['user']
        db = get_database()
        user_cur = db.execute('select * from users where name = ?',[user])
        user = user_cur.fetchone()
    return user



@app.route('/')
def index():
    user = get_current_user()
    return render_template('home.html',user = user)




@app.route('/login', methods=['POST', 'GET'])
def login():
    user = get_current_user()
    error = None
    db = get_database()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user_cursor = db.execute('select * from users where name = ?', [name])
        user = user_cursor.fetchone()

        if user:
            if check_password_hash(user['password'], password):
                session['user'] = user['name']
                return redirect(url_for('dashboard'))
            else:
                error = 'Username or Password did not match!!,try again.'
        else:
            error =  'Username or Password did not match!!,try again.'
    return render_template('login.html', loginerror=error,user = user)





@app.route('/register', methods=['POST', 'GET'])
def register():
    user = get_current_user()
    error = None
    db = get_database()

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        dbuser_cur = db.execute('select * from users where name = ?',[name])
        existing_username = dbuser_cur.fetchone()
        if existing_username:
             error = 'username already taken , try a different username'
        if not error:
            hashed_password = generate_password_hash(password)
            db.execute('insert into users(name, password) values(?, ?)', [name, hashed_password])
            db.commit()
            return redirect(url_for('index'))
    return render_template('register.html',registererror = error,user=user)


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    user = get_current_user()
    db = get_database()

    if request.method == 'GET':
        try:
            student_cur = db.execute('select * from students')  # Assuming table name is 'students'
            allstu = student_cur.fetchall()
        except sqlite3.Error as e:
            # Handle database error (e.g., connection issues)
            print(f"Database error: {e}")
            return render_template('error.html')  # Or display a user-friendly error message

        return render_template('dashboard.html', user=user, allstu=allstu,students=allstu,url_for=url_for)



@app.route('/addnewstudent', methods=['POST', 'GET'])
def addnewstudent():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        db = get_database()
        try:
            # Insert data
            cursor = db.cursor()
            cursor.execute('insert into students(name, email, phone, address) values(?, ?, ?, ?)',
                            (name, email, phone, address))

            # Commit changes
            db.commit()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return render_template('error.html')  # Or display a specific error message

        # Redirect to dashboard to display updated data
        return redirect(url_for('dashboard'))
    return render_template('addnewstudent.html', user=user)


@app.route('/singlestudentprofile/<int:empid>')
def singlestudentprofile(empid):
    user = get_current_user()
    db = get_database()

    with db as connection:  # Use 'with' on the connection object
        stud_cur = connection.cursor()
        stud_cur.execute("SELECT * FROM students WHERE empid = :empid", {"empid": empid})
        single_student = stud_cur.fetchone()

    # Handle case where no student is found (optional)
    if single_student is None:
        return render_template('error_student_not_found.html')  # Or handle differently

    return render_template('singlestudentprofile.html', user=user, single_student=single_student)


@app.route('/fetchone/<int:empid>')
def fetchone(empid):
    user=get_current_user()
    db = get_database()
    stud_cur=db.execute("SELECT * FROM students WHERE empid = :empid", {"empid": empid})
    single_student = stud_cur.fetchone()
    return render_template('updatestudent.html',user=user,single_student=single_student)



@app.route('/updatestudent',methods = ['POST','GET'])

def updatestudent():
    user = get_current_user()
    if request.method == 'POST':
        empid = request.form['empid']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        db = get_database()
        db.execute('insert into students(name, email, phone, address) values(?, ?, ?, ?)',
                            (name, email, phone, address))
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('updatestudent.html',user=user)


@app.route('/deletestudent/<int:empid>', methods=['POST', 'GET'])
def deletestu(empid):
  user=get_current_user()
  if request.method == 'GET':
      db = get_database()
      db.execute('delete from students where empid = ?',(empid,))
      db.commit()

      return redirect(url_for('dashboard'))
  return render_template('dashboard.html',user=user)




@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user information from session
    flash('You have been successfully logged out!', 'success')  # Informative flash message
    return redirect(url_for('home'))  # Redirect to login page or a dedicated logout page

if __name__ == '__main__':
    app.run(debug=True)
