#!/usr/bin/env python2

from flask import Blueprint, request, abort, url_for, redirect, render_template
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from models.facet import Facet
import json

search_controller = Blueprint('search', __name__)
client = Elasticsearch()


@search_controller.route('/')
def index():
    es_search_raw = buildSearch()   # Raw query
    es_search = appendAggregations(es_search_raw)   # Query with facets aggregations

    es_response = es_search.execute()

    layout_data = prepareLayoutData(es_search_raw, es_response)


    return render_template('debug.html',
                           layout_data = layout_data,
                           debug = es_search.execute().aggregations.to_dict()
                           )

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

def prepareLayoutData(es_search_raw, es_response):
    facets = Facet.all()

    vue_facets = ''
    for facet in facets:
        facet_dict = facet.toDict()
        facet_dict.update({'checkedOptions': []})

        aggregation = eval('es_response.aggregations.' + facet.name).buckets
        option_list = []
        for option in aggregation:
            option_list.append({
                'value': option.key,
                'text': option.key,
                'count': option.doc_count,
            })
        facet_dict.update({'mostFrequentOptions': option_list})

        vue_facets += json.dumps(facet_dict)
        vue_facets += ','
    vue_facets = '[' + vue_facets[:-1] + ']'

    result = {
        'vue_facets': vue_facets,
        'vue_elastic_search': json.dumps(es_search_raw.to_dict())
    }

    return result

