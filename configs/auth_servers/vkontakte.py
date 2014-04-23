#!/usr/bin/env python

"""
Mock server for Vk.com oAuth authorization
"""

# init app
from flask import Flask, request, redirect, jsonify, render_template_string
app = Flask(__name__)

# define routes
@app.route('/authorize')
def authorize():
    if 'client_id' not in request.args:
        return jsonify({
            "error": "invalid_client",
            "error_description": "client_id is incorrect"
        })

    if 'redirect_uri' not in request.args:
        return jsonify({
            "error": "invalid_request",
            "error_description": "redirect_uri has wrong domain, check application settings"
        })

    html = '<html><body><form action="/grant"><input type="hidden" name="redirect_uri" value="' + request.args.get('redirect_uri') + '"><input type="submit" value="Allow" /></form></body></html>'
    return render_template_string(html)


@app.route('/grant')
def grant():
    if 'redirect_uri' not in request.args:
        raise Exception('Redirect URI not specified')

    redirect_uri = request.args.get('redirect_uri') + '?code=AUTHORIZATION_CODE'
    return redirect(redirect_uri)

@app.route('/access_token')
def access_token():
    if 'client_id' not in request.args:
        return jsonify({
            "error": "invalid_client",
            "error_description": "client_id is incorrect"
        })

    if 'client_secret' not in request.args:
        return jsonify({
            "error": "invalid_client",
            "error_description": "client_secret is incorrect"
        })

    if 'code' not in request.args:
        return jsonify({
            "error": "invalid_grant",
            "error_description": "Code is invalid or expired."
        })

    if 'redirect_uri' not in request.args:
        return jsonify({
            "error": "invalid_grant",
            "error_description": "redirect_uri is undefined."
        })

    return jsonify({
        "access_token": "da9b87558d90d6a5a8d8247df5b65d3e1f07dc24d2d97f0d2d0adddda85d74d087f7c9bb138bd8246abb6",
        "expires_in": 86357,
        "user_id": 7777777
    })

@app.route('/method/<method>')
def method():
    if method == 'users.get':
        return jsonify({"response": [{"uid": 7777777, "first_name": "Lucky", "last_name": "Luke"}]})
    else:
        return render_template_string('Forbidden'), 403

# run server
app.run('127.0.0.1', 9876, True)