from flask import Flask, request, redirect, url_for, render_template
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

class User:
    def __init__(self, login, password):
        self.login = login
        self.password = password

user=User('U1','P1')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/login')
def login():
    return f'login page'

@app.errorhandler(HTTPException)
def errors(e):
    return f'Error: {e}'

if __name__=="main":
    app.run()