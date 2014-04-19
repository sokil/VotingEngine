import os

# Create app
from flask import Flask, request

# Init app
app = Flask(__name__)

# Configure app
app.config.from_object('configs.default.Config')

env = os.getenv('APPLICATION_ENV', 'development')
app.config.from_object('configs.' + env + '.Config')

# Register routes
from routes.voting import voting
app.register_blueprint(voting)

from routes.vote import vote
app.register_blueprint(vote)

# from routes.auth import auth
# app.register_blueprint(auth)

# Database connection
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from models.voting import Voting
from models.voting_variant import VotingVariant
from models.vote import Vote
from models.user import User

# Login manager
from flask_login import LoginManager
loginManager = LoginManager()
loginManager.login_view = 'auth.login'
loginManager.init_app(app)

@loginManager.user_loader
def load_user(email):
    return User.query.find(email=email)

# Localization
from flask_babel import Babel
babel = Babel(app)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['SUPPORTED_LANGUAGES'])

# Log errors
if app.config['LOGGER_ENABLED'] and len(app.config['LOGGER_EMAILS']) > 0:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler(
        app.config['SMTP_HOST'],
        app.config['SMTP_FROM'],
        app.config['LOGGER_EMAILS'],
        'Distributive Manager error'
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)