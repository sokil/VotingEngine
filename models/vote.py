from app import db
from sqlalchemy import Column, String, Integer, ForeignKey


class Vote(db.Model):
    __tablename__ = 'votes'

    id = Column(Integer, primary_key=True)
    voting_id = Column(Integer, ForeignKey('votings.id'))
    voting_variant_id = Column(Integer, ForeignKey('voting_variants.id'))
    point = Column(Integer)
    person_id = Column(Integer, ForeignKey('persons.id'))