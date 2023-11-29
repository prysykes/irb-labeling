import sys
print(sys.path)
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import LoginForm, db, Question, Response, User, RegistrationForm, LoginForm  # Import your models from models.py
# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.orm import Session
# from flask_wtf import FlaskForm
from flask_migrate import Migrate
# from passlib.hash import scrypt
from werkzeug.security import check_password_hash
import math

# from wtforms.validators import DataRequired, Email, EqualTo, Length

application = Flask(__name__)

# Configure the secret key
application.secret_key = 'ebd7979e922e558d1d34a7ec75caab1ef94faef6'
application.config['SESSION_TYPE'] = 'filesystem'
Session(application)
# Configure the database connection
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///depa.db'
db.init_app(application)
migrate = Migrate(application,db)
# Initialize Flask-Login
login_manager = LoginManager(application)
login_manager.login_view = 'login'

# Create the database tables within the application context
with application.app_context():
    db.create_all()

# Define User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# def is_last_question(question_id):
#     current_question = db.session.get(Question, question_id)
#     last_question = db.session.query(Question).order_by(Question.id.desc()).first()
#     return current_question == last_question

def is_last_question(question_id):
    current_question = db.session.query(Question).filter_by(id=question_id).first()
    last_question = db.session.query(Question).order_by(Question.id.desc()).first()
    return current_question.id == last_question.id


def get_next_question_id(question_id):
    current_question = db.session.query(Question).filter_by(id=question_id).first()
    if current_question:
        next_question = db.session.query(Question).filter(Question.id > question_id).order_by(Question.id).first()
        return next_question.id if next_question else None
    return None


# Define routes and views

@application.route('/')
# @login_required  # Add this to protect the home page
def index():
    questions = Question.query.all()
    return render_template('index.html', questions=questions)


@application.route('/fetch_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def fetch_question(question_id):
    if current_user.is_authenticated:
        # Retrieve the user's progress from the database
        user_progress = current_user.survey_progress or 2
        
        # Ensure the user can't access questions prior to their progress
        if question_id < user_progress:
            return redirect(url_for('fetch_question', question_id=user_progress))
            
        location = session.get('user_location', None)

        if request.method == 'POST':
            response_text = request.form['response_text']
            user_id = current_user.id
            # location = current_user.location

            if response_text.lower() == 'no':
                response_text = request.form.get('alternative_text', '')

                # Check if subsection-2 has been answered with "No"
                if not is_subsection_2_answered(user_id, question_id):
                    # If answered with "No," hide subsection-2 and show subsection-3
                    return jsonify({"hide_subsection_2": True})
                
            
            try:
                save_response_to_database(question_id, user_id, response_text, location)
                current_user.survey_progress = question_id
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                application.logger.error(f"Error saving response to the database: {str(e)}")
                flash("An error occurred while saving your response. Please try again.", "danger")
                return redirect(url_for('fetch_question', question_id=question_id))


            if is_last_question(question_id):
                return redirect(url_for('submit_survey'))
            else:
                next_question_id = get_next_question_id(question_id)
                # session['next_question_id'] = next_question_id
                return redirect(url_for('fetch_question', question_id = next_question_id))

        
        

        question = get_question_by_id(question_id)
        if not question:
            return "All questions have been answered", 200
        
        previous_question_id = question_id - 1
        next_question_id = get_next_question_id(question_id)
        total_questions = Question.query.count()

        # Calculate the progress percentage
        progress_percentage = math.ceil((question_id - 2) / (total_questions - 2) * 100)
# is_last_question = is_last_question(next_question_id) if next_question_id else True

        return render_template('question.html', 
        question_id=question_id, 
        question=question, 
        previous_question_id = previous_question_id, 
        next_question_id=next_question_id, 
        total_questions=total_questions,
        progress_percentage=progress_percentage,
        location = location)
    
    return "You must be logged in to access this page.", 401
def is_subsection_2_answered(user_id, question_id):
    # Query the database to check if the user has answered subsection-2 with "Yes"
    response = Response.query.filter_by(user_id=user_id, question_id=question_id).first()
    
    # Assuming there is a "response_option" field in your Response model to store the user's choice
    if response and response.dialect == "Yes":
        # Subsection-2 has been answered with "Yes"
        return True
    else:
        # Subsection-2 has not been answered with "Yes" or no response found
        return False



def get_question_by_id(question_id):
    try:
        question = Question.query.filter_by(id=question_id).first()
        return question
    except Exception as e:
        # print(f"Error getting question with ID {question_id}: {str(e)}")
        return None


def save_response_to_database(question_id, user_id, response_text, dialect, alternative_text, location):
    try:
        # Check if a response already exists for this user and question
        existing_response = Response.query.filter_by(user_id=user_id, question_id=question_id).first()
        if existing_response:
            existing_response.response_text = response_text
        else:
        
            response = Response(question_id=question_id, user_id=user_id, response_text=response_text, dialect = dialect, alternative_text = alternative_text, location = location)
            db.session.add(response)
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback the transaction in case of an error
        print(f"Database error: {str(e)}")


@application.route('/save_response/<int:question_id>', methods=['POST'])
@login_required  # Add this to protect the response submission
def save_response(question_id):
    question = get_question_by_id(question_id)

    if question is None:
        flash('Invalid question ID.', 'danger')
        return redirect(url_for('index'))  # Redirect to the homepage or an error page

    response_text = request.form['response_text']
    user_id = current_user.id  # Use the current logged-in user's ID
    # Fetch the dialect from the form
    dialect = request.form.get('dialect', '')  # Modify the default value as needed

    # Fetch the alternative_text from the form
    alternative_text = request.form.get('alternative_text', '')  # Modify the default value as needed

    # Fetch the location from the session
    location = session.get('user_location', None)

    # print(f"Received question_id: {question_id}")
    # print(f"Received response_text: {response_text}")
    # print(f"Current user ID: {user_id}")
    # print(f"Dialect?: {dialect}")
    # print(f"Alternative text: {alternative_text}")
    # print(f"Location: {location}")

    save_response_to_database(question_id, user_id, response_text, dialect, alternative_text, location)
    # Update the user's survey progress immediately
    current_user.survey_progress = question_id
    db.session.commit()

    if is_last_question(question_id):
        return redirect(url_for('submit_survey'))
    else:
        next_question_id = get_next_question_id(question_id)
        print(f"Next question ID: {next_question_id}")
        return redirect(url_for('fetch_question', question_id=next_question_id))


@application.route('/submit_survey')
@login_required  # Add this to protect the submission page
def submit_survey():
    return render_template('thank_you.html')

# @app.route('/survey/thank-you')
# def thank_you():
#     return render_template('thank_you.html')

@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(form.data)
    if form.validate_on_submit():
        # print('yes')
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user:
            # Check if the user's password is using scrypt hashing
            if user.password_hash and user.check_password(password):
                login_user(user)
                flash('Login successful.', 'success')

                if not user.location:
                    return redirect(url_for('location'))
                else:
                    return redirect(url_for('fetch_question', question_id = user.survey_progress))

                # return redirect(url_for('fetch_question', question_id=2)) 

        flash('Invalid username or password.', 'danger')
        print("Form not submitted")  # Debug statement
    return render_template('login.html', form=form)



@application.route('/logout', methods=['GET', 'POST'])
@login_required  # Add this to protect the logout route
def logout():
    try:
        # Save user progress when logging out
        current_user.survey_progress = current_user.survey_progress or 1 
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving user progress: {str(e)}")
    logout_user()
    return redirect(url_for('index'))


@application.route('/location', methods=['GET', 'POST'])
@login_required
def location():
    if current_user.is_authenticated:
        if current_user.location:
            # Location has already been set, redirect to the survey
            return redirect(url_for('fetch_question', question_id=2))  # Redirect to the first question

        if request.method == 'POST':
            selected_location = request.form.get('location')
            other_location = request.form.get('other_location', '')

            # Use the selected location or other_location based on the user's choice
            final_location = other_location if selected_location == 'other' else selected_location

            # Save the location to the current user
            current_user.location = final_location
            db.session.commit()

            # Store the location in the session
            session['user_location'] = final_location

            # Redirect to the survey's first question
            return redirect(url_for('fetch_question', question_id=2))

        return render_template('location.html')

    return "You must be logged in to access this page.", 401


@application.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(e)
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@application.route('/update_location', methods=['GET', 'POST'])
@login_required
def update_location():
    if current_user.is_authenticated:
        if request.method == 'POST':
            selected_location = request.form.get('location')
            other_location = request.form.get('other_location', '')  # Default to empty string if not present

            # Use the selected location or other_location based on the user's choice
            final_location = other_location if selected_location == 'other' else selected_location

            # Update the location for the current user
            current_user.location = final_location
            db.session.commit()

            # Store the updated location in the session
            session['user_location'] = final_location

            # Redirect to a page indicating that the location has been updated
            return render_template('location_updated.html', new_location=final_location)

        return render_template('update_location.html', current_location=current_user.location)

    return "You must be logged in to access this page.", 401



if __name__ == '__main__':
    application.run(debug=True)
