from flask import Blueprint, render_template

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
    return render_template('voting_variants.html', voting=voting_instance)