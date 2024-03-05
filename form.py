from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators, HiddenField
from wtforms.validators import DataRequired, URL


class QuestionForm(FlaskForm):
    csrf_token = HiddenField()
    question = StringField('Question', validators=[validators.length(max=1000)])
    answer_1 = StringField('First answer', validators=[validators.length(max=500)])
    answer_2 = StringField('Second answer', validators=[validators.length(max=500)])
    answer_3 = StringField('Third answern', validators=[validators.length(max=500)])
    answer_4 = StringField('Fourth answer', validators=[validators.length(max=500)])
    correct = StringField('Correct answer', validators=[validators.length(max=500)])
    image = StringField('Image', validators=[validators.length(max=5)])
    submit= SubmitField('submit')

    
class StartForm(FlaskForm):
    csrf_token = HiddenField()
    start = SubmitField('start')
    