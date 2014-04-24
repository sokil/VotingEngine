from app import db
from sqlalchemy import Column, String, Integer, ForeignKey


class Voting(db.Model):
    __tablename__ = 'votings'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    variants = db.relationship("VotingVariant", backref="votings", order_by="VotingVariant.title")
    owner = db.relationship('User')

    def filter_invalid_variants(self, voted_variant_id_list):
        voted_variant_id_list = [int(variant_id) for variant_id in voted_variant_id_list]
        valid_variant_id_list = [variant.id for variant in self.variants]

        variant_id_list = [variant_id for variant_id in voted_variant_id_list if variant_id in valid_variant_id_list]
        if len(variant_id_list) == 0:
            raise Exception('Wrong variants specified')

        return variant_id_list