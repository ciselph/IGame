from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, IntegerField, SelectField, \
    SelectMultipleField, IntegerRangeField
from wtforms.validators import DataRequired, Regexp, Email, EqualTo, InputRequired, Length
from wtforms import ValidationError
from ..models import User


class RatingForm(FlaskForm):
    gameRating = IntegerRangeField('Rating Number', validators=[DataRequired()])
    submit = SubmitField('RATE')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username required for login."),
                                                   Regexp('[^<>*]', message="Enter username again.")])
    password = PasswordField('Password', validators=[DataRequired(message="Password required for login."),
                                                     Regexp('[^<>*]', message="Enter password again.")])
    remember = BooleanField('Remember Me!')
    submit = SubmitField('Log In')


class GameForm(FlaskForm):
    game1 = StringField('Game 1')
    game1sel = SelectField('Select Game 1', choices=[], validators=[DataRequired(message='Field Required')])
    game2 = StringField('Game 2')
    game2sel = SelectField('Select Game 2', choices=[], validators=[DataRequired(message='Field Required')])
    game3 = StringField('Game 3')
    game3sel = SelectField('Select Game 3', choices=[], validators=[DataRequired(message='Field Required')])
    game4 = StringField('Game 4')
    game4sel = SelectField('Select Game 4', choices=[], validators=[DataRequired(message='Field Required')])
    game5 = StringField('Game 5')
    game5sel = SelectField('Select Game 5', choices=[], validators=[DataRequired(message='Field Required')])
    submit = SubmitField('FINISH')


class RegistrationForm(FlaskForm):
    username = StringField('A Username',
                           validators=[DataRequired(message="iGames requires a username for user identification."),
                                       Length(3, 50, message="Enter a username with 3 <= length <= 50"), Regexp('\w',
                                                                                                                message="Username must contain only Latin letters and whole numbers.")])
    password = PasswordField('A Password', validators=[
        InputRequired(message="Enter a desired password in this field and the next field."),
        Regexp('[^<>*]', message="Use letters, numbers and punctuation marks."),
        EqualTo('password_confirm', message='Passwords must match.')])
    password_confirm = PasswordField('Confirm Password',
                                     validators=[InputRequired(message="Re-enter desired password."),
                                                 EqualTo('password', message='Passwords do not match.')])
    email = StringField('Email Address', validators=[DataRequired(message="iGames registration requires email input."),
                                                     Regexp('[^<>*]',
                                                            message="Re-type email like: name@domain.whatever"),
                                                     Email(message="Invalid email input.")])
    name = StringField('Full Name', validators=[
        DataRequired(message="Enter your name. iGames accepts most unicode characters, including spaces."),
        Regexp('[^<>*]', message="Name input contains some unacceptable characters.")])
    bday = DateField('Birthdate', validators=[
        DataRequired(message="iGames generates age-appropriate game recommendations, so we need your birthdate.")])
    zipcode = IntegerField('Zipcode', validators=[DataRequired(message="Registration requires zipcode input.")])
    phone = StringField('Phone Number', validators=[DataRequired(message="Registration requires phone input."),
                                                    Length(1, 20, message='Simplify input to all numbers.'),
                                                    Regexp('[^<>*]', message="Simplify input to all numbers.")])
    submit = SubmitField('Register Me!')

    def validate_username(self, user):
        if User.query.filter(User.user_name == user.data).first():
            raise ValidationError('Username is taken.')
