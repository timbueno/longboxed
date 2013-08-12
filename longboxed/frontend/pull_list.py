# -*- coding: utf-8 -*-
"""
    longboxed.frontend.pull_list
    ~~~~~~~~~~~~~~~~~~

    Pull List blueprints
"""
import sys

from flask import (Blueprint, jsonify, render_template, request)
from flask.ext.login import current_user, login_required

from . import route
from ..services import comics as _comics
from ..services import users as _users


bp = Blueprint('pull_list', __name__)


@route(bp, '/pull_list')
@login_required
def p():
    return render_template('pull_list.html')


@route(bp, '/ajax/typeahead')
@login_required
def typeahead():
    titles = [title.name for title in _comics.titles.all()]
    return jsonify(titles=titles)

@route(bp, '/ajax/remove_favorite', methods=['POST'])
@login_required
def remove_favorite(): 
    try:
        # Get the index of the book to delete
        title = _comics.titles.get(long(request.form['id']))
        # Delete comic at desired index
        current_user.pull_list.remove(title)
        # Save updated user
        _users.save(current_user)
        html = render_template('favorites_list.html')
        return jsonify(success=True, html=html)
    except:
        print "Unexpected error:", sys.exc_info()[1]
        return jsonify(success=False, html=None)


@route(bp, '/ajax/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    new_title = _comics.titles.first(name=request.form['new_favorite'])
    if new_title not in current_user.pull_list:
        current_user.pull_list.append(new_title)
        _users.save(current_user)
        html = render_template('favorites_list.html')
        return jsonify(success=True, html=html)
    else:
        return jsonify(success=False, html=None)
