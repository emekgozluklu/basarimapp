from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired
from basarimapp.exam import EXAM_TYPES


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()], render_kw={'class': 'form-control'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'class': 'form-control'})
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In', render_kw={'class': 'form-group button-primary'})

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=3, max=32)], render_kw={'class': 'form-control'})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=32)], render_kw={'class': 'form-control'})
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()], render_kw={'class': 'form-control'})
    password = PasswordField('Password',
                             validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')],
                             render_kw={'class': 'form-control'}
                             )

    confirm = PasswordField('Verify password', render_kw={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)


class AddPublisherForm(FlaskForm):
    pub_name = StringField('Publisher Name', validators=[DataRequired(), Length(min=3, max=30)], render_kw={'class': 'form-control'})
    email = StringField('Email', validators=[DataRequired(), Length(1, 100), Email()], render_kw={'class': 'form-control'})
    password = PasswordField('Password',
                             validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')],
                             render_kw={'class': 'form-control'}
                             )

    confirm = PasswordField('Verify password', render_kw={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        super(AddPublisherForm, self).__init__(*args, **kwargs)


class AddExamForm(FlaskForm):
    title = StringField('Exam Title', validators=[DataRequired(), Length(min=3, max=250)], render_kw={'class': 'form-control'})
    exam_type = SelectField('Exam Type', choices=EXAM_TYPES, default=EXAM_TYPES[0], render_kw={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        super(AddExamForm, self).__init__(*args, **kwargs)


class EnterExamCodeForm(FlaskForm):
    code = StringField('Exam Code', validators=[DataRequired(), Length(min=8, max=15)], render_kw={'class': 'form-control'})

    def __init__(self, *args, **kwargs):
        super(EnterExamCodeForm, self).__init__(*args, **kwargs)
