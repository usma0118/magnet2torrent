from email.policy import default
from flask import render_template, Blueprint,redirect, url_for,request,flash
from flask_login import login_user,logout_user,current_user,login_required
from decouple import config

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
   # login code goes here
    form=request.form
    username = form.get('username')
    password = form.get('password')
    remember = True if form.get('remember') else False

    user = User(username,1)

    if not user or not username==config('user') or not user.check_password(password):
        flash('Invalid credentials')
        # # is_safe_url should check if the url is safe for redirects.
        # # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        #     return flask.abort(400)
        return render_template('login.html', title='Login', form=form)
    # login code goes here
    login_user(user, remember=remember)
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('main.index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


from flask_login import UserMixin
from hashlib import sha256
class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active
        self.hash=sha256(config('password',default='').encode('utf-8')).hexdigest()

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def check_password(self, password):
        hash=sha256(password.encode('utf-8')).hexdigest()
        return True if hash == self.hash else False