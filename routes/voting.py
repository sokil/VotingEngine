from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user

voting = Blueprint('voting', __name__)


@voting.route("/")
def voting_list():
    from models.voting import Voting
    voting_list = Voting.query.all()

    return render_template('voting_list.html', voting_list=voting_list)


@voting.route('/voting/<voting_id>')
def voting_variants(voting_id):
    from models.voting import Voting
    voting_instance = Voting.query.get(voting_id)

    from flask_login import current_user

    return render_template('voting_variants.html', voting=voting_instance, user=current_user)


@voting.route('/voting/save/<voting_id>', methods=['POST'])
def voting_save(voting_id):

    response = {'error': 0}

    try:

        # check permission to save
        if not current_user.is_authenticated():
            raise Exception('User not authorised')

        # prepare vote
        from models.voting import Voting
        voting_instance = Voting.query.get(voting_id)
        variant_id_list = voting_instance.filter_invalid_variants(request.form.getlist('variant'))

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