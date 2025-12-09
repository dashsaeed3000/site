"""
User Forms
WTForms for user registration and login
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Optional, Regexp


class RegistrationForm(FlaskForm):
    """User registration form (phone-based)"""
    phone = StringField(
        'شماره تلفن',
        validators=[
            DataRequired(message='شماره تلفن الزامی است'),
            Regexp(r'^[\d\s\-\+\(\)]+$', message='شماره تلفن معتبر نیست'),
            Length(min=10, max=20, message='شماره تلفن باید بین 10 تا 20 کاراکتر باشد')
        ],
        render_kw={
            'placeholder': '09123456789',
            'class': 'form-control',
            'dir': 'ltr'
        }
    )
    email = StringField(
        'ایمیل (اختیاری)',
        validators=[Optional(), Email(message='ایمیل معتبر نیست')],
        render_kw={
            'placeholder': 'example@email.com',
            'class': 'form-control',
            'dir': 'ltr'
        }
    )
    name = StringField(
        'نام و نام خانوادگی',
        validators=[DataRequired(message='نام الزامی است'), Length(min=2, max=100)],
        render_kw={
            'placeholder': 'نام و نام خانوادگی',
            'class': 'form-control'
        }
    )
    password = PasswordField(
        'رمز عبور',
        validators=[
            DataRequired(message='رمز عبور الزامی است'),
            Length(min=6, max=100, message='رمز عبور باید حداقل 6 کاراکتر باشد')
        ],
        render_kw={
            'placeholder': 'رمز عبور',
            'class': 'form-control'
        }
    )
    password_confirm = PasswordField(
        'تکرار رمز عبور',
        validators=[DataRequired(message='تکرار رمز عبور الزامی است')],
        render_kw={
            'placeholder': 'تکرار رمز عبور',
            'class': 'form-control'
        }
    )
    submit = SubmitField(
        'ثبت نام',
        render_kw={'class': 'butn-dark'}
    )


class LoginForm(FlaskForm):
    """User login form (phone-based)"""
    phone = StringField(
        'شماره تلفن',
        validators=[
            DataRequired(message='شماره تلفن الزامی است'),
            Regexp(r'^[\d\s\-\+\(\)]+$', message='شماره تلفن معتبر نیست')
        ],
        render_kw={
            'placeholder': '09123456789',
            'class': 'form-control',
            'dir': 'ltr'
        }
    )
    password = PasswordField(
        'رمز عبور',
        validators=[DataRequired(message='رمز عبور الزامی است')],
        render_kw={
            'placeholder': 'رمز عبور',
            'class': 'form-control'
        }
    )
    remember_me = BooleanField('مرا به خاطر بسپار')
    submit = SubmitField(
        'ورود',
        render_kw={'class': 'butn-dark'}
    )


class PhoneVerificationForm(FlaskForm):
    """Phone verification form for checkout"""
    phone = StringField(
        'شماره تلفن',
        validators=[
            DataRequired(message='شماره تلفن الزامی است'),
            Regexp(r'^[\d\s\-\+\(\)]+$', message='شماره تلفن معتبر نیست'),
            Length(min=10, max=20, message='شماره تلفن باید بین 10 تا 20 کاراکتر باشد')
        ],
        render_kw={
            'placeholder': '09123456789',
            'class': 'form-control',
            'dir': 'ltr'
        }
    )
    otp = StringField(
        'کد تایید',
        validators=[
            DataRequired(message='کد تایید الزامی است'),
            Length(min=6, max=6, message='کد تایید باید 6 رقم باشد'),
            Regexp(r'^\d+$', message='کد تایید باید عددی باشد')
        ],
        render_kw={
            'placeholder': '123456',
            'class': 'form-control',
            'dir': 'ltr',
            'maxlength': '6'
        }
    )
    submit = SubmitField(
        'تایید و ادامه',
        render_kw={'class': 'butn-dark'}
    )


class CheckoutForm(FlaskForm):
    """Checkout form"""
    name = StringField(
        'نام و نام خانوادگی',
        validators=[DataRequired(message='نام الزامی است'), Length(min=2, max=100)],
        render_kw={
            'placeholder': 'نام و نام خانوادگی',
            'class': 'form-control'
        }
    )
    email = StringField(
        'ایمیل (اختیاری)',
        validators=[Optional(), Email(message='ایمیل معتبر نیست')],
        render_kw={
            'placeholder': 'example@email.com',
            'class': 'form-control',
            'dir': 'ltr'
        }
    )
    shipping_address = TextAreaField(
        'آدرس ارسال',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': 'آدرس کامل ارسال',
            'class': 'form-control',
            'rows': 3
        }
    )
    notes = TextAreaField(
        'یادداشت (اختیاری)',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': 'یادداشت یا درخواست خاص',
            'class': 'form-control',
            'rows': 2
        }
    )
    submit = SubmitField(
        'ادامه به پرداخت',
        render_kw={'class': 'butn-dark'}
    )

