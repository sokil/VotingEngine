from flask import Blueprint, current_app, redirect, render_template, request, url_for, session
from flask_login import login_required, login_user, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/login')
def auth_login():
    # define return url
    return_url = request.args.get('next')
    if return_url and return_url[0] != '/':
        return_url = None

    return render_template('auth_login.html', return_url=return_url)

@auth.route('/auth/form/<auth_method>')
def auth_form(auth_method):

    # redirect
    if auth_method == 'vkontakte':
        auth_url = "%s/authorize?client_id=%d&redirect_uri=%s&scope=2" % (
            current_app.config['AUTH_VKONTAKTE_HOST'],
            current_app.config['AUTH_VKONTAKTE_APP_ID'],
            'http://%s/auth/vkontakte' % current_app.config['HOSTNAME']
        )

    else:
        raise Exception('Wrong auth method')

    # define return url
    if 'return_url' in request.args:
        session['return_url'] = request.args.get('return_url')

    return redirect(auth_url)


@auth.route('/auth/<auth_method>')
def auth_check(auth_method):

    if auth_method == 'vkontakte':

        # get access token
        if 'code' not in request.args:
            raise Exception('Code not specified');

        code = request.args['code']

        url = '/access_token?client_id=%d&client_secret=%s&code=%s&redirect_uri=%s' % (
            current_app.config['AUTH_VKONTAKTE_APP_ID'],
            current_app.config['AUTH_VKONTAKTE_SECRET'],
            code,
            'http://%s/auth/vkontakte' % current_app.config['HOSTNAME']
        )

        import urllib2
        import json
        response = json.loads(urllib2.urlopen(current_app.config['AUTH_VKONTAKTE_HOST'] + url).read())

        # check user existence
        from models.user import User
        user_instance = User.query.filter_by(vkontakte_id=response['user_id']).first()

        # register
        if user_instance is None:
            from app import db
            user_instance = User(vkontakte_id=response['user_id'])
            db.session.add(user_instance)
            db.session.commit()

        # authorize
        login_user(user_instance)

    # return
    return_url = session.get('return_url') if session.has_key('return_url') else '/'
    return redirect(return_url)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')