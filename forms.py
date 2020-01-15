from flask_wtf import FlaskForm
from wtforms import SelectField, FileField, StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email


class UploadForm(FlaskForm):
    file = FileField(validators=[InputRequired()])


class LogInForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    login = SubmitField('Log in')


class SignUpForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm password', validators=[InputRequired()])
    signup = SubmitField('Sign up')


class ChangeForm(FlaskForm):
    old_password = PasswordField('Old_password', validators=[InputRequired()])
    new_password = PasswordField('New_password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm_password', validators=[InputRequired()])


class FilterForm(FlaskForm):
    filter = StringField('Filter name')
