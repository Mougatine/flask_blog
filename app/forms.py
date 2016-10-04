from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class ChangePasswordForm(Form):
    old_pwd = PasswordField('Old password', validators=[DataRequired()])
    new_pwd = PasswordField('New password', validators=[DataRequired()])
    confirm_pwd = PasswordField('Confirm new password',
                                validators=[DataRequired()])

class SignupForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class WriterForm(Form):
    title = PageDownField('Title')
    intro = PageDownField('Type your intro (~ 2 lines max)')
    content = PageDownField('Type your article')
