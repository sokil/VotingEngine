from flask import Blueprint, current_app, redirect

auth = Blueprint('auth', __name__)


@auth.route('/auth/form/<auth_method>')
def auth_form(auth_method):

    host = current_app.config['HOSTNAME']

    # redirect
    if auth_method == 'vkontakte':
        vk_auth_host = current_app.config['AUTH_VKONTAKTE_HOST']
        vk_app_id = current_app.config['AUTH_VKONTAKTE_APP_ID']

        auth_url = "%s/authorize?client_id=%dredirect_uri=http://%s/auth/vkontakte&scope=2" % (vk_auth_host, vk_app_id, host)

    else:
        raise Exception('Wrong auth method')

    return redirect(auth_url)


@auth.route('/auth/<auth_method>')
def auth():
    pass