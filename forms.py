from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, TimeField, SelectField, FileField, MultipleFileField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, Email, Length, NoneOf

short_code = {
    "user_first_name": "{current_user.first_name}",
    "user_full_name": "{current_user.full_name}"
}

class NewUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First Name is required")])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last Name is required")])
    email = StringField('Email - serving as Login ID', validators=[DataRequired(message="Email is required"), Email()])
    phone = StringField('Phone', validators=[DataRequired(message="Phone is required"), Length(min=10, message="Please make sure to add country code: eg. +48 573 341 312")])
    type = SelectField('User type', validators=[DataRequired(message="User type is required")], choices=['Recruiter', 'Coordinator'])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required")])
    submit = SubmitField('Submit')

class NewUserAdminForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First Name is required")])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last Name is required")])
    email = StringField('Email - serving as Login ID', validators=[DataRequired(message="Email is required"), Email()])
    phone = StringField('Phone', validators=[DataRequired(message="Phone is required"), Length(min=10, message="Please make sure to add country code: eg. +48 573 341 312")])
    type = SelectField('User type', validators=[DataRequired(message="User type is required")], choices=['Recruiter', 'Coordinator', 'Admin'])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required")])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    login = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")

class NewTemplateForm(FlaskForm):
    name = StringField('Template name', validators=[DataRequired()])
    text = CKEditorField('Template body', validators=[DataRequired()])
    submit = SubmitField('Submit')

class NewInterviewForm(FlaskForm):
    recipient = SelectField('Send to:', validators=[DataRequired(message="Send to is required")])
    candidate_id = SelectField('Select Candidate:', validators=[DataRequired(message="Candidate is required")])
    role = StringField('Role', validators=[DataRequired(message="Role is required")])
    interviewers = StringField('List interviewers (separated by ","):', validators=[DataRequired(message="interviewers are required")])
    date = DateField('Interview Date')
    time = TimeField('Interview Time')
    scheduler_notes = CKEditorField('Notes', validators=[DataRequired(message="By adding notes you make your and your colleagues' life easier!")])
    add = SubmitField('Add')

class InterviewEditForm(FlaskForm):
    role = StringField('Role', validators=[DataRequired(message="Role is required")])
    interviewers = StringField('List interviewers (separated by ","):', validators=[DataRequired(message="interviewers are required")])
    interview_date = DateField('Interview Date')
    interview_time = TimeField('Interview Time')
    scheduler_notes = CKEditorField('Notes', validators=[DataRequired(message="By adding notes you make your and your colleagues' life easier!")])
    add = SubmitField('Add')

class NewCandidateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First Name is required")])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last Name is required")])
    email = StringField('Email - serving as Login ID', validators=[DataRequired(message="Email is required"), Email()])
    phone = StringField('Phone', validators=[DataRequired(message="Phone is required"), Length(min=10, message="Please make sure to add country code: eg. +48 573 341 312")])
    cv = FileField("Upload Candidate's CV")
    submit = SubmitField('Submit')

button_style = {'class': 'm-4'}

class NewTaskForm(FlaskForm):
    recipient = SelectField('Send to:', validators=[DataRequired(message="Send to is required")])
    candidate_id = SelectField('Select Candidate:', validators=[DataRequired(message="Candidate is required")])
    interviewers = StringField('List interviewers (separated by ","):', validators=[DataRequired(message="interviewers are required")])
    role = StringField('Position:', validators=[DataRequired(message="Position is required")])
    recruiter_notes = CKEditorField('Interview details:')
    submit = SubmitField('Submit', render_kw=button_style)

class DelegateTaskForm(FlaskForm):
    delegate_id = SelectField('Select user to delegate the task:', validators=[DataRequired(message="User is required")])
    delegate_task = SubmitField('Delegate')

class SelectTemplateForm(FlaskForm):
    templates = SelectField('Select pre-made template:', validators=[NoneOf("", message="Please select the template you want to use!")])
    select = SubmitField('Select')

class MessageForm(FlaskForm):
    send_to = StringField('Send To:', validators=[DataRequired(message="Recipient email required")])
    carbon_copy = StringField('CC:')
    subject = StringField('Subject:', validators=[DataRequired(message="Recipient email required")])
    text = CKEditorField('Email Body:', validators=[DataRequired()])
    send = SubmitField('Send')


