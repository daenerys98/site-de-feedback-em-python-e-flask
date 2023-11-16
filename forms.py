from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class FeedbackForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(min=1, max=100)])
    anotacao = TextAreaField('Anotação', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Postar Feedback')
