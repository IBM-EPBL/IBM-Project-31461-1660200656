from flask import Flask,render_template
import requests
import colorama
from bs4 import BeautifulSoup
import numpy
import pandas

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)