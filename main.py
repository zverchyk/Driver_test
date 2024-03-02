from flask import Flask, abort, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, distinct
from sqlalchemy.ext.declarative import declarative_base
from wtforms import StringField, SubmitField
from flask_bootstrap import Bootstrap5
import json
from form import QuestionForm, StartForm
import random as r

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
    correct = db.Column(String())
    image = db.Column(String())


def upload_data():  
    with app.app_context():
        db.create_all()
        with open("Questions\QC.json", 'r', encoding='utf-8') as file:
            database = json.load(file)
        

        for key, value in database.items():
            new_question = Question(
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
        session.clear()
        return redirect(url_for('next_question'))
    return render_template('start.html', form= form)
    
@app.route('/quiz/<int:number>', methods = ['GET', "POST"])
def quiz(number):  
    result = db.session.execute(db.select(Question))
    questions = result.scalars().all()

      
    question = questions[number]

    return render_template('index.html', question=question)
@app.route('/next_question')
def next_question():
    result = db.session.execute(db.select(Question))
    questions = result.scalars().all()
    current_question_index = session.get('current_question_index', 0)
    previous_questions = session.get('previous_questions', [])
    print(len(previous_questions))  
 
    if len(previous_questions) <= 0 or current_question_index +1 == len(previous_questions):
        number = get_random(all = len(questions) - 1, last = previous_questions)
        previous_questions.append(number)

    else:
        number = previous_questions[current_question_index+1]
        current_question_index+=1
    session['current_question_index'] = current_question_index
    session['previous_questions'] = previous_questions
    print('start: ', previous_questions)
    print('start index: ', current_question_index)
    return redirect(url_for('quiz', number = number))

@app.route('/previous_question')
def previous_question():
    current_question_index = session.get('current_question_index', 0)
    previous_questions = session.get('previous_questions', [])
    if current_question_index >0 and len(previous_questions) >1:
        current_question_index -=1
        
    number = previous_question[current_question_index]
    
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
        
        return redirect(url_for('quiz'))
    
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