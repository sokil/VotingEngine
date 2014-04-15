from app import db
from sqlalchemy import Column, String, Integer
from random import randint
from crypt import crypt


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    password = Column(String(255))
    salt = Column(String(255))

    votes = db.relationship("Vote", backref="persons")

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self['id']

    def set_password(self, password):
        # generate salt
        salt = u''
        alphabet = u'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!@#$%^&*()'
        alphabet_length = len(alphabet) - 1
        for i in range(0, 10):
            salt += alphabet[randint(0, alphabet_length)]

        # store password and salt
        self['password'] = self.get_password_hash(password, salt)
        self['salt'] = salt

        return self

    @staticmethod
    def get_password_hash(password, salt):
        return unicode(crypt(password, salt))

    def has_password(self, password):
        return self.get_password_hash(password, self['salt']) == self['password']