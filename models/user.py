from app import db
from sqlalchemy import Column, String, Integer
from random import randint
from crypt import crypt


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), index=True)
    password = Column(String(255))
    role = Column(String(30), default='user')
    salt = Column(String(255))
    vkontakte_id = Column(Integer, index=True)

    votings = db.relationship('Voting', backref="users")
    votes = db.relationship("Vote", backref="users")

    def is_authenticated(self):
        return bool(self.get_id())

    def is_active(self):
        return True

    def is_anonymous(self):
        return not self.is_authenticated()

    def get_id(self):
        return self.id

    def has_role(self, role):
        return role == self.role

    def set_password(self, password):
        # generate salt
        salt = u''
        alphabet = u'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!@#$%^&*()'
        alphabet_length = len(alphabet) - 1
        for i in range(0, 10):
            salt += alphabet[randint(0, alphabet_length)]

        # store password and salt
        self.password = self.get_password_hash(password, salt)
        self.salt = salt

        return self

    @staticmethod
    def get_password_hash(password, salt):
        return unicode(crypt(password, salt))

    def has_password(self, password):
        return self.get_password_hash(password, self['salt']) == self['password']