from flask import Flask, render_template, redirect, url_for, flash, abort, send_from_directory
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from forms import NewTemplateForm, NewInterviewForm, NewUserForm, LoginForm, NewUserAdminForm, NewCandidateForm, NewTaskForm, DelegateTaskForm, InterviewEditForm, SelectTemplateForm, MessageForm
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
from flask_modals import Modal
from functools import wraps
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import env
from markupsafe import Markup

# INITIATING APP EXTENSIONS
app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
Bootstrap(app)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
login_manager = LoginManager(app)
login_manager.login_view = "landing_page"

Base = declarative_base()
modal = Modal(app)

print(EMAIL_PASSWORD)



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
    templates = relationship("Template", back_populates="created_by")
    candidates = relationship("Candidate", back_populates="created_by")
    tasks_sent = relationship("Task", primaryjoin="User.id==Task.sender_id", back_populates="from_user")
    tasks_received = relationship("Task", primaryjoin="User.id==Task.recipient_id", back_populates="to_user")
    tasks_delegated = relationship("Task", primaryjoin="User.id==Task.delegate_id", back_populates="delegated_by")
    message = relationship("Message", primaryjoin="Message.user_id==User.id", back_populates="user")

class Template(db.Model, Base):
    __tablename__="templates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_by = relationship("User", back_populates="templates")


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
    message = relationship("Message", primaryjoin="Message.candidate_id==Candidate.id", back_populates="candidate")

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
    time_completed = db.Column(db.Time, nullable=True)
    pipeline_status = db.Column(db.String, nullable=False)
    message = relationship("Message", primaryjoin="Message.task_id==Task.id", back_populates="task")

class Message(db.Model, Base):
    __tablename__="messages"
    id = db.Column(db.Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    task = relationship("Task", foreign_keys=[task_id], back_populates="message")
    candidate = relationship("Candidate", foreign_keys=[candidate_id], back_populates="message")
    user = relationship("User", foreign_keys=[user_id], back_populates="message")
    subject = db.Column(db.String, nullable=False)
    text_content = db.Column(db.Text, nullable=False)
    sent_date = db.Column(db.Date, nullable=True)
    sent_time = db.Column(db.Time, nullable=True)



db.create_all()

###################################### MANAGING USER SESSION ###########################################

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None

# ADMIN ONLY DECORATOR FUNCTION
def admin_only(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403, description="You are not authorized not logged in as admin")
        return function(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.login.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('The password seems incorrect. Try again')
        else:
            flash('The user with provided login does not exist')
    return render_template('login.html', form=form, current_user=current_user, is_authenticated=current_user.is_authenticated)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


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
        if not user_email:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash('The email provided already exists in the database. Please select another one or log in to your account')
    else:
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                flash(err)

    return render_template('register.html', form=form, current_user=current_user, is_authenticated=current_user.is_authenticated)

@app.route('/', methods=['GET'])
def landing_page():
    return render_template('get_started.html')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    users = db.session.query(User).all()
    data_pending=[]
    data_new_tasks=[]
    data_completed_tasks=[]
    for user in users:
        pipeline_pending_tasks = Task.query.filter_by(recipient_id=user.id, pipeline_status="pending", status="accepted").all()
        pending_task={
            'user_name': user.full_name,
            'task_count': len(pipeline_pending_tasks),
        }
        data_pending.append(pending_task)
        pipeline_new_tasks = Task.query.filter_by(recipient_id=user.id, pipeline_status="pending", status="pending").all()
        new_task={
            'user_name': user.full_name,
            'task_count': len(pipeline_new_tasks),
        }
        data_new_tasks.append(new_task)
        pipeline_completed_tasks = Task.query.filter_by(recipient_id=user.id, pipeline_status="completed").all()
        completed_tasks={
            'user_name': user.full_name,
            'task_count': len(pipeline_completed_tasks),
        }
        data_completed_tasks.append(completed_tasks)
    tasks_completed = len(Task.query.filter_by(pipeline_status="completed").all())
    tasks_accepted = len(Task.query.filter_by(pipeline_status="pending", status="accepted").all())
    tasks_pending = len(Task.query.filter_by(pipeline_status="pending", status="pending").all())
    data_tasks_status = {
        "completed": tasks_completed,
        "accepted": tasks_accepted,
        "pending": tasks_pending,
    }


    return render_template('index.html', current_user=current_user, is_authenticated=current_user.is_authenticated, data_pending=data_pending, data_new_tasks=data_new_tasks, data_completed_tasks=data_completed_tasks, data_tasks_status=data_tasks_status)


###################################### MANAGING COMMUNICATION TEMPLATES ###########################################

@app.route('/templates')
@login_required
def templates():
    templates = db.session.query(Template).all()
    return render_template('message-templates.html', templates=templates, current_user=current_user, is_authenticated=current_user.is_authenticated)

### TEMPLATE SHORT CODES ###
short_codes = {
    "USER_FULL_NAME": "{current_user.full_name}",
    "USER_FIRST_NAME": "{current_user.full_name}",
    "CANDIDATE_FULL_NAME": "{task.candidate.full_name}",
    "CANDIDATE_FIRST_NAME": "{task.candidate.first_name}",
    "RECRUITER_FIRST_NAME": "{task.from_user.first_name}",
    "RECRUITER_FULL_NAME": "{task.from_user.full_name}",
    "ROLE": "{task.role}",
    "INTERVIEW_DATE": "{task.interview_date}",
    "INTERVIEW_TIME": "{task.interview_time}",
    "INTERVIEWERS": "{task.interviewers}"
}

@app.route('/templates/new', methods=['POST', 'GET'])
@login_required
def new_template():
    form = NewTemplateForm()
    if form.validate_on_submit():
        # CHANGE USER ID LATER !!!
        new_template = Template(name=form.name.data, text=form.text.data, date=date.today(), owner_id=current_user.id)
        db.session.add(new_template)
        db.session.commit()
        return redirect(url_for('templates'))
    return render_template('create-template.html', short_codes=short_codes, form=form, current_user=current_user, is_authenticated=current_user.is_authenticated)


@app.route('/templates/edit/<int:template_id>', methods=['POST', 'GET'])
@login_required
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

    return render_template('edit-template.html', short_codes=short_codes, form=form, template_id=template_id, current_user=current_user, is_authenticated=current_user.is_authenticated)


@app.route('/templates/delete/<int:template_id>')
@login_required
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
        pipeline_status="pending",
    )
    return new_task

###################################### MANAGING PIPELINE ###########################################
#### PIPELINE SHOWS ONLY ACCEPTED TASKS! ###
@app.route('/pipeline')
@login_required
def pipeline():
    tasks = Task.query.filter_by(recipient_id=current_user.id, status="accepted").all()
    return render_template('pipeline.html', tasks=tasks, current_user=current_user, is_authenticated=current_user.is_authenticated)


@app.route('/pipeline/new', methods=['GET', 'POST'])
@login_required
def pipeline_new():
    form = NewInterviewForm()
    candidates = db.session.query(Candidate).all()
    candidates_list = [candidate.full_name for candidate in candidates]
    users = db.session.query(User).all()
    users_list = [user.full_name for user in users]
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
@login_required
def pipeline_edit(task_id):
    task = Task.query.get(task_id)
    form = InterviewEditForm(
        role=task.role,
        interviewers=task.interviewers,
        interview_date=task.interview_date,
        interview_time=task.interview_time,
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
@login_required
def pipeline_delete(task_id):
    task_to_delete = Task.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('pipeline'))

@app.route('/pipeline/complete/<int:task_id>')
@login_required
def pipeline_complete(task_id):
    task_completed = Task.query.get(task_id)
    task_completed.pipeline_status = "completed"
    task_completed.date_completed = date.today()
    task_completed.time_completed = datetime.now().time()
    db.session.commit()
    return redirect(url_for('pipeline'))

@app.route('/pipeline/cancel/<int:task_id>')
@login_required
def pipeline_cancel(task_id):
    task_cancelled = Task.query.get(task_id)
    task_cancelled.pipeline_status = "cancelled"
    db.session.commit()
    return redirect(url_for('pipeline'))


###################################### MANAGING INBOX ###########################################
##### INBOX SHOWS ALL PENDING, ACCEPTED AND DELEGATED TASKS BY CURRENT USER. !!!! IT DOES NOT SHOW ARCHIVED ONES THOUGH !!!!

@app.route('/tasks/new', methods=['POST', 'GET'])
@login_required
def tasks_new():
    candidates = db.session.query(Candidate).all()
    candidates_list = [candidate.full_name for candidate in candidates]
    users = db.session.query(User).all()
    users_list = [user.full_name for user in users]
    form = NewTaskForm()

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
@login_required
def task_accept(task_id):
    accepted_task = Task.query.filter_by(id=task_id).first()
    accepted_task.status = "accepted"
    accepted_task.date_received = date.today()
    db.session.commit()
    flash(f"You have just accepted the task. Find more interview details in Pipeline section")
    return redirect(url_for('inbox'))


def get_tasks_count():
    delegations = Task.query.filter_by(delegate_id=current_user.id).all()
    delegated_list = []
    for task in delegations:
        if task.delegate_id == current_user.id and task.recipient_id != current_user.id:
            delegated_list.append(task)
    delegated_count = len(delegated_list)
    accepted_count = len(Task.query.filter_by(recipient_id=current_user.id, status="accepted", pipeline_status="pending").all())
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
@login_required
def task_delegate(task_id):
    user_tasks = Task.query.filter_by(recipient_id=current_user.id).all()
    new_task_form = NewTaskForm()
    form = DelegateTaskForm()
    users = db.session.query(User).all()
    users_list = [user.full_name for user in users]
    form.delegate_id.choices = users_list
    if form.validate_on_submit():
        chosen_recipient = User.query.filter_by(full_name=form.delegate_id.data).first()
        delegated_task = Task.query.filter_by(id=task_id).first()
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
    return render_template("modal_delegate.html", new_task_form=new_task_form, user_tasks=user_tasks, form=form, task_id=task_id, current_user=current_user, tasks_count=get_tasks_count(), delegated_tasks=get_delegations())

######### CHECKING TASKS DETAILS ###########

@app.route('/check_tasks_details/<int:task_id>')
@login_required
def check_task_details(task_id):
    task = Task.query.get(task_id)
    messages = task.message
    return render_template('view_task.html', task_id=task_id, task=task, messages=messages)

###################################### MANAGING USERS IN ADMIN PANEL ###########################################

@app.route('/users')
@login_required
def users():
    users = db.session.query(User).all()
    return render_template('users.html', users=users)


@app.route('/users/new', methods=['POST', 'GET'])
@login_required
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
@login_required
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
@login_required
def user_delete(user_id):
    deleted_user = User.query.get(user_id)
    db.session.delete(deleted_user)
    db.session.commit()
    return redirect(url_for('users'))


###################################### MANAGING Candidates #########################################


@app.route('/candidates')
@login_required
def candidates():
    candidates = db.session.query(Candidate).all()


    return render_template('candidates.html', candidates=candidates, current_user=current_user)

@app.route('/candidates/new', methods=['POST', 'GET'])
@login_required
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

@app.route('/candidate/show_cv/<int:candidate_id>')
@login_required
def show_cv(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    candidate_cv = candidate.cv
    return send_from_directory('Uploads/CVs', candidate_cv)


@app.route('/inbox')
@login_required
def inbox():
    user_tasks = Task.query.filter_by(recipient_id=current_user.id).all()
    new_task_form = NewTaskForm()
    return render_template('inbox.html', user_tasks=user_tasks, tasks_count=get_tasks_count(), current_user=current_user, delegated_tasks=get_delegations(), new_task_form=new_task_form)

def send_email(message, recipient, cc):

    sender = "yourgemcrm@gmail.com"

    password = EMAIL_PASSWORD

    msg = MIMEMultipart('alternative')
    msg['Subject'] = message.subject
    msg['From'] = current_user.email
    msg['To'] = recipient
    msg['Cc'] = cc
    html = message.text_content
    converted_text = MIMEText(html, 'html')
    msg.attach(converted_text)

    # Send the message via local SMTP server.
    s = smtplib.SMTP_SSL("smtp.gmail.com", port=465)
    s.login(sender, password)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()




@app.route('/send_message/<task_id>', methods=['POST', 'GET'])
@login_required
def send_message(task_id):
    task = Task.query.get(task_id)
    templates = db.session.query(Template).all()
    templates_text = {template.name: template.text.format(task=task, current_user=current_user) for template in templates}

    templates_names_list = [template.name for template in templates]
    templates_names_list.insert(0, "")
    form = SelectTemplateForm()
    form.templates.choices = templates_names_list

    message_form = MessageForm(
        send_to=task.candidate.email,
        carbon_copy=task.from_user.email,
        subject=f"Interview with {task.candidate.full_name} for the role of {task.role}",
    )

    if message_form.validate_on_submit() and message_form.send.data:
        new_message = Message(
            user=current_user,
            candidate=task.candidate,
            task=task,
            subject=message_form.subject.data,
            text_content=message_form.text.data,
            sent_date=datetime.today(),
            sent_time=datetime.now().time(),
        )
        send_email(message=new_message, recipient=message_form.send_to.data, cc=message_form.carbon_copy.data)
        db.session.add(new_message)
        db.session.commit()
        flash('The message has been successfully sent!')
        return redirect(url_for('pipeline'))

    elif form.validate_on_submit() and form.select.data:
        chosen_template = templates_text[form.templates.data]
        message_form.text.data = chosen_template
    else:
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                flash(err)

    return render_template('send_message.html', templates=templates, form=form, task=task, task_id=task_id, message_form=message_form, current_user=current_user)

if __name__ == "__main__":
    app.run(debug=True)