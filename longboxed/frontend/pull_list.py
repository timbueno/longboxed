# -*- coding: utf-8 -*-
"""
    longboxed.frontend.pull_list
    ~~~~~~~~~~~~~~~~~~

    Pull List blueprints
"""
import sys

from flask import (abort, Blueprint, jsonify, render_template, request, url_for)
from flask.ext.login import current_user, login_required
from flask.ext.wtf import Form

from . import route
from ..services import comics as _comics


bp = Blueprint('pull_list', __name__)


@route(bp, '/pull_list')
@login_required
def p():
    return render_template('pull_list.html')


@route(bp, '/ajax/typeahead')
@login_required
def typeahead():
    titles = _comics.distinct_titles()
    print 'DISTINCT TITLES: ', titles
    return jsonify(titles=titles)

@route(bp, '/ajax/remove_favorite', methods=['POST'])
@login_required
def remove_favorite(): 
    try:
        # Get the index of the book to delete
        i = int(request.form['id'])
        # Delete comic at desired index
        del current_user.pull_list[i]
        # Save updated user
        current_user.save()
        html = render_template('favorites_list.html')
        return jsonify(success=True, html=html)
    except:
        print "Unexpected error:", sys.exc_info()[1]
        return jsonify(success=False, html=None)


@route(bp, '/ajax/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    # print current_user.pull_list
    if request.form['new_favorite'] not in current_user.pull_list:
        current_user.pull_list.append(request.form['new_favorite'])
        # current_user.pull.sort()
        current_user.save()
        html = render_template('favorites_list.html')
        return jsonify(success=True, html=html)
    else:
        return jsonify(success=False, html=None)
