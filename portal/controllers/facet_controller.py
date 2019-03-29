#!/usr/bin/env python2

from flask import Blueprint, Flask, render_template, request, abort, jsonify
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import json, ast
from models.facet import Facet

facet_controller = Blueprint('facets', __name__, url_prefix='/facets')
client = Elasticsearch()

@facet_controller.route('/api/<string:facet_name>')
def showApi(facet_name):
    facet = Facet.get(facet_name)
    if (facet is None):
        return

    search_dict = request.args.get('search_dict')  # Load GET parameter
    search_dict = ast.literal_eval(search_dict)  # Change single quotes to double quotes
    search_dict = json.loads(json.dumps(search_dict))

    client = Elasticsearch()
    search = Search(using=client, index='xstane34_projects')  # Set search env
    search = search.update_from_dict(search_dict)  # Use main search query used
    search.aggs.bucket(facet.name, 'terms', field=facet.field, size=100)  # Aggregate the field

    if request.args.get('search_val') is not None:
        search_val = '*' + request.args.get('search_val') + '*'
        search = search.query('query_string', query=search_val, fields=[facet.field_no_keyword])

    response = search.execute()

    results_es = eval('response.aggregations.' + facet.name).buckets
    results_arr = []
    #results_dict.update(response.to_dict())
    for result_es in results_es:
        results_arr.append({'text': result_es.key, 'value': result_es.key, 'count': result_es.doc_count})

    return jsonify(results_arr)