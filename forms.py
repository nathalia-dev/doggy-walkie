from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, BooleanField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users (both)."""

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    dog_walker_check = BooleanField('Are you a Dog Walker?')
    
class LoginForm(FlaskForm):
    """Login form for both."""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    dog_walker_check = BooleanField('Are you a Dog Walker?')

class Dog_Owner_Profile_Form(FlaskForm):
    """Form to edit dog_owner profile"""

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    cellphone = StringField('Cellphone')
    photo = StringField("Photo")
    password = PasswordField('Password', validators=[Length(min=6)])

class Dog_Walker_Profile_Form(FlaskForm):
    """Form to edit dog_walker profile"""

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    cellphone = StringField('Cellphone')
    description= TextAreaField('Description')
    photo = StringField("Photo")
    password = PasswordField('Confirm your password to edit', validators=[Length(min=6)])

class Address_Form(FlaskForm):
    """Form to add an address """

    address = StringField("Address")
    zipcode = IntegerField("Zip Code", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    neighbor = StringField("Neighbor", validators=[DataRequired()])

class Dog_Form(FlaskForm):
    """Form to add an dog """ 

    first_name = StringField('First Name', validators=[DataRequired()])
    breed = SelectField("Breed", validators=[DataRequired()])
    weight = IntegerField('Weight (in pounds)', validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])

class Edit_Dog_Form(FlaskForm):
    """Form to edit an dog""" 

    first_name = StringField('First Name', validators=[DataRequired()])
    breed = SelectField('Breed', validators=[DataRequired()])
    weight = IntegerField('Weight (in pounds)', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    color = StringField('Color')
    description= TextAreaField('Description')
    photo = StringField('Photo')

class New_Message_Form(FlaskForm):
    """Form to create a Message"""
    
    text = TextAreaField("Message", validators=[DataRequired()])

class New_Appointment_Form(FlaskForm):
    """Form to create an Appointment"""

    dog_owner_id = SelectField("Costumer", coerce = int, validators=[DataRequired()])
    date = DateField('Date', format='%m-%d-%Y', validators=[DataRequired(message="Type date as 05-25-2021")])
    time_start = StringField('Start at', validators=[DataRequired()])
    day_period = SelectField("AM or PM?", validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])

class Review_Form(FlaskForm):
    """Form to create a review about the Appointment"""

    rate = SelectField("Rate", coerce = int, validators=[DataRequired()])
    comment = TextAreaField("Comment")

