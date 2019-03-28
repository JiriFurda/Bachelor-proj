#!/usr/bin/env python2

from flask import Blueprint, request, abort, url_for, redirect, render_template
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from models.facet import Facet

search_controller = Blueprint('search', __name__)
client = Elasticsearch()


@search_controller.route('/')
def index():
    es_search_raw = buildSearch()
    es_search = appendAggregations(es_search_raw)


    return render_template('debug.html', debug=es_search.execute().aggregations.to_dict())

def buildSearch():
    es_search = Search(using=client, index=['xstane34_projects', 'xstane34_deliverables'])
    es_search = es_search.query(
        Q('query_string', query=request.args.get('query-new', 'test'),
          fields=['acronym^6', 'title^5', 'objective^3', 'fundedUnder.subprogramme^2', 'website.origWeb']))

    return es_search

def appendAggregations(es_search):
    facets = Facet.all()
    for facet in facets:
        es_search.aggs.bucket(facet.name, 'terms', field=facet.field, size=6)

    return es_search

