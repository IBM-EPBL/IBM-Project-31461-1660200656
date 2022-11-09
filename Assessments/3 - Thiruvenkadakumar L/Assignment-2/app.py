from flask import Flask,render_template,session,url_for,request,redirect
import ibm_db
from dotenv import load_dotenv
import hashlib
import os
app = Flask(__name__)


app.secret_key = os.urandom(16)

try:
    conn = ibm_db.connect(os.getenv('CREDENTIALS'),'','')
except Exception as err:
     print("Exception occurs->", err)

@app.route('/')
def index():
    if session['login-status'] == True:
        return render_template('index.html')
    return render_template('register.html')
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/do_register',methods=['GET','POST'])
def do_register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        cnf_password =request.form['cnf-password']

        if password != cnf_password:
            return "<h3>Password Doesn't Match</h3>"
        # password hashing
        password = hashlib.sha256(bytes(password,'utf-8')).hexdigest()
        insert_sql = "INSERT INTO  users VALUES (?, ?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, email)
        ibm_db.bind_param(prep_stmt, 2, password)
        ibm_db.execute(prep_stmt)
        return redirect(url_for('login'))

@app.route('/do_login')
def do_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM users WHERE email=? AND password=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        acc = ibm_db.execute(stmt)

        if acc:
            session['login-status'] = True
            return redirect(url_for('index'))
        
        return "<h3> Account Doesn't Exists </h3>"
        
