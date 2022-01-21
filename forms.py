from wtforms import SubmitField, StringField, SelectField, PasswordField, TextAreaField, IntegerField, DateField, DecimalField, RadioField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, NumberRange

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    first_name = StringField("First name", validators=[InputRequired()])
    surname = StringField("Last name", validators=[InputRequired()])
    icon = RadioField("Icons", id="Icons",choices=[("winky","Winky Face"),("horse","Horse"),("fox","Fox")], validators=[InputRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class SearchLocationForm(FlaskForm):
    search = StringField("Search for a Place:", validators=[InputRequired()])
    order = RadioField("Choice", id="Choices",choices=["Alphabetical","Highest Rating"], validators=[InputRequired()])
    submit = SubmitField("Submit")

class SearchActivityForm(FlaskForm):
    search = SelectField("Choose an Activity:", validators=[InputRequired()])
    order = RadioField("Order", id="Order",choices=["Alphabetical","Highest Rating"], validators=[InputRequired()])
    submit = SubmitField("Submit")

class CommentForm(FlaskForm):
    comment = TextAreaField("Comment Section", validators=[InputRequired()])
    rating = IntegerField("Rating ?/10", validators=[InputRequired(),NumberRange(min=1,max=10,message="Must be between %(min)s and %(max)s")])
    submit = SubmitField("Submit")

class BookingForm(FlaskForm):
    start_date = DateField("Start Date", validators=[InputRequired()])
    end_date = DateField("End Date", validators=[InputRequired()])
    submit = SubmitField("Submit")

class UpdateForm(FlaskForm):
    updateID = IntegerField("ID")
    update2 = StringField("col2")
    update3 = StringField("col3")
    update4 = StringField("col4")
    update5 = StringField("col5")
    submit1 = SubmitField("destinations")
    submit2 = SubmitField("login")
    submit3 = SubmitField("booking")

class AddDestinationForm(FlaskForm):
    place = StringField("Place", validators=[InputRequired()])
    county = StringField("County", validators=[InputRequired()])
    description = StringField("Description")
    rating = IntegerField("Rating",validators=[NumberRange(1,10)])
    price = IntegerField("Price", validators=[InputRequired()])
    submit = SubmitField("Submit")
    
class ActivityForm(FlaskForm):
    date = DateField("Date", validators=[InputRequired()])
    time = StringField("Time: (eg. 9:00)", validators=[InputRequired()])
    activity = SelectField("Choose an Activity:", validators=[InputRequired()])
    submit = SubmitField("Submit")