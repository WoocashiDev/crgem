from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, TimeField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, Email, Length

class NewUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First Name is required")])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last Name is required")])
    email = StringField('Email - serving as Login ID', validators=[DataRequired(message="Email is required"), Email()])
    phone = StringField('Phone', validators=[DataRequired(message="Phone is required"), Length(min=10, message="Please make sure to add country code: eg. +48 573 341 312")])
    type = StringField('User type', validators=[DataRequired(message="User type is required")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required")])
    submit = SubmitField('Submit')

class NewTemplateForm(FlaskForm):
    name = StringField('Template name', validators=[DataRequired()])
    text = CKEditorField('Message text', validators=[DataRequired()])
    submit = SubmitField('Submit')

class NewCandidateForm(FlaskForm):
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
