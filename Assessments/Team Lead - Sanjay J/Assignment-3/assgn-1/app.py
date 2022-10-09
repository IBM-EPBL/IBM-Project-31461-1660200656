#!/usr/bin/python3

from flask import Flask,render_template,request

app = Flask(__name__)

@app.route('/')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')

        return display_info(username,email,phone)
    return render_template('register.html')
    



def display_info(name,mail,phone):
    return f'''
        <center>
         <h3> Here are the details you have entered: </h3>
         <p> username : {name} </p>
         <p> email : {mail} </p>
         <p> phone : {phone} </p>
        </center>
    
    '''
