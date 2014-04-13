from app import db
from sqlalchemy import Column, String, Integer


class Person(db.Model):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)

    votes = db.relationship("Vote", backref="persons")