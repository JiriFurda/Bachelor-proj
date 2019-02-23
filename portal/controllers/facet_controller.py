#!/usr/bin/env python2

from flask import Blueprint, Flask, render_template, request, abort
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import json, ast
from models.facet import Facet

facet_controller = Blueprint('facets', __name__, url_prefix='/facets')
client = Elasticsearch()


@facet_controller.route('/<string:facet_name>')
def show(facet_name):
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
        # search_val = search_val.lower() @todo wildcard seems to be case sensitive
        search = search.query('wildcard', **{facet.field: search_val})  # @todo experiment with __keyword

    response = search.execute()

    return render_template('facets/index.html',
                           results=eval('response.aggregations.' + facet.name).buckets, facet=facet)