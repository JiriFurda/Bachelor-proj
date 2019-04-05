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
    projectsSearch = IndexSearch('xstane34_projects',
                              'objective',
                              ['acronym^6', 'title^5', 'objective^3', 'fundedUnder.subprogramme^2', 'website.origWeb'])

    deliverablesSearch = IndexSearch('xstane34_deliverables',
                              'deliv.plainText',
                              ['deliv.sourceInfo.title^3', 'deliv.plainText'])

    results = {
        'xstane34_projects': projectsSearch.response,
        'xstane34_deliverables': deliverablesSearch.response
    }
    #results = groupResults(baseSearch)

    return render_template('search/index.html',
                           layout_data=projectsSearch.layout_data,
                           results=results,
                           debug=projectsSearch.debug
                           )

def groupResults(baseSearch):
    result = {}

    for index in baseSearch.indices:
        subsearch = copy.copy(baseSearch.search_raw)
        subsearch = subsearch.query(Q('term', _index=index))
        result.update({index: subsearch.execute()})

    return result

