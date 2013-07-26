# -*- coding: utf-8 -*-
"""
    longboxed.frontend.authorization
    ~~~~~~~~~~~~~~~~~~

    Authorization blueprints
"""
from datetime import datetime, timedelta

from flask import (Blueprint, current_app, flash, g,
                   request, redirect, url_for)
from flask.ext.login import current_user, login_required, login_user,logout_user
from rauth.service import OAuth2Service

import requests

from . import route
from ..core import login_manager
from ..services import users as _users

# Google OAuth Setup
GOOGLE_CLIENT_ID = '200273015685.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console

bp = Blueprint('authorization', __name__)

# rauth OAuth 2.0 service wrapper
service = OAuth2Service(
            name='google',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            access_token_url='https://accounts.google.com/o/oauth2/token',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            base_url='https://www.google.com/accounts/')


@login_manager.user_loader
def load_user(userid):
    print 'INSIDE USER LOADER: ', userid
    user = _users.find_user_with_id(userid)
    print user
    if user:
        user.last_login = datetime.now()
        user.save()
    return user

@bp.before_app_request
def before_request():
    print 'IN BEFORE APP REQUEST!!!!'
    print current_user.is_anonymous()
    if not current_user.is_anonymous():
        # get new access token if current one is expired
        if datetime.utcnow() > current_user.expire_time:
            # print "GETTING NEW TOKEN!!"
            auth_response = service.get_raw_access_token(data={
                'refresh_token': current_user.refresh_token,
                'grant_type': 'refresh_token'
            })
            auth_data = auth_response.json()
            current_user.access_token = auth_data['access_token']
            current_user.expire_time = datetime.utcnow() + timedelta(seconds=int(auth_data['expires_in']))
            current_user.save()
        g.user = current_user
    else:
        g.user = None

@route(bp, '/logout')
@login_required
def logout():
    logout_user()
    g.user = None
    return redirect(url_for('dashboard.index'))

@route(bp, '/login')
def login():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('dashboard.index'))
    params={'scope': 'openid email https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/calendar',
            'response_type': 'code',
            'access_type': 'offline',
            'redirect_uri': url_for('.authorized', _external=True)}
    return redirect(service.get_authorize_url(**params))

@route(bp, REDIRECT_URI)
def authorized():
    if not 'code' in request.args:
        flash('DID NOT AUTHORIZE')
        return redirect(url_for('dashboard.index'))

    # make a request for the access token credentials using code
    redirect_uri = url_for('.authorized', _external=True)
    data = dict(code=request.args['code'], grant_type='authorization_code', redirect_uri=redirect_uri)

    auth_response = service.get_raw_access_token(data=data)
    auth_data = auth_response.json()

    # Get the user identity
    headers = {'Authorization': 'OAuth '+auth_data['access_token']}
    identity_response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo',
                                     headers=headers)
    identity_data = identity_response.json()

    if not _users.find_user_with_id(identity_data['id']):
        # print "CREATING NEW USER"
        identity = identity_data
        identity['access_token'] = auth_data['access_token']
        print 'AUTH_DATA ', auth_data
        identity['refresh_token'] = auth_data['refresh_token']
        create_new_user(identity)

    # Get the user and save token
    u = _users.find_user_with_id(identity_data['id'])
    u.access_token = auth_data['access_token']
    u.expire_time = datetime.utcnow() + timedelta(seconds=int(auth_data['expires_in']))
    u.save()

    # Login the user
    login_user(u)
    g.user = current_user

    return redirect(url_for('dashboard.index'))


def create_new_user(resp):
    # Create new user
    newUser = _users.new()
    newUser.userid = resp['id']
    # User Info
    newUser.email = resp['email']
    newUser.first_name = resp['given_name']
    newUser.last_name = resp['family_name']
    newUser.full_name = resp['name']

    # Set default calendar
    # newUser.default_cal = resp['email']
    newUser.settings.default_cal = resp['email']

    # Save tokens
    # newUser.access_token = resp['access_token']
    # newUser.refresh_token = resp['refresh_token']
    newUser.tokens.access_token = resp['access_token']
    newUser.tokens.refresh_token = resp['refresh_token']

    newUser.save()
    return