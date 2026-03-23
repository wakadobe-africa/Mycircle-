from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, EmailField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email,EqualTo,Length, Optional

class CreateAccount(FlaskForm):
    username=StringField('Username', validators=[DataRequired(message='Create a username')])
    email=EmailField('Email', validators=[DataRequired(message='Enter your email'), Email(message='Enter a valid email')])
    password=PasswordField('Password',validators=[DataRequired(),Length(min=8, message='Password must be at least 8 characters long')])
    con_password=PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password',message='Re-enter the password to confirm')])
    btncreate=SubmitField('Create Account')

class LoginForm(FlaskForm):
    email=EmailField('Email', validators=[DataRequired(message='Enter your email'), Email(message='Enter a valid email')])
    password=PasswordField('Password',validators=[DataRequired(message='Enter a password')])
    btn=SubmitField('Log in')


class CreateCommunity(FlaskForm):
    name_com=StringField('Community Name',validators=[DataRequired (message='Create a name for your community')])
    desc_com=TextAreaField('Description of your community',validators=[DataRequired (message='Tell us what your community is about')])
    # category_id will be populated with choices in the view
    category_id = SelectField('Select Category', coerce=int, validators=[DataRequired(message='Please select a category')])
    btn=SubmitField('Create Community')

class EditCommunity(FlaskForm):
    name_com=StringField('Community Name',validators=[DataRequired (message='Create a name for your community')])
    desc_com=TextAreaField('Description of your community',validators=[DataRequired (message='Tell us what your community is about')])
    # category_id will be populated with choices in the view
    category_id = SelectField('Select Category', coerce=int, validators=[DataRequired(message='Please select a category')])
    btn=SubmitField('Update Community')

    
class ProfileUpdate(FlaskForm):
    photo = FileField(validators=[FileAllowed(["jpg","png","jpeg","gif"],\
    message="Invalid filetype")])
    username=StringField('Username:', validators=[DataRequired(message='Update username')])
    firstname=StringField('Firstname:', validators=[DataRequired (message='Enter Firstname')])
    lastname=StringField('Lastname:', validators=[DataRequired (message='Enter Lastname')])
    email=EmailField('Email:', validators=[DataRequired(message='Enter your email'), Email(message='Enter a valid email')])
    current_password=PasswordField('Current Password:', validators=[Optional()])
    new_password=PasswordField('New Password',validators=[Optional(), Length(min=8, message='Password must be at least 8 characters long')])
    confirm_new_password=PasswordField('Confirm New Password',validators=[Optional(), EqualTo('new_password',message='Re-enter the password to confirm')])
    btn=SubmitField('Update Profile')


class PasswordResetForm(FlaskForm):
    email = EmailField('Email:', validators=[DataRequired(message='Enter your registered email'), Email(message='Enter a valid email')])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters long')])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    btn = SubmitField('Reset Password')


class AdminProfileUpdate(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Username is required')])
    email = EmailField('Email', validators=[DataRequired(message='Email is required'), Email(message='Enter a valid email')])
    role = StringField('Role', validators=[DataRequired(message='Role is required')])
    auth_level = SelectField('Authorization Level', coerce=int,
        choices=[(i, f'Level {i}') for i in range(1, 11)],
        validators=[DataRequired(message='Select an authorization level')])
    password = PasswordField('New Password', validators=[Length(min=0, max=255)])
    con_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match')])
    btn = SubmitField('Update Profile')
