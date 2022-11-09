from flask import Flask , render_template , url_for
from flask import request

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/info')
def info():
    return render_template('info.html',result)

@app.route('/register',methods=['GET','POST'])
def register():
    result= {}
    if request.method == 'POST':
        name = request.form['name']
        result.update({'name':name})

        email = request.form['email']
        result.update({'email':email})

        mobile  = request.form['mobile-number']
        result.update({'mobile':mobile})

        city = request.form['city']
        result.update({'city':city})

        state = request.form['state']
        result.update({'state':state})

        country = request.form['country']
        result.update({'country':country})

        return render_template('info.html',result=result)

    

