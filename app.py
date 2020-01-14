import os
import pdoc
import uuid
import codecs

from hashlib import sha256
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from forms import UploadForm, SignUpForm, LogInForm, ChangeForm, FilterForm

ALLOWED_EXTENSIONS = {'py'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://twewxikheafkcm:0a85002e32d391f3878c7a30f7c2f1545825c06fa5ec1a7c7e86b6f942df5e76" \
                                        "@ec2-107-21-97-5.compute-1.amazonaws.com:5432/d2v3n5k0dhe10"
app.config['SECRET_KEY'] = "kursovahorodniukserhii"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)
app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='kpistudydb@gmail.com',
    MAIL_PASSWORD='kpistudy129087',
))
mail = Mail(app)


class User(db.Model):

    __tablename__ = 'orm_user'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(45), nullable=False)
    user_username = db.Column(db.String(45), nullable=False)
    user_password = db.Column(db.String(64), nullable=False)

    files = db.relationship('File')


class File(db.Model):

    __tablename__ = 'orm_file'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(45), nullable=False)
    upload_time = db.Column(db.String(100), nullable=False)

    language_id = db.Column(db.Integer, db.ForeignKey('orm_language.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('orm_user.id'))


class Language(db.Model):

    __tablename__ = 'orm_language'

    id = db.Column(db.Integer, primary_key=True)
    language_name = db.Column(db.String(45), nullable=False)
    language_version = db.Column(db.String(20), nullable=False)
    language_release_date = db.Column(db.String(45), nullable=False)

    files = db.relationship('File')


class Documentation(db.Model):

    __tablename__ = 'orm_documentation'

    id = db.Column(db.Integer, primary_key=True)
    documentation_name = db.Column(db.String(100), nullable=False)

    file_id = db.Column(db.Integer, db.ForeignKey('orm_file.id'))


@app.route('/', methods=['GET'])
def home():
    return redirect('/documentation')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LogInForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = sha256(str(form.password.data).encode('utf-8')).hexdigest()
            print(password)
            user = User.query.filter_by(user_email=email).first()
            if user:
                try:
                    assert user.user_password == password
                except AssertionError:
                    return render_template('login.html', message='Password is wrong!', user=None, form=form)
                else:
                    session['username'] = email
                    return redirect('/')
            else:
                return render_template('login.html', message='User does not exist!', user=None, form=form)
        return render_template('error.html', message='Something is wrong', user=None)
    return render_template('login.html', message=' ', user=None, form=form)


@app.route('/unlogin', methods=['GET'])
def unlogin():
    session.pop('username', None)
    return redirect(url_for('login'))


def sha256_decode(text):
    return sha256(text.encode('utf-8')).hexdigest()


def is_password_correct(password, confirm):
    try:
        assert password == confirm
    except AssertionError:
        return False
    return True


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    form_login = LogInForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            username = form.username.data
            password = sha256_decode(form.password.data)
            confirm_password = sha256_decode(form.confirm_password.data)
            if is_password_correct(password, confirm_password):
                try:
                    user = User(user_email=email, user_username=username, user_password=password)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    return render_template('login.html',
                                           message=f'Try to log in, because user with email {email} does exist.',
                                           user=None, form=form_login)
                else:
                    try:
                        msg = Message(f"Hello, {username}!", sender="kpistudydb@gmail.com", recipients=[email])
                        mail.send(msg)
                    except Exception as e:
                        print(e)
                    return redirect(url_for('login'))
    return render_template('signup.html', user=None, form=form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/documentation', methods=['GET', 'POST'])
def documentation():
    if session.get('username'):
        form = UploadForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                name = form.file.data.filename
                if allowed_file(name):
                    form.file.data.save(os.path.join(os.path.abspath(''), 'review.py'))
                    libpath = os.path.abspath('templates')
                    try:
                        mod = pdoc.import_module('review')
                        doc = pdoc.Module(mod)
                        html = doc.html()
                    except Exception as e:
                        print(e)
                        return render_template('error.html',
                                               user=session.get('username'),
                                               message='Something wrong in your module!')
                    else:
                        now = datetime.now()
                        user = User.query.filter_by(user_email=session.get('username')).first()
                        file = File(user_id=user.id,
                                    file_name=name,
                                    language_id=1,
                                    upload_time=str(now))
                        db.session.add(file)
                        filename = str(uuid.uuid4())
                        file = File.query.filter_by(user_id=user.id, file_name=name, upload_time=str(now)).first()
                        doc = Documentation(documentation_name=filename, file_id=file.id)
                        db.session.add(doc)
                        db.session.commit()
                        with open(os.path.join(libpath, f"{filename}.html"), "w") as f:
                            f.write(html)
                        return html
                return render_template('error.html', user=session.get('username'), message='Not valid file format!')
            return render_template('error.html', message='Not valid form!', user=session.get('username'))
        return render_template('documentation.html', user=session.get('username'), form=form)
    return render_template('notlogin.html', user=None)


@app.route('/history', methods=['GET', 'POST'])
def history():
    if session.get('username'):
        result = list()
        form = FilterForm()
        user = User.query.filter_by(user_email=session.get('username')).first()
        if request.method == 'POST':
            if form.validate_on_submit():
                filter_name = str(form.filter.data)
                files = File.query.filter_by(user_id=user.id, file_name=filter_name).all()
            else:
                files = []
        else:
            files = File.query.filter_by(user_id=user.id).all()
        for file in files:
            doc = Documentation.query.filter_by(file_id=file.id).first()
            if doc is not None:
                res = list()
                res.append(file.file_name)
                res.append(file.upload_time)
                res.append(doc.documentation_name)
                result.append(res)
        return render_template('history.html', rows=result, user=session.get('username'), form=form)
    return redirect(url_for('anywhere'))


@app.route('/get_doc_by_filename', methods=['POST', 'GET'])
def get_doc_by_filename():
    if request.method == 'POST':
        if session.get('username'):
            filename = request.form['filename_by_get']
            path = os.path.abspath('templates')
            f = codecs.open((os.path.join(path, f'{filename}.html')), 'r')
            html = f.read()
            return html
        return render_template('notlogin.html', user=None)
    return redirect('/documentation')


@app.route('/send_mail_by_filename', methods=['POST', 'GET'])
def send_mail_by_filename():
    if request.method == 'POST':
        if session.get('username'):
            filename = request.form['filename_by_send']
            path = os.path.abspath('templates')
            try:
                f = codecs.open((os.path.join(path, f'{filename}.html')), 'r')
                html = f.read()
            except Exception as e:
                print(e)
                return render_template('error.html', user=session.get('username'), message='File does not exist!')
            else:
                try:
                    msg = Message(f"Your documentation", sender="kpistudydb@gmail.com",
                                  recipients=[session.get('username')])
                    msg.html = html
                    mail.send(msg)
                except Exception as e:
                    print(e)
                    flash('Something is wrong!')
                    return redirect(url_for('history'))
                else:
                    flash('Your documentation was successfully sent!')
                    return redirect(url_for('history'))
        return render_template('notlogin.html', user=None)
    return redirect('/documentation')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if session.get('username'):
        form = ChangeForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                old_password = sha256_decode(form.old_password.data)
                user = User.query.filter_by(user_email=session.get('username')).first()
                actual_password = user.user_password
                new_password = sha256_decode(form.new_password.data)
                confirm_password = sha256_decode(form.confirm_password.data)
                if is_password_correct(new_password, confirm_password) and \
                    is_password_correct(old_password, actual_password):
                    try:
                        user.user_password = new_password
                        db.session.add(user)
                        db.session.commit()
                    except Exception:
                        return render_template('error.html', message='Oops. Something is wrong!',
                                               user=session.get('username'))
                    return redirect(url_for('login'))
                else:
                    return render_template('error.html', message='Are you sure that password is right?')
            return render_template('error.html', message='Form is not valid', user=session.get('username'))
        return render_template('change.html', user=session.get('username'), form=form)
    return redirect(url_for('anywhere'))


@app.route('/<path:path>')
def anywhere(path):
    return render_template('404.html', user=session.get('username'))


if __name__ == '__main__':
    app.run(debug=True)
