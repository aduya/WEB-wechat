from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField,PasswordField
from wtforms.validators import DataRequired,Email,length,Regexp,EqualTo,Length
from wtforms import ValidationError
from .models import User

class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[Email(),DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(),length(6,16)])
    remember_me = BooleanField('记住我')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(6, 64),
                                           Email()])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.'),length(6,16)])
    password2 = PasswordField('确认密码', validators=[DataRequired()])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email已经被注册过.请更换')

