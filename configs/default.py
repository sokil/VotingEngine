class Config(object):
    HOSTNAME = 'voting'

    PORT = 9876
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/voting?charset=utf8'

    SECRET_KEY = 'fa+hq4;tr7q4@ra8*t62^783,.87'

    PERMANENT_SESSION_LIFETIME = 1200

    LOGGER_ENABLED = True
    LOGGER_EMAILS = []

    SMTP_FROM = None
    SMTP_HOST = '127.0.0.1'

    SUPPORTED_LANGUAGES = ['en', 'uk', 'ru']
    BABEL_DEFAULT_LOCALE = 'uk'

    AUTH_VKONTAKTE = False
    AUTH_VKONTAKTE_HOST = "https://oauth.vk.com"
    AUTH_VKONTAKTE_APP_ID = None
    AUTH_VKONTAKTE_SECRET = None
