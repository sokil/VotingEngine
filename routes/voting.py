from flask import Blueprint, render_template, request, jsonify, current_app, redirect, session, url_for, flash
from flask_login import login_required
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
@login_required
def voting_edit(voting_id=None):

    from models.voting import Voting
    if voting_id:
        voting_instance = Voting.query.get(voting_id)
    else:
        from flask_login import current_user
        voting_instance = Voting(owner_id=current_user.get_id())

    return render_template('voting_edit.html', voting=voting_instance)


"""
Voting page
"""
@voting.route('/voting/<voting_id>')
def voting_variants(voting_id):

    from flask_login import current_user

    # Check if user voted in this voting
    if current_user.is_authenticated():
        from models.vote import Vote
        if Vote.query.filter_by(voting_id=voting_id, user_id=current_user.get_id()).first() is not None:
            return redirect(url_for('voting.voting_result', voting_id=voting_id))

    # get voting
    from models.voting import Voting
    voting_instance = Voting.query.get(voting_id)

    return render_template('voting_variants.html', voting=voting_instance, user=current_user)


"""
Save voting
"""
@voting.route('/voting/save', methods=['POST'])
@login_required
def voting_save():
    from models.voting import Voting
    if request.form.get('id'):
        voting_instance = Voting.query.get(request.form.get('id'))
    else:
        from flask_login import current_user
        voting_instance = Voting(owner_id=current_user.get_id())

    voting_instance.name = unicode(request.form['name'])

    from app import db
    db.session.add(voting_instance)
    db.session.commit()

    return redirect(url_for('voting.voting_edit', voting_id=voting_instance.id))

"""
New voting variant
"""
@voting.route('/voting/<voting_id>/new_variant')
@login_required
def variant_new(voting_id=None):

    # get voting
    from models.voting import Voting
    voting_instance = Voting.query.get(voting_id)

    # check owner
    from flask_login import current_user
    if current_user != voting_instance.owner:
        raise Exception('Not allowed to edit voting')

    # create variant
    from models.voting_variant import VotingVariant
    variant_instance = VotingVariant(voting_id=voting_id)

    return render_template('voting_variant_edit.html', variant=variant_instance)


"""
Edit voting variant
"""
@voting.route('/voting/edit_variant/<variant_id>')
@login_required
def variant_edit(variant_id=None):

    # get variant
    from models.voting_variant import VotingVariant
    variant_instance = VotingVariant.query.get(variant_id)

    # get voting
    voting_instance = variant_instance.voting

    # check owner
    from flask_login import current_user
    if current_user != voting_instance.owner:
        raise Exception('Not allowed to edit voting')

    return render_template('voting_variant_edit.html', variant=variant_instance)


"""
Save voting variant
"""
@voting.route('/voting/save_variant', methods=['POST'])
@login_required
def variant_save():

    from models.voting_variant import VotingVariant

    if request.form.get('id'):
        variant_instance = VotingVariant.query.get(request.form.get('id'))
    else:
        if 'voting_id' not in request.form:
            raise Exception('Voting not specified');

        variant_instance = VotingVariant(voting_id=request.form['voting_id'])

    variant_instance.title = request.form['title'].strip()
    variant_instance.description = request.form['description']

    from app import db
    db.session.add(variant_instance)
    db.session.commit()

    return redirect(url_for('voting.voting_variants', variant_id=variant_instance.id))


"""
Show results
"""
@voting.route('/voting/result/<voting_id>')
@login_required
def voting_result(voting_id):

    # Check if user voted in this voting
    from models.vote import Vote
    from flask_login import current_user
    if Vote.query.filter_by(voting_id=voting_id, user_id=current_user.get_id()).first() is None:
        flash(gettext(u'You must vote first to see results'))
        return redirect(url_for('voting.voting_variants', voting_id=voting_id))

    # Get points of variants
    #
    # SELECT voting_variant_id, SUM(point) AS rate
    # FROM votes
    # WHERE voting_id = 5
    # GROUP BY voting_variant_id
    # ORDER BY rate DESC
    from models.vote import Vote
    from app import db
    from sqlalchemy.sql import func
    from sqlalchemy.sql import label
    vote_stat_list = db.session\
        .query(Vote.voting_variant_id, func.sum(Vote.point).label('rate'))\
        .filter_by(voting_id=voting_id)\
        .group_by(Vote.voting_variant_id)\
        .order_by('rate DESC')\
        .all()

    # get variants
    from models.voting import Voting
    voting_instance = Voting.query.get(voting_id)
    voting_variants = voting_instance.variants

    # prepare structure
    votes = []
    total_points = 0
    for vote_stat in vote_stat_list:
        for variant in voting_variants:
            if variant.id != vote_stat[0]:
                continue
            votes.append({
                'variant': variant,
                'rate': vote_stat[1]
            })
            voting_variants.remove(variant)
            total_points += vote_stat[1]
            break

    for variant in voting_variants:
        votes.append({
            'variant': variant,
            'rate': 0
        })

    # calc total stat
    for vote in votes:
        vote['percent'] = round(vote['rate'] / total_points * 100, 2)

    return render_template('voting_result.html', voting=voting_instance, votes=votes)