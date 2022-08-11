from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, TimeField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, Email, Length


class NewTemplateForm(FlaskForm):
    name = StringField('Template name', validators=[DataRequired()])
    text = CKEditorField('Message text', validators=[DataRequired()])
    submit = SubmitField('Submit')

class NewCandidateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(message="First Name field is required")])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last Name field is required")])
    email = StringField('Email', validators=[DataRequired(message="Email field is required"), Email()])
    phone = StringField('Phone', validators=[DataRequired(message="Phone field is required"), Length(min=10, message="Please make sure to add country code: eg. +48 573 341 312")])
    role = StringField('Role', validators=[DataRequired(message="Role field is required")])
    req_id = StringField('Req ID', validators=[DataRequired(message="Requisition ID field is required")])
    recruiter = StringField('Recruiter', validators=[DataRequired(message="Recruiter field is required")])
    interviewers = StringField('Interviewers', validators=[DataRequired(message="Interviewers field is required")])
    date = DateField('Interview Date')
    time = TimeField('Interview Time')
    notes = CKEditorField('Notes', validators=[DataRequired(message="By adding notes you make your and your colleagues' life easier!")])
    add = SubmitField('Add')
