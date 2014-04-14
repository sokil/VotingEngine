from flask import Blueprint, render_template, request, jsonify

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


@voting.route('/voting/save/<voting_id>', methods=['POST'])
def voting_save(voting_id):

    response = {'error': 0}

    try:
        # get person
        person_id = 4

        # get voting
        from models.voting import Voting
        voting_instance = Voting.query.get(voting_id)

        # get voting variants
        valid_variant_id_list = [variant.id for variant in voting_instance.variants]
        voted_variant_id_list = [int(variant_if) for variant_if in request.form.getlist('variant')]

        variant_id_list = [variant_id for variant_id in voted_variant_id_list if variant_id in valid_variant_id_list]
        if len(variant_id_list) == 0:
            raise Exception('Wrong elements specified')

        # save vote
        from app import db
        from models.vote import Vote
        point = len(valid_variant_id_list)
        for variant_id in variant_id_list:
            db.session.add(Vote(voting_id=voting_id, voting_variant_id=variant_id, point=point, person_id=person_id))
            point -= 1

        db.session.commit()

    except Exception, e:
        response['error'] = 1
        response['errorMessage'] = str(e)

    return jsonify(response)