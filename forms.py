from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, TimeField, SelectField, FileField, MultipleFileField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, Email, Length

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
    text = CKEditorField('Message text', validators=[DataRequired()])
    submit = SubmitField('Submit')

class NewInterviewForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First Name is required")])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last Name is required")])
    email = StringField('Email', validators=[DataRequired(message="Email is required"), Email()])
    phone = StringField('Phone', validators=[DataRequired(message="Phone is required"), Length(min=10, message="Please make sure to add country code: eg. +48 573 341 312")])
    role = StringField('Role', validators=[DataRequired(message="Role is required")])
    req_id = StringField('Req ID', validators=[DataRequired(message="Requisition ID is required")])
    recruiter = StringField('Recruiter', validators=[DataRequired(message="Recruiter is required")])
    interviewers = StringField('Interviewers', validators=[DataRequired(message="Interviewers is required")])
    date = DateField('Interview Date')
    time = TimeField('Interview Time')
    notes = CKEditorField('Notes', validators=[DataRequired(message="By adding notes you make your and your colleagues' life easier!")])
    add = SubmitField('Add')

class NewCandidateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First Name is required")])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last Name is required")])
    email = StringField('Email - serving as Login ID', validators=[DataRequired(message="Email is required"), Email()])
    phone = StringField('Phone', validators=[DataRequired(message="Phone is required"), Length(min=10, message="Please make sure to add country code: eg. +48 573 341 312")])
    cv = FileField("Upload Candidate's CV")
    submit = SubmitField('Submit')

class NewTaskForm(FlaskForm):
    recipient = SelectField('Send to:', validators=[DataRequired(message="Send to is required")])
    candidate_id = SelectField('Select Candidate:', validators=[DataRequired(message="Candidate is required")])
    interviewers = StringField('List interviewers (separated by ","):', validators=[DataRequired(message="interviewers are required")])
    role = StringField('Position:', validators=[DataRequired(message="Position is required")])
    description = CKEditorField('Interview details:')
    submit = SubmitField('Submit')
