from flask import Flask, abort, render_template, redirect,jsonify, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, distinct
from sqlalchemy.ext.declarative import declarative_base
from wtforms import StringField, SubmitField
from flask_bootstrap import Bootstrap5
import json
from form import QuestionForm, StartForm
import random as r
import threading
from time import sleep

#offset-aware datetime
import pytz
from datetime import datetime, timedelta

#allowed time in minutes
ALLOWED_TIME =  1
# Function to decrement the timer value and update it

app = Flask(__name__)
#config paths
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'

Bootstrap5(app)

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)



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

#uploads data to sql
@app.route('/add', methods=['GET', 'POST'])
def upload_data():  
    # with app.app_context():
    db.create_all()
    with open("Questions\QC.json", 'r', encoding='utf-8') as file:
        database = json.load(file)
    

    for key, value in database.items():
        new_question = Question(
            id= key,
            question=value["question"],
            answer_1=value["answers"][0],
            answer_2=value["answers"][1],
            answer_3=value["answers"][2],
            answer_4=value["answers"][3],
            correct=value["correct"],
            image=value['image']
        )
        db.session.add(new_question)
    db.session.commit()
    return 'data successfuly added'

def find_id_by_answer():
    with app.app_context():
        db.create_all()
        form = QuestionForm()
        search_question = request.form.get('search_question')
        result  = db.session.execute(db.select(Question).where(Question.answer_1== search_question)).scalar()
   
            
def get_random(all, last= []):
    number = r.randint(0, all)
    while number in last:
        number = r.randint(0, all)
    return number

@app.route('/', methods=["GET", "POST"])
def start():
    session.clear()
    form = StartForm()
    print(form.validate_on_submit())  
    if request.method == "POST":
        # session.clear()
            # Start the timer thread
        # timer_thread = threading.Thread(target=countdown, args= (result_queue))
        # timer_thread.start()
        session['start_time'] = datetime.now(pytz.UTC)
        session['update_website_time'] = True
        
        
        return redirect(url_for('next_question'))
    return render_template('start.html', form= form)
    
@app.route('/quiz/<int:number>', methods = ['GET', "POST"])
def quiz(number):  
    result = db.session.execute(db.select(Question))
    questions = result.scalars().all()
    #previous_questions contains questions' index number in the list 
    previous_questions = session.get('previous_questions', [])
    update_website_time = session.get('update_website_time', False)
    answered_questions = session.get('answered_questions', 0)
    dot_list = session.get('dot_list', ["green_dot" for x in range(5)])
    current_question_index = session.get('current_question_index', 0)
    print(previous_questions)
    print(number)
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
    len_previous_questions = len(previous_questions)
    minutes, seconds = divmod(time_used.total_seconds(), 60)
    
    errors = len([dot for dot in dot_list if dot != 'green_dot'])
    correct_answers = answered_questions - errors
    if time_used > allowed_duration or not 'green_dot' in dot_list:
        return render_template('result.html', success = False, time = {'minutes': int(minutes), 'seconds': int(seconds)}, correct_answers =correct_answers, q_list = len_previous_questions, mistakes = errors)  
    elif correct_answers ==25:
        return render_template('result.html', success = True, time = {'minutes': int(minutes), 'seconds': int(seconds)}, correct_answers =correct_answers, q_list = len_previous_questions, mistakes = errors)  

      
    question = questions[number]
    if request.method == "POST":
        selected_answer = str(request.form.get('answer'))
        if selected_answer == question.correct:
            print('it is correct answer', question.id)
        else:
            #search for first occurrence of value 'green_dot' and changes it to 'red_dot'
            fisrt_occurrence = dot_list.index('green_dot')
            dot_list[fisrt_occurrence] = 'red_dot'
            session['dot_list'] = dot_list
            print('you answer is written', question.id) 
        answered_questions+=1
        session['answered_questions'] = answered_questions
        return redirect(url_for('next_question'))
 
    return render_template('index.html', question=question, number = number, data_json=json.dumps(data), dot_list = dot_list, q_list =current_question_index)
@app.route('/next_question')
def next_question():
    result = db.session.execute(db.select(Question))
    questions = result.scalars().all()
    current_question_index = session.get('current_question_index', 0)
    previous_questions = session.get('previous_questions', [])
    len_previous_questions = len(previous_questions) 
 
    if len_previous_questions <= 0 or current_question_index +1 == len_previous_questions:
        if len_previous_questions == 30:
            return redirect(url_for('quiz', number = previous_questions[-1]))
        number = get_random(all = len(questions) - 1, last = previous_questions)
        previous_questions.append(number)
        if current_question_index != 0:
            current_question_index+=1 
    else:
        number = previous_questions[current_question_index+1]
        current_question_index+=1
    session['current_question_index'] = current_question_index
    session['previous_questions'] = previous_questions
    print('start: ', previous_questions)
    print('start index: ', current_question_index)
    return redirect(url_for('quiz', number = number))

@app.route('/previous_question/<int:number>')
def previous_question(number):  
    current_question_index = session.get('current_question_index', 0)
    previous_questions = session.get('previous_questions', [])
    if current_question_index >0 and len(previous_questions) >1:
        current_question_index -=1
        number = previous_questions[current_question_index] 
    else: 
        number = number
    print('previous: ', previous_questions)
    print('previous index: ', current_question_index)
    
    session['current_question_index'] = current_question_index
    session['previous_questions'] = previous_questions
    return redirect(url_for('quiz', number= number))

@app.route('/edit/<int:question_id>', methods =['GET', "POST"])
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
    if request.method == "POST":
        print(edit_q.validate_on_submit())
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

        

def delete_duplicates():
    with app.app_context():
        db.create_all()
        keep_rows = db.session.query(
            Question.id,
            db.func.row_number().over(
                partition_by=(Question.question, Question.answer_2),
                order_by=Question.id
            ).label('row_number')
        ).subquery('keep_rows')

        # Delete rows that are not in the keep_rows subquery
        delete_query = Question.__table__.delete().where(
            Question.id.notin_(
                db.session.query(keep_rows.c.id)
            )
        )

        db.session.execute(delete_query)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
    
    
    # for looking for question by its name
# form = QuestionForm()

    
# if request.method== "POST":
#     search_question = request.form.get('search_question')
#     result  = db.session.execute(db.select(Question).where(Question.question== search_question)).scalar()