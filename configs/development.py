import default


class Config(default.Config):
    DEBUG = True

    AUTH_VKONTAKTE = True
    AUTH_VKONTAKTE_HOST = "http://127.0.0.1:9876"
    AUTH_VKONTAKTE_APP_ID = 1234567
    AUTH_VKONTAKTE_SECRET = 'qwertyuiopasdfghjklzxcvbnm'