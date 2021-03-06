from app import db
from flask import request, flash, url_for
from sqlalchemy import Column, String, Integer, ForeignKey, func, event


class Voting(db.Model):
    __tablename__ = 'votings'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    country = Column(String(2))
    token = Column(String(80))

    variants = db.relationship("VotingVariant", backref="votings", order_by="VotingVariant.title")
    owner = db.relationship('User')

    def filter_invalid_variants(self, voted_variant_id_list):
        voted_variant_id_list = [int(variant_id) for variant_id in voted_variant_id_list]
        valid_variant_id_list = [variant.id for variant in self.variants]

        variant_id_list = [variant_id for variant_id in voted_variant_id_list if variant_id in valid_variant_id_list]
        if len(variant_id_list) == 0:
            raise Exception('Wrong variants specified')

        return variant_id_list

    def get_voted_users_num(self):
        from models.vote import Vote
        result = db.session\
            .query(func.count(func.distinct(Vote.user_id)))\
            .filter_by(voting_id=self.id)\
            .first()

        return result[0] if len(result) > 0 else 0

    def is_owned_by(self, user):
        return user.get_id() == self.owner_id

    def is_moderated_by(self, user):
        return user.has_role('moderator') or self.is_owned_by(user)

    def is_allowed_for_country(self, alpha2=None):

        if not self.country:
            return True

        if alpha2:
            alpha2 = alpha2.upper()
        else:
            if request.remote_addr == '127.0.0.1':
                flash('<b>DEBUG!</b> This voting limited to %s' % self.country)
                return True

            import pygeoip
            geoip = pygeoip.GeoIP('./configs/geoip/GeoIP.dat')
            alpha2 = geoip.country_code_by_addr(request.remote_addr)

        return alpha2 == self.country

    @staticmethod
    def generate_token():
        import random
        alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'
        return ''.join([random.choice(alphabet) for _ in range(80)])

    def set_private(self):
        self.token = self.generate_token()
        return self

    def set_public(self):
        self.token = None
        return self

    def is_public(self):
        return not bool(self.token)

    def get_url(self):
        if not self.id:
            return None

        if self.is_public():
            return url_for('voting.voting_page', voting_id=self.id, _external=True)
        else:
            return url_for('voting.voting_page', voting_id=self.id, token=self.token, _external=True)