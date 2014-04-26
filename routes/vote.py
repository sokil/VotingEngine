from flask import Blueprint, render_template, request, jsonify, current_app, redirect, session, url_for
from flask_login import current_user

vote = Blueprint('vote', __name__)


@vote.route('/vote/save/<voting_id>', methods=['POST'])
def vote_save(voting_id=None):

    response = {'error': 0}

    try:
        from models.voting import Voting
        from models.vote import Vote

        # get variants
        if 'variant[]' not in request.form:
            raise Exception('Variants not passed')

        voting_instance = Voting.query.get(voting_id)
        variant_id_list = voting_instance.filter_invalid_variants(request.form.getlist('variant[]'))

        # check permission to save
        if current_user.is_authenticated():

            # Check if user voted in this voting
            if Vote.query.filter_by(voting_id=voting_id, user_id=current_user.get_id()).first() is not None:
                raise Exception('User already voted in this voting')

            # save vote
            from app import db
            point = len(voting_instance.variants)
            for variant_id in variant_id_list:
                db.session.add(Vote(voting_id=voting_id, voting_variant_id=variant_id, point=point, user_id=current_user.get_id()))
                point -= 1

            db.session.commit()

            response['redirect_url'] = url_for('voting.voting_page', voting_id=voting_id)

        else:
            session['vote'] = {
                'voting_id': voting_id,
                'variants': variant_id_list
            }

            if 'auth_method' not in request.form:
                raise Exception('Auth method not specified')

            response['redirect_url'] = url_for('auth.auth_form',
                auth_method=request.form.get('auth_method'),
                return_url=url_for('vote.vote_session_save')
            )

    except Exception, e:
        response['error'] = 1
        response['errorMessage'] = str(e)

    return jsonify(response)


@vote.route('/vote/ses_save', methods=['GET'])
def vote_session_save():

    # check permission to save
    if not current_user.is_authenticated():
        raise Exception('Not allowed to save')

    # prepare vote
    from models.voting import Voting
    from models.vote import Vote

    # get variants
    if 'vote' not in session:
        raise Exception('Variants not passed')

    voting_id = session['vote']['voting_id']

    voting_instance = Voting.query.get(voting_id)
    variant_id_list = session['vote']['variants']

    # Check if user voted in this voting
    if Vote.query.filter_by(voting_id=voting_id, user_id=current_user.get_id()).first() is not None:
        return redirect(url_for('voting.voting_page', voting_id=voting_id))

    # save vote
    from app import db
    from models.vote import Vote
    point = len(voting_instance.variants)
    for variant_id in variant_id_list:
        db.session.add(Vote(voting_id=voting_id, voting_variant_id=variant_id, point=point, user_id=current_user.get_id()))
        point -= 1

    db.session.commit()

    return redirect(url_for('voting.voting_page', voting_id=voting_id))