from app import db
from sqlalchemy import Column, String, Integer, ForeignKey


class VotingVariant(db.Model):
    __tablename__ = 'voting_variants'

    id = Column(Integer, primary_key=True)
    voting_id = Column(Integer, ForeignKey('votings.id'))
    title = Column(String(255))
    description = Column(String(1000))

    voting = db.relationship('Voting')