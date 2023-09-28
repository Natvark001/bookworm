from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms import StringField, SubmitField,TextAreaField,PasswordField
from wtforms.validators import Email,DataRequired,EqualTo,Length


class RegForm(FlaskForm):
    fullname=StringField('FirstName',validators=[DataRequired(message='Your first name must be supplied')])
    usermail=StringField('Email',validators=[DataRequired(message='Your must suppy an email'),Email(message='Invalid Email Format')])
    pwd=PasswordField('Your password',validators=[DataRequired(message='Password is required')])
    btnsubmit=SubmitField('Register')
    confpwd=PasswordField('confirm password',validators=[EqualTo('pwd',message='Both passwords must match')])

class DpForm(FlaskForm):
    dp=FileField('Upload a Profile Picture',validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'])])
    btnupload=SubmitField('Upload')
    
class ProfileForm(FlaskForm):
    fullname=StringField('FirstName')
    btnsubmit=SubmitField('submit')
    
class ContactForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(message='Your must suppy an email'),Email(message='Invalid Email Format')])
    btnsubmit=SubmitField('Subscribe')