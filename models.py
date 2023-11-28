from datetime import datetime
# from tkinter.tix import INTEGER
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
# from passlib.hash import scrypt
from werkzeug.security import check_password_hash

db = SQLAlchemy()


# Define the Question model
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    
    def __init__(self, question_text):
        self.question_text = question_text

    def __repr__(self):
        return f'<Question {self.id}>'

# Define the Response model
class Response(db.Model):
    __tablename__ = 'responses'
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location = db.Column(db.String(255))
    response_text = db.Column(db.String(255))
    dialect = db.Column(db.String(3))  # Add dialect column (e.g., "Yes" or "No")
    alternative_text = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='responses')
    question = db.relationship('Question')
    
    
    def __init__(self, question_id, user_id, response_text, dialect=None, alternative_text=None, location=None):
        self.question_id = question_id
        self.user_id = user_id
        self.response_text = response_text
        self.dialect = dialect  # Initialize the dialect field
        self.alternative_text = alternative_text  # Initialize the alternative_text field
        self.location = location


    def __repr__(self):
        return f'<Response {self.id}>'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(255))
    survey_progress = db.Column(db.Integer, default = 2)
    

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')