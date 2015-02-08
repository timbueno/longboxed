# -*- coding: utf-8 -*-
"""
    longboxed.api.users
    ~~~~~~~~~~~~~~~~~~~~

    Users endpoints
"""
from datetime import datetime
from datetime import date as _date

from flask import current_app, Blueprint, g, jsonify, request
from flask.ext.security.registerable import register_user
from werkzeug.datastructures import MultiDict
from werkzeug.local import LocalProxy

from ..models import Bundle, Title
from ..helpers import current_wednesday, next_wednesday, two_wednesdays
from .authentication import auth
from .errors import bad_request, forbidden
from . import route


_security = LocalProxy(lambda: current_app.extensions['security'])

bp = Blueprint('users', __name__, url_prefix='/users')


@route(bp, '/login')
@auth.login_required
def login():
    return jsonify(dict(user=g.current_user.to_json()))


@route(bp, '/register', methods=['POST'])
def register():
    form_class = _security.register_form
    form_data = MultiDict(request.json)
    form = form_class(form_data, csrf_enabled=False)
    if form.validate_on_submit():
        user = register_user(**form.to_dict())
        form.user = user
        message = 'User: %s created successfully!' % user.email
        return jsonify(dict(user=user.to_json(), message=message)), 200
    return jsonify(dict(errors=form.errors)), 400


@route(bp, '/delete', methods=['DELETE'])
@auth.login_required
def delete():
    email = g.current_user.email
    _security_datastore = LocalProxy(lambda:
            current_app.extensions['security'].datastore)
    _security_datastore.delete_user(g.current_user)
    _security_datastore.commit()
    return jsonify(dict(user=email, message='Successfully deleted user!'))


@route(bp, '/<int:id>/pull_list/', methods=['GET'])
@auth.login_required
def get_user_pull_list(id):
    if id != g.current_user.id:
        return forbidden('You do not have permission to access this users pull list')
    return jsonify({
        'user': g.current_user.email,
        'pull_list': [title.to_json() for title in g.current_user.pull_list]
    })


@route(bp, '/<int:id>/pull_list/', methods=['POST'])
@auth.login_required
def add_title_to_pull_list(id):
    if id != g.current_user.id:
        return forbidden('You do not have permission to access this users pull list')
    title_id = request.args.get('title_id', type=int)
    if title_id:
        title = Title.query.get_or_404(title_id)
    else:
        return bad_request('title_id: attribute not found')
    if title not in g.current_user.pull_list:
        g.current_user.pull_list.append(title)
        g.current_user = g.current_user.save()
        Bundle.refresh_user_bundle(g.current_user, current_wednesday())
        Bundle.refresh_user_bundle(g.current_user, next_wednesday())
        Bundle.refresh_user_bundle(g.current_user, two_wednesdays())
    else:
        return bad_request('Title is already on users pull list')
    return jsonify({
        'user': g.current_user.email,
        'pull_list': [t.to_json() for t in g.current_user.pull_list]
    })


@route(bp, '/<int:id>/pull_list/', methods=['DELETE'])
@auth.login_required
def remove_title_from_pull_list(id):
    if id != g.current_user.id:
        return forbidden('You do not have permission to access this users pull list')
    title_id = request.args.get('title_id', type=int)
    if title_id:
        title = Title.query.get_or_404(title_id)
    else:
        return bad_request('title_id: attribute not found')
    if title in g.current_user.pull_list:
        g.current_user.pull_list.remove(title)
        g.current_user = g.current_user.save()
        Bundle.refresh_user_bundle(g.current_user, current_wednesday())
        Bundle.refresh_user_bundle(g.current_user, next_wednesday())
        Bundle.refresh_user_bundle(g.current_user, two_wednesdays())
    else:
        return bad_request('Title is not on the users pull list')
    return jsonify({
        'user': g.current_user.email,
        'pull_list': [t.to_json() for t in g.current_user.pull_list]
    })


@route(bp, '/<int:id>/bundles/', methods=['GET'])
@auth.login_required
def get_user_bundles(id):
    if id != g.current_user.id:
        return forbidden('You do not have permission to access this users pull list')
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 5, type=int)
    date = request.args.get('date', current_wednesday())
    if isinstance(date, _date):
        pass
    elif isinstance(date, unicode):
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        return abort(404)
    pagination = Bundle.query.filter(
                                Bundle.user==g.current_user,
                                Bundle.release_date<=date)\
                             .order_by(Bundle.release_date.desc())\
                             .paginate(page, per_page=count, error_out=False)
    bundles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'bundles': [bundle.to_json() for bundle in bundles],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'count': count
    })


@route(bp, '/<int:id>/bundles/latest', methods=['GET'])
@auth.login_required
def get_latest_bundles(id):
    from ..comics.models import Bundle
    if id != g.current_user.id:
        return forbidden('You do not have permission to access this users pull list')
    b = Bundle.query.filter(
                        Bundle.user==g.current_user,
                        Bundle.release_date<=current_wednesday())\
                    .order_by(Bundle.release_date.desc())\
                    .first()
    return jsonify(b.to_json())
