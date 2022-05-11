from flask import Flask
from web import routes
from flask_login import LoginManager
from web.auth import User
from decouple import config
import logging

def create_app(SECRET_KEY):
    app = Flask(__name__)
    app.config['SECRET_KEY']=SECRET_KEY
    logging.basicConfig(level=logging.DEBUG)

    app.logger.debug('Validating settings')
    user=config('web_username',default='')
    if user=='':
        app.logger.warning('User settings is empty defaulting to admin')

    password=config('web_userpassword',default='')
    if password=='':
        app.logger.error('Password not defined')
    else:
        app.logger.info('Password configured')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message=''
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(config('web_username',default='admin'),1)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

