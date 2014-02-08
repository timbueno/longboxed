# -*- coding: utf-8 -*-
"""
    longboxed.frontend.pull_list
    ~~~~~~~~~~~~~~~~~~

    Pull List blueprints
"""
import sys
from json import dumps

from flask import (Blueprint, jsonify, render_template, Response, request)
from flask.ext.login import current_user, login_required

from . import route
from ..forms import AddToPullList
from ..helpers import current_wednesday, refresh_bundle
from ..services import comics as _comics
from ..services import users as _users


bp = Blueprint('pull_list', __name__)


@route(bp, '/pull_list', methods=['GET', 'POST'])
@login_required
def pull_list():
    form = AddToPullList()
    return render_template('pull_list.html', form=form)


# @route(bp, '/ajax/typeahead')
# @login_required
# def typeahead():
#     """
#     AJAX method

#     Gets title names for all titles. This should go away someday
#     """
#     titles = [title.name for title in _comics.titles.all()]
#     return jsonify(titles=titles)

@route(bp, '/ajax/typeahead')
@login_required
def typeahead():
    """
    AJAX method

    Gets title names for all titles. This should go away someday
    """
    # titles = [
    #     {
    #         'value': title.id,
    #         'name': title.name
    #     }
    #     for title in _comics.titles.all()
    # ]
    titles = [title.name for title in _comics.titles.all()]
    return Response(dumps(titles), mimetype='application/json')

# @route(bp, '/ajax/remove_favorite', methods=['POST'])
# @login_required
# def remove_favorite():
#     """
#     AJAX method

#     Remove a favorite title from your pull list
#     """
#     try:
#         # Get the index of the book to delete
#         title = _comics.titles.get(long(request.form['id']))
#         # Delete comic at desired index
#         current_user.pull_list.remove(title)
#         # Save updated user
#         _users.save(current_user)
#         html = render_template('favorites_list.html')
#         refresh_bundle(current_user, current_wednesday())
#         return jsonify(success=True, html=html)
#     except:
#         print "Unexpected error:", sys.exc_info()[1]
#         return jsonify(success=False, html=None)


@route(bp, '/ajax/remove_from_pull_list', methods=['POST'])
@login_required
def remove_from_pull_list():
    """
    AJAX method

    Remove a favorite title from your pull list
    """
    try:
        print request.form['id']
        # Get the index of the book to delete
        title = _comics.titles.get(long(request.form['id']))
        # Delete comic at desired index
        current_user.pull_list.remove(title)
        # Save updated user
        _users.save(current_user)
        refresh_bundle(current_user, current_wednesday())
        response = {
            'status': 'success',
            'message': title.name+' removed from your pull list'
        }
    except:
        print "Unexpected error:", sys.exc_info()[1]
        response = {
            'status': 'error', 
            'message': 'Something went wrong...'
        }
    return jsonify(response)



@route(bp, '/ajax/add_to_pull_list', methods=['POST'])
@login_required
def add_to_pull_list():
    form = AddToPullList()
    response = {'status': 'fail', 'message': 'Title not being tracked by Longboxed'}
    if form.validate_on_submit():
        title = _comics.titles.first(name=request.form['title'])
        if title and title not in current_user.pull_list:
            current_user.pull_list.append(title)
            _users.save(current_user)
            # html = render_template('favorites_list.html')
            # html = 'thing'
            refresh_bundle(current_user, current_wednesday())
            response = {
                'status': 'success',
                'message': '<strong>'+title.name+'</strong> has been added to your pull list!',
                'data': {
                    'title': title.name,
                    'title_id': title.id
                }
            }
        else:
            response = {
                'status': 'fail',
                'message': '<strong>'+title.name+'</strong> is already on your pull list!',
                'data': {
                    'title': title.name,
                    'title_id': title.id
                }
            }
    return jsonify(response)


# @route(bp, '/ajax/add_favorite', methods=['POST'])
# @login_required
# def add_favorite():
#     """
#     AJAX method

#     Add a favorite title to your pull list
#     """
#     new_title = _comics.titles.first(name=request.form['new_favorite'])
#     if new_title not in current_user.pull_list:
#         current_user.pull_list.append(new_title)
#         _users.save(current_user)
#         html = render_template('favorites_list.html')
#         refresh_bundle(current_user, current_wednesday())
#         return jsonify(success=True, html=html)
#     else:
#         return jsonify(success=False, html=None)
