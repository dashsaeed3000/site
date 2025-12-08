"""
Admin Area Forms
WTForms for authentication
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    """Login form"""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={'placeholder': 'Enter your username', 'class': 'form-control'}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)],
        render_kw={'placeholder': 'Enter your password', 'class': 'form-control'}
    )
    remember_me = BooleanField('Remember me')
    submit = SubmitField(
        'Login',
        render_kw={'class': 'btn btn-primary btn-block'}
    )

