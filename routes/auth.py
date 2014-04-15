from flask import Blueprint, jsonify, render_template, current_app, redirect, url_for, request, flash, session
from flask_login import login_required
from bson.objectid import ObjectId

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    pass

@auth.route('/logout')
@login_required
def logout():
    pass