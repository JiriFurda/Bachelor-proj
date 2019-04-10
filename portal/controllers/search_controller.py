#!/usr/bin/env python2

from flask import Blueprint, request, abort, url_for, redirect, render_template
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from models.index_search import IndexSearch
import json, copy

search_controller = Blueprint('search', __name__)
client = Elasticsearch()


@search_controller.route('/')
def index():
    searches = IndexSearch.createForEveryIndex()

    results = {
        'projects': searches['projects'].response,
        'deliverables': searches['deliverables'].response,
        'topics': searches['topics'].response
    }
    #results = groupResults(baseSearch)

    return render_template('search/index.html',
                           layout_data=searches[getSearchType()].layout_data,
                           results=results,
                           searches=searches,
                           search_type=getSearchType(),
                           debug=searches['projects'].debug
                           )

def getSearchType():
    if request.args.get('type') == 'deliverables' or request.args.get('type') == 'topics':
        return request.args.get('type')

    return 'projects'

def groupResults(baseSearch):
    result = {}

    for index in baseSearch.indices:
        subsearch = copy.copy(baseSearch.search_raw)
        subsearch = subsearch.query(Q('term', _index=index))
        result.update({index: subsearch.execute()})

    return result

