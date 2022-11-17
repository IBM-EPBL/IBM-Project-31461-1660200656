from flask import Flask,render_template,redirect
from flask import url_for,session,request
from dotenv import load_dotenv
from mailer import send_the_email
from datetime import datetime
from generator import generate_unique_id
from fetch import fetch_home
from check import check_the_acc_info
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
    if not session:
        return render_template('index.htm')

    return redirect(url_for('home'))

@app.route('/login')
def login():
    if not session or not session['login_status']:
        return render_template('login.htm')

    return redirect(url_for('home'))

@app.route('/guide')
def guide():
    return render_template('guide.htm')

@app.route('/register')
def register():
    return render_template('register.htm')

@app.route('/account')
def account():
    if not session:
        return redirect(url_for('home'))
    if session['account-type'] == 'Donor':
        useremail = session['user_email']
        sql = "SELECT FIRSTNAME,LASTNAME,DOB,PHONE,USER_EMAIL,BLOOD_TYPE,COVID_STATUS,GENDER,STATE,PINCODE FROM DONORS WHERE USER_EMAIL=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,useremail)
        ibm_db.execute(stmt)
        res = ibm_db.fetch_assoc(stmt)
        return render_template('account.htm',res=res)
    if session['account-type'] =='user':
        useremail = session['user_email']
        sql = "SELECT FULLNAME,USER_DOB,PHONE_NO,EMAIL FROM USERS WHERE EMAIL=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,useremail)
        ibm_db.execute(stmt)
        result = ibm_db.fetch_assoc(stmt)
        return render_template('account.htm',res=result)

@app.route('/admin')
def admin():
    if not session or not session['admin-login']:
        return render_template('login_admin.htm')
    return render_template('admin.htm')

@app.route('/adminlogin')
def adminlogin():
    return render_template('login_admin.htm')

@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        password = bytes(password,'utf-8')
        password = hashlib.sha256(password).hexdigest()

        sql = "SELECT * FROM admin WHERE username=? AND password=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        adm = ibm_db.execute(stmt)
        if adm:
            session['admin-login'] = True
            return redirect(url_for('admin'))

@app.route('/donate')
def donate():
    if not session or not session['login_status']:
        return render_template('login.htm')

    if session['account-type'] == 'user':
        return redirect(url_for('register'))

    results = {}
    sql = "SELECT * FROM Requests WHERE REQUEST_STATUS=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,'PENDING')
    ibm_db.execute(stmt)
    result = ibm_db.fetch_assoc(stmt)
    i = 1
    while result:
        results.update({i : result})
        i = i + 1   
        result = ibm_db.fetch_assoc(stmt)
    return render_template('donate.htm',results=results)

@app.route('/BookAppointment/<req_id>')
def book_appointment(req_id):
    return render_template('donateForm.htm',req_id=req_id)

@app.route('/err')
def err():
    return render_template('err.htm',err_msg)

@app.route('/track')
def track():
    session['track_id'] = False
    return render_template('track.htm')



@app.route('/request')
def _request():
    if not session or not session['login_status']:
        return render_template('user_registration.htm')
    
    return render_template('request.htm')



@app.route('/track_request',methods=['GET','POST'])
def track_request():
    
    if request.method == 'POST':
        track_id = request.form['tracking-id']
        
        sql = "SELECT * FROM REQUESTS WHERE REQUEST_ID=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,track_id)
        ibm_db.execute(stmt)
        res = ibm_db.fetch_assoc(stmt)
        if res:
            session['track_id'] = True
            return render_template('track.htm',res=res)
        if not res:
            err_msg = 'There is no such request with this request id. '
            err_msg += 'Please Check Your Request ID once again'
            return render_template('err.htm',err_msg=err_msg)
    
@app.route('/track_req/<req_id>')
def track_req(req_id):
    track_id = req_id
    sql = "SELECT * FROM REQUESTS WHERE REQUEST_ID=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,track_id)
    ibm_db.execute(stmt)
    res = ibm_db.fetch_assoc(stmt)
    if res:
        session['track_id'] = True
        return render_template('track.htm',res=res)
    if not res:
        err_msg = 'There is no such request with this request id. '
        err_msg += 'Please Check Your Request ID once again'
        return render_template('err.htm',err_msg=err_msg)

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
            msg = "Password Doesn't Match"
            return render_template('err.htm',err_msg=msg)
         
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
            msg = "Account already Exists, Please login"
            return render_template('err.htm',err_msg=msg)
            

         # case 2: validate the input if it matches the required pattern
        if not re.match(r"^\S+@\S+\.\S+$", user_email):
            msg =  "Please Enter Valid Email Address "
            return render_template('err.htm',err_msg=msg)

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
        req,res = fetch_home(conn=conn)
        return render_template('home.htm',username=session['user_id'],req=req,res=res)

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
            msg = "Password Doesn't Match"
            return render_template('err.htm',err_msg=msg)
        
        password = bytes(password,'utf-8')
        password = hashlib.sha256(password).hexdigest()

        # case 1: check if user does exists already
        sql = "SELECT * FROM donors WHERE user_email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_assoc(stmt)
        if acc:
            msg = "Account already Exists, Please login "
            return render_template('err.htm',err_msg=msg)

        # case 2: validate the input if it matches the required pattern
        if not re.match(r"^\S+@\S+\.\S+$", email):
            msg =  "Please Enter Valid Email Address "
            return render_template('err.htm',err_msg=msg)

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
            session['account-type'] = 'user'
            session['login_status'] = True
            session['user_email'] = user_email
            session['user_id'] = user_email.split('@')[0]
            return redirect(url_for('home'))
        if acc:
            session['login_status'] = True
            session['account-type'] = 'Donor'
            session['user_email'] = user_email
            session['user_id'] = user_email.split('@')[0]
            return redirect(url_for('home'))

        
        # check if the acc exists 
        sql = "SELECT * FROM donors WHERE user_email=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,user_email)
        ibm_db.execute(stmt)
        res = ibm_db.fetch_assoc(stmt)
        if res:
            msg = "Account already Exists, Please login "
            return render_template('err.htm',err_msg=msg)
        else:
            msg = "Don't you have an account ? try register with us "
            return render_template('err.htm',err_msg=msg)


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
        ibm_db.execute(prep_stmt)

        return render_template('success.htm',request_id = request_id)

@app.route('/make_donation',methods=['GET','POST'])
def make_donation():
    if request.method == 'POST':
        request_id = request.form['req_id']
        donor_name = request.form['donor-name']
        donor_age = request.form['donor-age']
        blood_type = request.form['blood-type']
        medical_status = request.form['medical-status']
        location = request.form['location']
        date_time= request.form['datetime']
        date_time = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')
        phone_number = request.form['phone-number']
        contact_address =  request.form['contact-address']

        datenow = datetime.now().strftime('%Y-%m-%dT%H:%M')
        if str(date_time) < datenow:
            msg = "The Date you've entered is not suitable for making this appointment"
            return render_template('err.htm',err_msg=msg)


        chck = "SELECT * FROM Appointments WHERE request_id=?"
        stmt = ibm_db.prepare(conn,chck)
        ibm_db.bind_param(stmt,1,request_id)
        ibm_db.execute(stmt)
        res = ibm_db.fetch_assoc(stmt)
        if res:
            msg = " The Request was Already Engaged"
            return render_template('err.htm',err_msg=msg)
        
        sql = "INSERT INTO  Appointments VALUES (?, ?, ?, ?, ?, ?, ?,?, ?)"
        prep_stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(prep_stmt,1,request_id)
        ibm_db.bind_param(prep_stmt,2,donor_name)
        ibm_db.bind_param(prep_stmt,3,donor_age)
        ibm_db.bind_param(prep_stmt,4,blood_type)
        ibm_db.bind_param(prep_stmt,5,medical_status)
        ibm_db.bind_param(prep_stmt,6,location)
        ibm_db.bind_param(prep_stmt,7,date_time)
        ibm_db.bind_param(prep_stmt,8,phone_number)
        ibm_db.bind_param(prep_stmt,9,contact_address)
        ibm_db.execute(prep_stmt)

        upt_sql = "UPDATE requests SET request_status=? WHERE request_id=?"
        status = "ACCEPTED BY DONOR"
        upt_stmt = ibm_db.prepare(conn,upt_sql)
        ibm_db.bind_param(upt_stmt,1,status)
        ibm_db.bind_param(upt_stmt,2,request_id)
        ibm_db.execute(upt_stmt)

        msql = "SELECT recipient_email FROM requests WHERE request_id=?"
        mstmt = ibm_db.prepare(conn,msql)
        ibm_db.bind_param(mstmt,1,request_id)
        ibm_db.execute(mstmt)
        res = ibm_db.fetch_assoc(mstmt)
        to_email = res['RECIPIENT_EMAIL']
        subject = f'Your Request ID {request_id} has been Accepted By The Donor and Please refer the content of this mail'
        content = f'''
            <h1>Donor Found </h1>
            <h2>Details of the Donor and Appointment</h2>
            <body>
            <pre>
            Request ID      : {request_id}
            Donor's Name    : {donor_name}
            Donor's Age     : {donor_age}
            Medical Status  : {medical_status}
            Blood Type      : {blood_type}
            Location        : {location}
            Date and Time   : {date_time}
            Contact Address : {contact_address}
            </pre>   
            <h3> You May contact the Donor For Full Details</h3>
            <h3>Get Well Soon</h3>
            </body>
        '''
        send_the_email(to_email, subject,content)

        return redirect('/track_req/'+request_id)


@app.route('/logout')
def logout():
    # session['login_status'] = False
    session.pop('login_status',None)
    session.pop('user_id',None)
    session.pop('user_email',None)
    session.pop('account-type',None)
    session.pop('track_id',None)

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)