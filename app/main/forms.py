from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField(('Username'), validators=[DataRequired()])
    password = PasswordField(('Password'), validators=[DataRequired()])
    remember_me = BooleanField(('Remember Me'))
    submit = SubmitField(('Sign In'))


class PostForm(FlaskForm):
    body = TextAreaField(('Текст'), validators=[DataRequired(), Length(min=0, max=1000)])
    image = FileField(('Изображение'))
    submit = SubmitField(('Отправить'))