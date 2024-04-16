from flask import Flask, abort, render_template, redirect,jsonify, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, distinct
from sqlalchemy.ext.declarative import declarative_base
from wtforms import StringField, SubmitField
from flask_bootstrap import Bootstrap5
import json
from form import QuestionForm, StartForm
import random as r
import os
from time import sleep
from functools import wraps

#offset-aware datetime
import pytz
from datetime import datetime, timedelta

#allowed time in minutes
ALLOWED_TIME =  25
# Function to decrement the timer value and update it

app = Flask(__name__)
#config paths
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'
app.config["SQLALCHEMY_BINDS"] = {
    'users': "sqlite:///users.db"
    }
Bootstrap5(app)

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader        
def load_user(user_id):
    return User.query.get(int(user_id))

#admin decorator 
def admin_only(function):
    @wraps(function) 
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.name != "admin":
            print(current_user) 
            print(current_user.is_authenticated)  
            return abort(403)
        else:
            return function(*args, **kwargs)
    return wrapper

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(Integer, primary_key=True)
    question = db.Column(String(), nullable=False)
    answer_1 = db.Column(String(), nullable=False)
    answer_2 = db.Column(String(), nullable=False)
    answer_3 = db.Column(String(), nullable=False)
    answer_4 = db.Column(String(), nullable=False)
    correct = db.Column(String(), nullable=False)
    image = db.Column(String())

 

with app.app_context():
    db.create_all()
    
# checking for pictures    
def file_exist(file_path):
    return os.path.exists(file_path)


#uploads data to sql
@app.route('/add', methods=['GET', 'POST'])

def upload_data():  
    # with app.app_context():
    db.create_all()
    with open("Questions\RQC.json", 'r', encoding='utf-8') as file:
        database = json.load(file)
    

    for key, value in database.items():
        new_question = Question(
            id= key,
            question=value["question"],
            answer_1=value["answers"][0],
            answer_2=value["answers"][1],
            answer_3=value["answers"][2],
            answer_4=value["answers"][3],
            correct=value["correct"]
        )
        db.session.add(new_question)
    db.session.commit()
    return 'data successfuly added'


@app.route('/login/<string:name>/<string:password>')
def login(name, password):
    user_name = db.session.execute(db.select(User).where(User.name == name)).scalar()
    user_password = db.session.execute(db.select(User).where(User.password == password)).scalar()
    if user_name and user_password:
        login_user(user_name)
    else:
        return abort(400)
    return redirect(url_for('quiz'))   
    
    
def find_id_by_answer():
    with app.app_context():
        db.create_all()
        form = QuestionForm()
        search_question = request.form.get('search_question')
        result  = db.session.execute(db.select(Question).where(Question.answer_1== search_question)).scalar()
   
            
def get_unique_values(lst, num_unique_values):
    # Ensure that num_unique_values is not greater than the length of the original list
    num_unique_values = min(num_unique_values, len(lst))
    
    # Use a set to store unique values
    unique_values = set()
    
    # Loop until we have enough unique values
    while len(unique_values) < num_unique_values:
        # Randomly select an element from the original list
        random_value = r.choice(lst)
        
        # Add it to the set of unique values
        unique_values.add(random_value)
    
    # Convert the set back to a list and return it
    return list(unique_values)

@app.route('/', methods=["GET", "POST"])
def start():
    
    session.clear()
    form = StartForm()
    print(form.validate_on_submit())  
    # admin = User(
    #     name= 'admin',
    #     password = '353535'
    # )
    # db.session.add(admin)
    # db.session.commit()
    if request.method == "POST":

        session['start_time'] = datetime.now(pytz.UTC)
        session['update_website_time'] = True
        result = db.session.execute(db.select(Question))
        questions = len(result.scalars().all())
        print(type(questions))
        questions_unique_indexes = get_unique_values(range(questions), 30)
        session['questions_unique_indexes'] = questions_unique_indexes 
        
        return redirect(url_for('next_question'))
    return render_template('start.html', form= form)
    
@app.route('/quiz', methods = ['GET', "POST"])
def quiz():  
    result = db.session.execute(db.select(Question))
    questions = result.scalars().all()
    #current index, index list, question number
    current_question_index = session.get('current_question_index', 0)
    questions_unique_indexes = session.get('questions_unique_indexes', [])
    
    number = questions_unique_indexes[current_question_index]
    #website time
    update_website_time = session.get('update_website_time', False)
    answered_questions = session.get('answered_questions', [])
    #error dots
    dot_list = session.get('dot_list', ["green_dot" for x in range(5)])
    current_question_index = session.get('current_question_index', 0)

    

    #website timer
    if update_website_time:
        data= {"update": True}
        session['update_website_time'] = False
    else:
        data= {"update": False}
    
     
    #inner timer settings 
    allowed_duration = timedelta(minutes=ALLOWED_TIME)
    start_time = session.get('start_time', None)  
    now = datetime.now(pytz.UTC)
    time_used = now - start_time
    #checking for remaining time and correct answers 
    len_questions_unique_indexes = len(questions_unique_indexes)
    minutes, seconds = divmod(time_used.total_seconds(), 60)
    
    errors = len([dot for dot in dot_list if dot != 'green_dot'])
    correct_answers = len(answered_questions) - errors
 
    if time_used > allowed_duration or not 'green_dot' in dot_list:
        return render_template('result.html', success = False, time = {'minutes': int(minutes), 'seconds': int(seconds)}, correct_answers =correct_answers, q_list = len(answered_questions), mistakes = errors)  
    elif correct_answers ==25:
        return render_template('result.html', success = True, time = {'minutes': int(minutes), 'seconds': int(seconds)}, correct_answers =correct_answers, q_list = len(answered_questions), mistakes = errors)  

      
    question = questions[number]
    if request.method == "POST":
        selected_answer = str(request.form.get('answer'))
        if selected_answer != question.correct:
            #search for first occurrence of value 'green_dot' and changes it to 'red_dot'
            fisrt_occurrence = dot_list.index('green_dot')
            dot_list[fisrt_occurrence] = 'red_dot'
            session['dot_list'] = dot_list 
            
        answered_questions.append(current_question_index)
        session['answered_questions'] = answered_questions
        return redirect(url_for('next_question'))
    image_path = f"static/img/" + str(question.id) + ".png"
    is_answered = current_question_index in answered_questions
    
    return render_template('index.html', question=question, number = number, data_json=json.dumps(data), dot_list = dot_list, q_list =current_question_index+1, file_exist= file_exist(image_path), image_path = image_path, is_answered = is_answered, getattr = getattr, is_admin= current_user) 

@app.route('/next_question')
def next_question():
    current_question_index = session.get('current_question_index', -1)
    if current_question_index <29:
        current_question_index += 1
        session['current_question_index'] = current_question_index
    return redirect(url_for('quiz'))
@app.route('/previous_question/<int:number>')
def previous_question(number):  
    current_question_index = session.get('current_question_index', 0)
    if current_question_index !=0:
        current_question_index -= 1
        session['current_question_index'] = current_question_index
    return redirect(url_for('quiz'))

@app.route('/edit/<int:question_id>', methods =['GET', "POST"])
@admin_only
def edit_question(question_id):
    question = db.get_or_404(Question, question_id)
    edit_q = QuestionForm(
            question = question.question,
            answer_1 = question.answer_1,
            answer_2 = question.answer_2,
            answer_3 = question.answer_3,
            answer_4 = question.answer_4,
            correct = question.correct,
            image = question.image
    )

    if edit_q.validate_on_submit() and request.method == "POST":
        question.question = edit_q.question.data
        question.answer_1 = edit_q.answer_1.data
        question.answer_2 = edit_q.answer_2.data
        question.answer_3 = edit_q.answer_3.data
        question.answer_4 = edit_q.answer_4.data
        question.correct = edit_q.correct.data
        question.image = edit_q.image.data
        db.session.commit()
        
        return redirect(url_for('quiz', number = question_id))
    
    return render_template('edit.html', form=edit_q, id = question_id)

        


if __name__ == "__main__":
    app.run(debug=True)
    
    
    # for looking for question by its name
# form = QuestionForm()

    
# if request.method== "POST":
#     search_question = request.form.get('search_question')
#     result  = db.session.execute(db.select(Question).where(Question.question== search_question)).scalar()