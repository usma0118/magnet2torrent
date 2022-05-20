import logging
import uuid
from flask import Flask
from flask.logging import default_handler
from flask_login import LoginManager
from waitress import serve
from decouple import config
from web import routes
from web.auth import User

def create_app(secret_key, logging_handler):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key
    app.logger.removeHandler(default_handler)
    app.logger.handler = logging_handler

    if not config('web_auth', default = 'basic') =='basic':
        app.config['LOGIN_DISABLED']= True
        app.logger.warning('Swithing to OAuth2')
    else:
        user = config('web_username', default = '')
        if user == '':
            app.logger.warning('User settings is empty defaulting to admin')

        password = config('web_userpassword', default = '')
        if password == '':
            app.logger.error('Password not defined')
        else:
            app.logger.info('Password configured')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = ''
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(config('web_username', default = 'admin'), 1)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

def start_server():
    logger = logging.getLogger('waitress')
    webapp = create_app(config('webserver_secret', default= str(uuid.uuid4())), logger)
    serve(webapp, host= '0.0.0.0', port= config('webserver_port', default= '8080'), url_prefix= config('webserver_basepath', default= ''))
