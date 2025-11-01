import os
from dotenv import load_dotenv
from flask import Flask, request, redirect, url_for, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from flask_login import UserMixin

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db=SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={'placeholder':'Username'})
    password = StringField(validators=[InputRequired(),Length(min=8, max=20)], render_kw={'placeholder':'Password'})
    submit = SubmitField('Register')

    def username_validation(self, username):
        username_exists = User.query.filter_by(username=username.data).first()

        if username_exists:
            raise ValidationError("Username is taken, pick another one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(max=20)], render_kw={'placeholder':'Username'})
    password = StringField(validators=[InputRequired(),Length(max=20)], render_kw={'placeholder':'Password'})
    submit = SubmitField('Login')

@app.route('/')
@app.route('/games')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/login')
def login():
    return render_template("form.html")

@app.route('/register')
def register():
    return render_template("form.html")

@app.errorhandler(HTTPException)
def errors(e):
    return f'Error: {e}'

if __name__=="__main__":
    app.run()