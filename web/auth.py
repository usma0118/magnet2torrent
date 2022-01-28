from email.policy import default
from flask import render_template, Blueprint,redirect, url_for,request,flash
from flask_login import login_user,logout_user,current_user,login_required
from decouple import config
import logging

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

    user=None
    if username==config('username',default='admin'):
        user = User(username,1)

    if not user or not user.check_password(password):
        flash('Invalid credentials')
        return render_template('login.html', title='Login', form=form)
    # login code goes here
    login_user(user, remember=remember)
    next_page = request.args.get('next')
    if not next_page or not is_safe_url(next_page):
        return redirect(url_for('main.index'))
    return redirect(next_page)

from urllib.parse import urlparse, urljoin
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


from flask_login import UserMixin
from argon2 import PasswordHasher
class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active
        ph=PasswordHasher()
        self.hash=ph.hash(config('password',default=''))

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def check_password(self, password:str):
        ph=PasswordHasher()
        return ph.verify(self.hash,password)