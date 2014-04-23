from flask import Blueprint, render_template, request, jsonify, current_app, redirect, session, url_for, flash
from flask_login import current_user, login_required
from flask_babel import gettext

voting = Blueprint('voting', __name__)

"""
Voting list
"""
@voting.route("/")
def voting_list():
    from models.voting import Voting
    voting_list = Voting.query.all()

    return render_template('voting_list.html', voting_list=voting_list)

"""
Voting editor
"""
@voting.route('/voting/new')
@voting.route('/voting/edit/<voting_id>')
def voting_edit(voting_id=None):

    from models.voting import Voting
    if voting_id:
        voting_instance = Voting.query.get(voting_id)
    else:
        voting_instance = Voting()

    return render_template('voting_edit.html', voting=voting_instance)


"""
Voting page
"""
@voting.route('/voting/<voting_id>')
def voting_variants(voting_id):
    from models.voting import Voting
    voting_instance = Voting.query.get(voting_id)

    from flask_login import current_user

    return render_template('voting_variants.html', voting=voting_instance, user=current_user)


"""
Save vote
"""
@voting.route('/voting/save', methods=['POST'])
def voting_save():
    from models.voting import Voting
    if request.form.get('id'):
        voting_instance = Voting.query.get(request.form.get('id'))
    else:
        voting_instance = Voting()

    voting_instance.name = unicode(request.form['name'])

    from app import db
    db.session.add(voting_instance)
    db.session.commit()

    return redirect(url_for('voting.voting_edit', voting_id=voting_instance.id))

"""
New voting variant
"""
@voting.route('/voting/<voting_id>/new_variant')
def variant_new(voting_id=None):

    from models.voting_variant import VotingVariant
    variant_instance = VotingVariant(voting_id=voting_id)

    return render_template('voting_variant_edit.html', variant=variant_instance)


"""
Edit voting variant
"""
@voting.route('/voting/edit_variant/<variant_id>')
def variant_edit(variant_id=None):

    from models.voting_variant import VotingVariant
    variant_instance = VotingVariant.query.get(variant_id)

    return render_template('voting_variant_edit.html', variant=variant_instance)


"""
Save voting variant
"""
@voting.route('/voting/save_variant', methods=['POST'])
def variant_save():

    from models.voting_variant import VotingVariant

    if request.form.get('id'):
        variant_instance = VotingVariant.query.get(request.form.get('id'))
    else:
        if 'voting_id' not in request.form:
            raise Exception('Voting not specified');

        variant_instance = VotingVariant(voting_id=request.form['voting_id'])

    variant_instance.title = request.form['title']
    variant_instance.description = request.form['description']

    from app import db
    db.session.add(variant_instance)
    db.session.commit()

    return redirect(url_for('voting.variant_edit', variant_id=variant_instance.id))


"""
Show results
"""
@voting.route('/voting/result/<voting_id>')
@login_required
def voting_result(voting_id):

    # Check if user voted in this voting
    from models.vote import Vote
    if Vote.query.filter_by(voting_id=voting_id, user_id=current_user.get_id()).first() is None:
        flash(gettext(u'You must vote first to see results'))
        return redirect(url_for('voting.voting_variants', voting_id=voting_id))

    # Get points of variants
    #
    # SELECT voting_variant_id, SUM(point) AS rate
    # FROM votes
    # WHERE voting_id = 5
    # GROUP BY voting_variant_id ORDER BY rate DESC
    from models.vote import Vote
    from sqlalchemy import func
    Vote.query.filter_by(voting_id=voting_id)

    # Get rates


    # get variants
    from models.voting import Voting

    return render_template('voting_result.html')