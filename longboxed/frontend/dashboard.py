# -*- coding: utf-8 -*-
"""
    longboxed.frontend.dashboard
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Frontend blueprints
"""
from flask import (current_app, Blueprint, g, jsonify, redirect,
                   render_template, url_for)
from flask.ext.security import current_user, login_required
from flask.ext.security.utils import logout_user
from flask.ext.wtf.csrf import generate_csrf
from werkzeug.local import LocalProxy

from . import route
from ..forms import DeleteUserAccountForm, UserInformationForm
from ..helpers import current_wednesday
from ..models import Issue, User


bp = Blueprint('dashboard', __name__)

@bp.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
    if not current_user.is_anonymous():
        g.user = current_user
    else:
        g.user = None


@route(bp, '/')
def index():
    issues = Issue.query.filter(Issue.on_sale_date == current_wednesday(), Issue.is_parent == True).\
                         order_by(Issue.num_subscribers.desc()).\
                         limit(4).\
                         all()
    if issues:
        for issue in issues:
            if issue.cover_image.original:
                featured = issue
                break
            featured = issues[0]
    else:
        featured = None
    return render_template('splash.html', issues=issues, featured=featured)


@route(bp, '/privacy')
def privacy():
    return render_template('privacy.html')


@route(bp, '/settings', methods=('GET', 'POST'))
@login_required
def settings():
    delete_user_account_form = DeleteUserAccountForm()
    user_info_form = UserInformationForm(obj=current_user)
    if user_info_form.validate_on_submit():
        user_info_form.populate_obj(current_user)
        current_user.save()
    return render_template('settings.html', user_info_form=user_info_form, delete_user_account_form=delete_user_account_form)


@route(bp, '/delete_account', methods=('GET', 'POST'))
@login_required
def delete_account():
    delete_user_account_form = DeleteUserAccountForm()
    if delete_user_account_form.validate_on_submit():
        user_temp = User.query.get(current_user.id)
        logout_user()
        _security_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)
        _security_datastore.delete_user(user_temp)
        _security_datastore.commit()
    return redirect(url_for('dashboard.index'))
