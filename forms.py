from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, Email

class NewTemplateForm(FlaskForm):
    name = StringField('Template name', validators=[DataRequired()])
    text = CKEditorField('Message text', validators=[DataRequired()])
    submit = SubmitField('Submit')