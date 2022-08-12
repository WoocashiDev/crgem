from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from forms import NewTemplateForm, NewCandidateForm, NewUserForm, LoginForm
from flask_wtf.csrf import CSRFProtect
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user,logout_user

os.environ['SECRET_KEY'] = 'TOP_SECRET_KEY!'
# INITIATING APP EXTENSIONS

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
Bootstrap(app)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(app)

# CONNECTING TO DB

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///crm.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CONFIGURE DATABASE

class User(db.Model, UserMixin):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

class Template(db.Model):
    __tablename__="templates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)

class Interview(db.Model):
    __tablename__="interviews"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    req_id = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    recruiter = db.Column(db.String, nullable=False)
    interviewers = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=True)
    time = db.Column(db.Time, nullable=True)
    notes = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)
    creation_time = db.Column(db.DateTime, nullable=False)
    completion_time = db.Column(db.DateTime, nullable=True)

db.create_all()

# USER SESSION MANAGEMENT

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None

# APP ROUTING

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.login.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                print(current_user.is_authenticated)
                return redirect(url_for('home'))
            else:
                flash('The password seems incorrect. Try again')
        else:
            flash('The user with provided login does not exist')
    return render_template('login.html', form=form, current_user=current_user, is_authenticated=current_user.is_authenticated)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = NewUserForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            type=form.type.data,
            password=hashed_password,
        )
        user_email = User.query.filter_by(email=new_user.email).first()
        print(user_email)
        if not user_email:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash('The email provided already exists in the database. Please select another one or log in to your account')
    else:
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                flash(err)

    return render_template('register.html', form=form, current_user=current_user, is_authenticated=current_user.is_authenticated)

@app.route('/')
def home():
    return render_template('index.html', current_user=current_user, is_authenticated=current_user.is_authenticated)

########### MANAGING MESSAGE TEMPLATES


# displaying templates list

@app.route('/templates')
def templates():
    templates = db.session.query(Template).all()
    print(templates)
    return render_template('message-templates.html', templates=templates, current_user=current_user, is_authenticated=current_user.is_authenticated)

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
    return render_template('create-template.html', form=form, current_user=current_user, is_authenticated=current_user.is_authenticated)

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

    return render_template('edit-template.html', form=form, template_id=template_id, current_user=current_user, is_authenticated=current_user.is_authenticated)

# deleting templates
@app.route('/templates/delete/<int:template_id>')
def delete_template(template_id):
    template_to_delete = Template.query.get(template_id)
    db.session.delete(template_to_delete)
    db.session.commit()
    return redirect(url_for('templates'))

##### CANDIDATES MANAGEMENT
@app.route('/pipeline')
def pipeline():
    interviews = db.session.query(Interview).all()
    return render_template('pipeline.html', interviews=interviews, current_user=current_user, is_authenticated=current_user.is_authenticated)

@app.route('/pipeline/new', methods=['GET', 'POST'])
def pipeline_new():
    form = NewCandidateForm()
    if form.validate_on_submit():
        new_interview = Interview(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            role=form.role.data,
            req_id=form.req_id.data,
            recruiter=form.recruiter.data,
            interviewers=form.interviewers.data,
            date=form.date.data,
            time=form.time.data,
            notes=form.notes.data,
            ### ADD CURRENT USER ID LATER
            created_by=1,
            creation_time=datetime.now()
            )
        db.session.add(new_interview)
        db.session.commit()
        return redirect(url_for('pipeline'))
    return render_template('pipeline_new.html', form=form, current_user=current_user, is_authenticated=current_user.is_authenticated)

@app.route('/pipeline/edit/<int:interview_id>', methods=['POST', 'GET'])
def pipeline_edit(interview_id):
    interview = Interview.query.get(interview_id)
    form = NewCandidateForm(
        first_name=interview.first_name,
        last_name=interview.last_name,
        email=interview.email,
        phone=interview.phone,
        role=interview.role,
        req_id=interview.req_id,
        recruiter=interview.recruiter,
        interviewers=interview.interviewers,
        date=interview.date,
        time=interview.time,
        notes=interview.notes,
    )
    if form.validate_on_submit():
        for key in form.__dict__.keys():
            if key in interview.__dict__.keys():
                setattr(interview, key, form[key].data)
        interview.creation_time = datetime.now()
        db.session.commit()
        return redirect(url_for('pipeline'))
    return render_template('pipeline_edit.html', form=form, interview_id=interview_id, current_user=current_user, is_authenticated=current_user.is_authenticated)

@app.route('/pipeline/delete/<int:interview_id>')
def pipeline_delete(interview_id):
    interview_to_delete = Interview.query.get(interview_id)
    db.session.delete(interview_to_delete)
    db.session.commit()
    return redirect(url_for('pipeline'))


if __name__ == "__main__":
    app.run(debug=True)