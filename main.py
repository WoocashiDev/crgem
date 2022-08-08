from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from forms import NewTemplateForm
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import date


# INITIATING APP EXTENSIONS

app = Flask(__name__)
Bootstrap(app)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# CONNECTING TO DB

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///crm.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CONFIGURE DATABASE

class Template(db.Model):
    __tablename__="templates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)

db.create_all()

# APP ROUTING

@app.route('/')
def home():
    return render_template('index.html')

########### MANAGING MESSAGE TEMPLATES


# displaying templates list

@app.route('/templates')
def templates():
    templates = db.session.query(Template).all()
    print(templates)
    return render_template('message-templates.html', templates=templates)

# adding new template

@app.route('/templates/new', methods=['POST', 'GET'])
def new_template():
    form = NewTemplateForm()
    if form.validate_on_submit():
        # CHANGE USER ID LATER !!!
        new_template = Template(name=form.name.data, text=form.text.data, date=date.today(), created_by='1')
        db.session.add(new_template)
        db.session.commit()
        return redirect(url_for('templates'))
    return render_template('create-template.html', form=form)

# editing templates
@app.route('/templates/edit/<int:template_id>', methods=['POST', 'GET'])
def edit_template(template_id):
    template = Template.query.get(template_id)
    form = NewTemplateForm(
        name=template.name,
        text=template.text,
    )
    if form.validate_on_submit():
        template.name = form.name.data
        template.text = form.text.data
        db.session.commit()
        return redirect(url_for('templates'))

    return render_template('edit-template.html', form=form, template_id=template_id)

# deleting templates
@app.route('/templates/delete/<int:template_id>')
def delete_template(template_id):
    template_to_delete = Template.query.get(template_id)
    db.session.delete(template_to_delete)
    db.session.commit()
    return redirect(url_for('templates'))

if __name__ == "__main__":
    app.run(debug=True)