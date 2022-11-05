from flask import Flask,render_template,redirect
from flask import url_for,session,request
from dotenv import load_dotenv
from mailer import send_the_email
from generator import generate_unique_id
import os
import hashlib
import re
import ibm_db
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(16)

try:
    conn = ibm_db.connect(os.getenv('CREDENTIALS'),'','')
except Exception as err:
     print("Exception occurs->", err)

@app.route('/')
def index():
    if not session or not session['login_status']:
        return render_template('index.htm')

    return redirect(url_for('home'))

@app.route('/login')
def login():
    if not session or not session['login_status']:
        return render_template('login.htm')

    return redirect(url_for('home'))

@app.route('/register')
def register():
    if not session or not session['login_status']:
        return render_template('register.htm')

    return redirect(url_for('home'))


@app.route('/request')
def _request():
    if not session or not session['login_status']:
        return render_template('user_registration.htm')
    
    return render_template('request.htm')

@app.route('/user_register',methods=['GET','POST'])
def user_register():
    if request.method == 'POST':
        user_name = request.form['username']
        user_dob = request.form['dob']
        user_phone = request.form['user-phone']
        user_email = request.form['useremail']
        password = request.form['password']
        cnf_password = request.form['cnf-password']

        # hashing the password
        if password != cnf_password:
            return "<span> Password Doesn't Match </span>"
         
        password = bytes(password,'utf-8')
        password = hashlib.sha256(password).hexdigest()
        # password hashed

    ## case 1: check if user does exists already
        sql = "SELECT * FROM users WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,user_email)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_assoc(stmt)
        if acc:
            return "<span> Account already Exists, Please login <a href='/login'>here</a></span>"

         # case 2: validate the input if it matches the required pattern
        if not re.match(r"^\S+@\S+\.\S+$", user_email):
            return "<span> Please Enter Valid Email Address </span>"

        insert_sql = "INSERT INTO  users VALUES (?, ?, ?, ?, ?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, user_name)
        ibm_db.bind_param(prep_stmt, 2, user_dob)
        ibm_db.bind_param(prep_stmt, 3, user_phone)
        ibm_db.bind_param(prep_stmt, 4, user_email)
        ibm_db.bind_param(prep_stmt, 5, password)
        ibm_db.execute(prep_stmt)


        to_email = user_email
        subject = "Confirmation on Registration with Plasma-Donor-App as User"
        html_content = '''

          <h1>Registration Successfull</h1><br>
          <p> Thank you so much for registering with us </p><br>
         <p> You are now registered user </p>   
        
        '''
        send_the_email(to_email, subject, html_content)
        return redirect(url_for('login'))


@app.route('/home')
def home():
    if not session:
        return redirect(url_for('login'))

    if session['login_status']:
        return render_template('home.htm',username=session['user_id'])

    return redirect(url_for('login'))


@app.route('/do_register',methods=['GET','POST'])
def do_register():
    if request.method == 'POST':
        first_name = request.form['fname']
        last_name = request.form['lname']
        email = request.form['email']
        addrss1 = request.form['Locality']
        addrss2 = request.form['address']
        state = request.form['State']
        pincode = request.form['Zip']
        dob = request.form['dob']
        gender = request.form['gender']
        phone = request.form['phone']
        covid_status = request.form['covid-report']
        blood_type = request.form['b-type']
        #------------------
        # password hashing
        password = request.form['password']
        cnf_password = request.form['cnf-password']
        if password != cnf_password:
            return "<span>Password Doesn't Match</span>"
        
        password = bytes(password,'utf-8')
        password = hashlib.sha256(password).hexdigest()

        # case 1: check if user does exists already
        sql = "SELECT * FROM donors WHERE user_email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_assoc(stmt)
        if acc:
            return "<span> Account already Exists, Please login <a href='/login'>here</a></span>"

        # case 2: validate the input if it matches the required pattern
        if not re.match(r"^\S+@\S+\.\S+$", email):
            return "<span> Please Enter Valid Email Address </span>"

        insert_sql = "INSERT INTO  donors VALUES (?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, first_name)
        ibm_db.bind_param(prep_stmt, 2, last_name)
        ibm_db.bind_param(prep_stmt, 3, email)
        ibm_db.bind_param(prep_stmt, 4, addrss1)
        ibm_db.bind_param(prep_stmt, 5, addrss2)
        ibm_db.bind_param(prep_stmt, 6, state)
        ibm_db.bind_param(prep_stmt, 7, pincode)
        ibm_db.bind_param(prep_stmt, 8, dob)
        ibm_db.bind_param(prep_stmt, 9, gender)
        ibm_db.bind_param(prep_stmt, 10, phone)
        ibm_db.bind_param(prep_stmt, 11, covid_status)
        ibm_db.bind_param(prep_stmt, 12, blood_type)
        ibm_db.bind_param(prep_stmt, 13, password)
        ibm_db.execute(prep_stmt)


        to_email =email
        subject='Confirmation on Registration with Plasma-Donor-App'
        html_content='''
            <h1>Registration Successfull</h1><br>
            <p> Thank you so much for registering with us </p><br>
            <p> You are now registered donor </p>        
        '''
        send_the_email(to_email, subject, html_content)
        return redirect(url_for('login'))
    return redirect(url_for('register'))

@app.route('/do_login',methods=['GET','POST'])
def do_login():
    if request.method == 'POST':
        user_email = request.form['user_email']
        password = request.form['password']
        # salt the password 
        password = bytes(password,'utf-8')
        password = hashlib.sha256(password).hexdigest()

        #query the db
        sql = "SELECT * FROM donors WHERE user_email =? AND pass_word=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,user_email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_assoc(stmt)
        if not acc:
            # check if present in users
            sql = "SELECT * FROM users WHERE email =? AND password=?"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,user_email)
            ibm_db.bind_param(stmt,2,password)
            ibm_db.execute(stmt)
            acc = ibm_db.fetch_assoc(stmt)
            session['login_status'] = True
            session['user_id'] = user_email.split('@')[0]
            return redirect(url_for('home'))
        if acc:
            session['login_status'] = True
            session['user_id'] = user_email.split('@')[0]
            return redirect(url_for('home'))

        
        # check if the acc exists 
        sql = "SELECT * FROM donors WHERE user_email=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,user_email)
        ibm_db.execute(stmt)
        res = ibm_db.fetch_assoc(stmt)
        if res:
            return "<span> Account Exists, Seems Like Password is incorrect </span>"
        else:
            return "<span>Don't you have an account ? try register with us <a href='/register'>HERE</a></span>"

@app.route('/do_request',methods=['GET','POST'])
def do_request():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        phone = request.form['phone']
        requested_blood_type = request.form['blood-type']
        locality = request.form['locality']
        postal_code = request.form['postal-code']
        address = request.form['contact-addrss']

        # generate request id
        request_id = generate_unique_id()
        # initial status of the request
        request_status = 'PENDING'

        insert_sql = "INSERT INTO  requests VALUES (?, ?, ?, ?, ?, ?, ?,?, ?, ?)"
        prep_stmt = ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(prep_stmt,1,request_id)
        ibm_db.bind_param(prep_stmt,2,request_status)
        ibm_db.bind_param(prep_stmt,3,name)
        ibm_db.bind_param(prep_stmt,4,age)
        ibm_db.bind_param(prep_stmt,5,email)
        ibm_db.bind_param(prep_stmt,6,phone)
        ibm_db.bind_param(prep_stmt,7,requested_blood_type)
        ibm_db.bind_param(prep_stmt,8,locality)
        ibm_db.bind_param(prep_stmt,9,postal_code)
        ibm_db.bind_param(prep_stmt,10,address)
        ibm_db.exec(prep_stmt)

        session['requested'] = True
        return render_template('success.htm',request_id = request_id)
  

@app.route('/logout')
def logout():
    session['login_status'] = False
    session.pop('user_id',None)

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)