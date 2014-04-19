from flask import Blueprint, render_template, request, jsonify, current_app, redirect, session
from flask_login import current_user

vote = Blueprint('vote', __name__)

@vote.route('/vote/save/<voting_id>', methods=['POST'])
def vote_save(voting_id):

    response = {'error': 0}

    try:

        # prepare vote
        from models.voting import Voting
        voting_instance = Voting.query.get(voting_id)

        # get variants
        if 'variant' not in request.form:
            raise Exception('Variants not passed')

        variant_id_list = voting_instance.filter_invalid_variants(request.form.getlist('variant'))

        # check permission to save
        if not current_user.is_authenticated():
            raise Exception('User not authorised')

        # save vote
        from app import db
        from models.vote import Vote
        point = len(voting_instance.variants)
        for variant_id in variant_id_list:
            db.session.add(Vote(voting_id=voting_id, voting_variant_id=variant_id, point=point, user_id=current_user['id']))
            point -= 1

        db.session.commit()

    except Exception, e:
        response['error'] = 1
        response['errorMessage'] = str(e)

    return jsonify(response)