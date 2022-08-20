from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from forms import NewTemplateForm, NewInterviewForm, NewUserForm, LoginForm, NewUserAdminForm, NewCandidateForm, NewTaskForm, DelegateTaskForm, InterviewEditForm
from flask_wtf.csrf import CSRFProtect
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from flask_modals import Modal, render_template_modal

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
Base = declarative_base()
modal = Modal(app)



# CONNECTING TO DB

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///crm.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CONFIGURE DATABASE

class User(db.Model, UserMixin, Base):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    interviews = relationship("Interview", back_populates="created_by")
    templates = relationship("Template", back_populates="created_by")
    candidates = relationship("Candidate", back_populates="created_by")
    tasks_sent = relationship("Task", primaryjoin="User.id==Task.sender_id", back_populates="from_user")
    tasks_received = relationship("Task", primaryjoin="User.id==Task.recipient_id", back_populates="to_user")
    tasks_delegated = relationship("Task", primaryjoin="User.id==Task.delegate_id", back_populates="delegated_by")

class Template(db.Model, Base):
    __tablename__="templates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_by = relationship("User", back_populates="templates")

class Interview(db.Model, Base):
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
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_by = relationship("User", back_populates="interviews")
    creation_time = db.Column(db.DateTime, nullable=False)
    completion_time = db.Column(db.DateTime, nullable=True)

class Candidate(db.Model, Base):
    __tablename__="candidates"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False)
    cv = db.Column(db.String, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_by = relationship("User", back_populates="candidates")
    created_date = db.Column(db.Date, nullable=False)
    tasks = relationship("Task", back_populates="candidate")

class Task(db.Model, Base):
    __tablename__="tasks"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    delegate_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    from_user = relationship("User", foreign_keys=[sender_id], back_populates="tasks_sent")
    to_user = relationship("User", foreign_keys=[recipient_id], back_populates="tasks_received")
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    candidate = relationship("Candidate", foreign_keys=[candidate_id], back_populates="tasks")
    interviewers = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    recruiter_notes = db.Column(db.Text, nullable=True)
    date_sent = db.Column(db.Date, nullable=False)
    date_received = db.Column(db.Date, nullable=True)
    date_completed = db.Column(db.Date, nullable=True)
    status = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, nullable=False)
    delegated_by = relationship("User", foreign_keys=[delegate_id], back_populates="tasks_delegated")
    interview_date = db.Column(db.Date, nullable=True)
    interview_time = db.Column(db.Time, nullable=True)
    scheduler_notes = db.Column(db.Text, nullable=True)
    completion_time = db.Column(db.DateTime, nullable=True)

db.create_all()

###################################### MANAGING USER SESSION ###########################################

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None

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
            full_name = f'{form.first_name.data} {form.last_name.data}',
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


###################################### MANAGING COMMUNICATION TEMPLATES ###########################################

@app.route('/templates')
def templates():
    templates = db.session.query(Template).all()
    print(templates)
    return render_template('message-templates.html', templates=templates, current_user=current_user, is_authenticated=current_user.is_authenticated)


@app.route('/templates/new', methods=['POST', 'GET'])
def new_template():
    form = NewTemplateForm()
    if form.validate_on_submit():
        # CHANGE USER ID LATER !!!
        new_template = Template(name=form.name.data, text=form.text.data, date=date.today(), owner_id=current_user.id)
        db.session.add(new_template)
        db.session.commit()
        return redirect(url_for('templates'))
    return render_template('create-template.html', form=form, current_user=current_user, is_authenticated=current_user.is_authenticated)


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


@app.route('/templates/delete/<int:template_id>')
def delete_template(template_id):
    template_to_delete = Template.query.get(template_id)
    db.session.delete(template_to_delete)
    db.session.commit()
    return redirect(url_for('templates'))

###################################### CREATING NEW TASKS FOR PIPELINE & INBOX ###########################################

def create_new_task(form):
    """pass over the form"""
    chosen_recipient = User.query.filter_by(full_name=form.recipient.data).first()
    chosen_candidate = Candidate.query.filter_by(full_name=form.candidate_id.data).first()
    new_task = Task(
        sender_id=current_user.id,
        recipient_id=chosen_recipient.id,
        delegate_id=chosen_recipient.id,
        candidate_id=chosen_candidate.id,
        interviewers=form.interviewers.data,
        role=form.role.data,
        date_sent=date.today(),
        is_archived=False,
        status="pending",
    )
    return new_task

###################################### MANAGING PIPELINE ###########################################
#### PIPELINE SHOWS ONLY ACCEPTED TASKS! ###
@app.route('/pipeline')
def pipeline():
    tasks = Task.query.filter_by(status="accepted").all()
    return render_template('pipeline.html', tasks=tasks, current_user=current_user, is_authenticated=current_user.is_authenticated)


@app.route('/pipeline/new', methods=['GET', 'POST'])
def pipeline_new():
    form = NewInterviewForm()
    candidates = db.session.query(Candidate).all()
    candidates_list = [candidate.full_name for candidate in candidates]
    users = db.session.query(User).all()
    users_list = [user.full_name for user in users]
    print(candidates_list)
    print(users)
    form.candidate_id.choices = candidates_list
    form.recipient.choices = users_list
    if form.validate_on_submit():
        new_task = create_new_task(form)
        new_task.scheduler_notes = form.scheduler_notes.data
        new_task.interview_time = form.time.data
        new_task.interview_date = form.date.data
        new_task.date_received = datetime.now()
        new_task.date_sent = datetime.now()
        new_task.status = "accepted"
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('pipeline'))
    return render_template('pipeline_new.html', form=form, current_user=current_user, is_authenticated=current_user.is_authenticated)


@app.route('/pipeline/edit/<int:task_id>', methods=['POST', 'GET'])
def pipeline_edit(task_id):
    task = Task.query.get(task_id)
    form = InterviewEditForm(
        role=task.role,
        interviewers=task.interviewers,
        date=task.interview_date,
        time=task.interview_time,
        scheduler_notes=task.scheduler_notes,
    )
    if form.validate_on_submit():
        for key in form.__dict__.keys():
            if key in task.__dict__.keys():
                setattr(task, key, form[key].data)
        db.session.commit()
        return redirect(url_for('pipeline'))
    return render_template('pipeline_edit.html', form=form, task_id=task_id, current_user=current_user, is_authenticated=current_user.is_authenticated)


@app.route('/pipeline/delete/<int:task_id>')
def pipeline_delete(task_id):
    task_to_delete = Task.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('pipeline'))


###################################### MANAGING USERS IN ADMIN PANEL ###########################################

@app.route('/users')
def users():
    users = db.session.query(User).all()
    return render_template('users.html', users=users)


@app.route('/users/new', methods=['POST', 'GET'])
def user_new():
    form = NewUserAdminForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            full_name=f'{form.first_name.data} {form.last_name.data}',
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
            return redirect(url_for('users'))
        else:
            flash(
                'The email provided already exists in the database. Please select another one to register the new user')
    else:
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                flash(err)

    return render_template('user_new.html', form=form)


@app.route('/users/edit/<int:user_id>', methods=["Post", "GET"])
def user_edit(user_id):
    user_to_edit = User.query.get(user_id)
    form = NewUserAdminForm(
        first_name=user_to_edit.first_name,
        last_name=user_to_edit.last_name,
        email=user_to_edit.email,
        phone=user_to_edit.phone,
        type=user_to_edit.type,
    )

    if form.validate_on_submit():
        for key in form.__dict__.keys():
            if key in user_to_edit.__dict__.keys():
                setattr(user_to_edit, key, form[key].data)
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        user_to_edit.password = hashed_password
        db.session.commit()
        return redirect(url_for('users'))

    return render_template('user_edit.html', user_id=user_id, form=form)

@app.route('/users/delete/<int:user_id>')
def user_delete(user_id):
    deleted_user = User.query.get(user_id)
    db.session.delete(deleted_user)
    db.session.commit()
    return redirect(url_for('users'))


###################################### MANAGING Candidates #########################################


@app.route('/candidates')
def candidates():
    candidates = db.session.query(Candidate).all()


    return render_template('candidates.html', candidates=candidates, current_user=current_user)

@app.route('/candidates/new', methods=['POST', 'GET'])
def candidates_new():
    form = NewCandidateForm()
    if form.validate_on_submit():


        if form.cv.data:
            cv_filename = secure_filename(form.cv.data.filename)
            form.cv.data.save('Uploads/CVs/'+cv_filename)
        else:
            cv_filename = ''


        new_candidate = Candidate(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            full_name=f'{form.first_name.data} {form.last_name.data}',
            email=form.email.data,
            phone=form.phone.data,
            owner_id=current_user.id,
            created_date=date.today(),
            cv=cv_filename,
        )

        candidate_email = Candidate.query.filter_by(email=new_candidate.email).first()
        if not candidate_email:
            db.session.add(new_candidate)
            db.session.commit()
            return redirect(url_for('candidates'))
        else:
            flash(
                'The email provided already exists in the database. Please select another one to register the candidate')
    else:
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                flash(err)
    return render_template('candidates_new.html', form=form, current_user=current_user)


@app.route('/tasks/new', methods=['POST', 'GET'])
def tasks_new():
    candidates = db.session.query(Candidate).all()
    candidates_list = [candidate.full_name for candidate in candidates]
    users = db.session.query(User).all()
    users_list = [user.full_name for user in users]
    form = NewTaskForm()
    print(candidates_list)
    print(users)
    form.candidate_id.choices = candidates_list
    form.recipient.choices = users_list
    if form.validate_on_submit():
        new_task = create_new_task(form)
        new_task.recruiter_notes = form.recruiter_notes.data
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('inbox'))
    return render_template('tasks_new.html', form=form)

@app.route('/inbox/task_accept/<int:task_id>', methods=['POST', 'GET'])
def task_accept(task_id):
    accepted_task = Task.query.filter_by(id=task_id).first()
    accepted_task.status = "accepted"
    accepted_task.date_received = date.today()
    db.session.commit()
    flash(f"You have just accepted the task. Find more interview details in Pipeline section")
    return redirect(url_for('inbox'))

##### GETTING TASKS COUNT ######

def get_tasks_count():
    delegations = Task.query.filter_by(delegate_id=current_user.id).all()
    delegated_list = []
    for task in delegations:
        if task.delegate_id == current_user.id and task.recipient_id != current_user.id:
            delegated_list.append(task)
    delegated_count = len(delegated_list)
    accepted_count = len(Task.query.filter_by(recipient_id=current_user.id, status="accepted").all())
    pending_count = len(Task.query.filter_by(recipient_id=current_user.id, status="pending").all())
    # Delegated tasks show the tasks delegated by current user

    tasks_count = {
        "accepted": accepted_count,
        "pending": pending_count,
        "delegated": delegated_count,
    }
    return tasks_count

### GETTING LIST OF DELEGATED TASKS
def get_delegations():
    delegations = Task.query.filter_by(delegate_id=current_user.id).all()
    return delegations

@app.route('/inbox/delegate/<int:task_id>', methods=['POST', 'GET'])
def task_delegate(task_id):
    user_tasks = Task.query.filter_by(recipient_id=current_user.id).all()
    form = DelegateTaskForm()
    users = db.session.query(User).all()
    users_list = [user.full_name for user in users]
    form.delegate_id.choices = users_list
    print(users_list)
    if form.validate_on_submit():
        chosen_recipient = User.query.filter_by(full_name=form.delegate_id.data).first()
        delegated_task = Task.query.filter_by(id=task_id).first()
        print(chosen_recipient.id)
        print(current_user)
        delegated_task.to_user = chosen_recipient
        delegated_task.delegated_by = current_user
        delegated_task.status = "pending"

        db.session.commit()
        flash(f"The task has been delegated to {chosen_recipient.full_name}")
        return redirect(url_for('inbox'))
    else:
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                flash(err)
    return render_template("modal_delegate.html", user_tasks=user_tasks, form=form, task_id=task_id, current_user=current_user, tasks_count=get_tasks_count(), delegated_tasks=get_delegations())

@app.route('/inbox')
def inbox():
    user_tasks = Task.query.filter_by(recipient_id=current_user.id).all()
    return render_template('inbox.html', user_tasks=user_tasks, tasks_count=get_tasks_count(), current_user=current_user, delegated_tasks=get_delegations())



if __name__ == "__main__":
    app.run(debug=True)