from flask import Blueprint, render_template, render_template_string, request, jsonify, current_app, redirect, session, url_for, flash
from flask_login import login_required
from flask_babel import gettext

voting = Blueprint('voting', __name__)

"""
Voting list
"""
@voting.route("/")
def voting_list():
    from models.voting import Voting
    from sqlalchemy import or_

    query = Voting.query

    remote_address = request.remote_addr

    # get code of current country
    if remote_address != '127.0.0.1':
        import pygeoip
        geoip = pygeoip.GeoIP('./configs/geoip/GeoIP.dat')
        alpha2 = geoip.country_code_by_addr(remote_address)

        query = query.filter(or_(Voting.country.is_(None), Voting.country == alpha2))

    return render_template('voting_list.html', voting_list=query.all())

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

        # check permissions to edit
        from flask_login import current_user
        if not voting_instance.is_moderated_by(current_user):
            raise Exception('You are not allowed to moderate this voting')
    else:
        from flask_login import current_user
        voting_instance = Voting(owner_id=current_user.get_id())

    # get country list
    from pycountry import countries

    return render_template('voting_edit.html', voting=voting_instance, countries=countries)


"""
Voting page
"""
@voting.route('/voting/<voting_id>')
def voting_page(voting_id):

    # get voting
    from models.voting import Voting
    voting_instance = Voting.query.get(voting_id)
    if voting_instance is None:
        return render_template('error_notfound.html'), 404

    # check if allowed in current country
    if not voting_instance.is_allowed_for_country():
        flash(gettext('This voting not allowed in your country. Allowed only for %s' % voting_instance.country))
        return redirect(url_for('voting.voting_list'))

    from flask_login import current_user
    from models.vote import Vote

    # Show voting variants
    if not current_user.is_authenticated() or Vote.query.filter_by(voting_id=voting_id, user_id=current_user.get_id()).first() is None:
        return render_template('voting_variants.html', voting=voting_instance, user=current_user)

    # Get points of variants
    from app import db
    from sqlalchemy.sql import func, label
    vote_stat_list = db.session\
        .query(Vote.voting_variant_id, func.sum(Vote.point).label('rate'))\
        .filter_by(voting_id=voting_id)\
        .group_by(Vote.voting_variant_id)\
        .order_by('rate DESC')\
        .all()

    # get variants
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


"""
Save voting
"""
@voting.route('/voting/save', methods=['POST'])
@login_required
def voting_save():
    from models.voting import Voting
    from flask_login import current_user

    if request.form.get('id'):
        voting_instance = Voting.query.get(request.form.get('id'))

        # check permissions to edit
        if not voting_instance.is_moderated_by(current_user):
            raise Exception('You are not allowed to moderate this voting')
    else:
        voting_instance = Voting(owner_id=current_user.get_id())

    voting_instance.name = unicode(request.form['name'])

    if request.form.get('country'):
        voting_instance.country = unicode(request.form['country'])

    from app import db
    db.session.add(voting_instance)
    db.session.commit()

    return redirect(url_for('voting.voting_list'))

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

    return redirect(url_for('voting.voting_page', voting_id=variant_instance.voting_id))