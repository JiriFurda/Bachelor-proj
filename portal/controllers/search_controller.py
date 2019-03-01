#!/usr/bin/env python2

from flask import Blueprint, request, abort, url_for, redirect
from elasticsearch import Elasticsearch

search_controller = Blueprint('search', __name__)
client = Elasticsearch()


@search_controller.route('/')
def index():
    if request.args.has_key('search'):
        if request.args.get('search') == 'topics':
            return redirect(url_for('topics.index') + '?' + request.query_string)
        if request.args.get('search') == 'topics':
            return redirect(url_for('projects.index')+'?'+request.query_string)

    abort(500, 'Invalid search type')