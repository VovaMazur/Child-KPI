from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, DateField
from wtforms.validators import Length, EqualTo, DataRequired, ValidationError
from childkpi.models import User


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    password1 = PasswordField(label='PIN:', validators=[Length(max=4), DataRequired()])
    password2 = PasswordField(label='Confirm PIN:', validators=[EqualTo('password1'), DataRequired()])
    is_parent = BooleanField(label='Are you Parent?')
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='PIN:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class BinaryAnswerForm(FlaskForm):
    number = SelectField(label='Have you completed your daily goals?', choices=[(100, 'Yes'), (0, 'No')], validators=[DataRequired()])
    comment = StringField(label='Comments:', validators=[Length(max=30)])
    submit = SubmitField(label='Submit')


class NumberAnswerForm(FlaskForm):
    number = SelectField(label='How good are your daily goals completed?', choices=[(0, '0%'), (25, '25%'), (50, '50%'), (75, '75%'), (100, '100%')], validators=[DataRequired()])
    comment = StringField(label='Comments:', validators=[Length(max=30)])
    submit = SubmitField(label='Submit')


class SportAnswerForm(FlaskForm):
    number = SelectField(label='How good are your daily goals completed?', choices=[(0, '0%'), (25, '25%'), (50, '50%'), (75, '75%'), (100, '100%')], validators=[DataRequired()])
    sport = SelectField(label='Which sport activity have you done?',
                        choices=[('Walk', 'Walk'),
                                 ('Exercises', 'Exercises'),
                                 ('Yoga', 'Yoga'),
                                 ('Run', 'Run'),
                                 ('Other', 'Other'),
                                 ('Many', 'Many')])
    comment = StringField(label='Comments:', validators=[Length(max=30)])
    submit = SubmitField(label='Submit')