from app import db
from sqlalchemy import Column, String, Integer


class Voting(db.Model):
    __tablename__ = 'votings'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    variants = db.relationship("VotingVariant", backref="votings")