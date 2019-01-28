#!/usr/bin/env python2

from flask import Flask, render_template, request, abort
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MoreLikeThis
from flask_paginate import Pagination, get_page_args
from collections import OrderedDict
import pprint
import json
import ast
from models.facets import Facet
from controllers.search_controller import SearchController

app = Flask(__name__)
client = Elasticsearch()


@app.route('/')
def results():
    return SearchController.render();

@app.route('/ajax_search_in_facet/<string:facet_name>')
def ajax_search_in_facet(facet_name):
    facet = Facet.get(facet_name)
    if(facet is None):
        return

    search_dict = request.args.get('search_dict')   # Load GET parameter
    search_dict = ast.literal_eval(search_dict)   # Change single quotes to double quotes
    search_dict = json.loads(json.dumps(search_dict))


    search = Search(using=client, index='xstane34_projects')    # Set search env
    search = search.update_from_dict(search_dict)   # Use main search query used
    search.aggs.bucket(facet.name, 'terms', field=facet.field, size=100)    # Aggregate the field

    if request.args.get('search_val') is not None:
        search_val = '*' + request.args.get('search_val') + '*'
        #search_val = search_val.lower() @todo wildcard seems to be case sensitive
        search = search.query('wildcard', **{facet.field: search_val}) # @todo experiment with __keyword


    response = search.execute()

    return render_template('ajax_search_in_facet.html', results=eval('response.aggregations.' + facet.name).buckets, facet=facet)


@app.route('/projects/<int:project_id>')
def projects_show(project_id):
    s = Search(using=client, index="xstane34_projects") \
        .query("match", id=project_id)
    response = s.execute()

    if response.success() == False or response.hits.total == 0:
        abort(404)

    project = response.hits[0]

    similar_search = Search(using=client, index="xstane34_projects") #{'_id': project.id, '_index': 'xstane34_projects'}
    similar_search = similar_search.query(MoreLikeThis(like={'_id': project.id, '_index': 'xstane34_projects'}))
    similar_response = similar_search.execute()


    return render_template('projects_show.html', project=project, similar_projects=similar_response[:3])

@app.route('/calls/<string:topic_id>')
def topics(topic_id):
    s = Search(using=client, index="xfurda00_topics") \
        .query("match", identifier=topic_id)
    response = s.execute()

    if response.success() == False or response.hits.total == 0:
        abort(404)

    return render_template('topic.html', topic=response.hits[0])


@app.route('/json')
def json_results():
    s = Search(using=client, index="xstane34_projects") \
        .query("match", title="emotions")

    response = s.execute()

    return render_template('debug.html', debug=json.dumps(response.hits[0].to_dict()))

@app.route('/json_calls')
def json_calls():
    s = Search(using=client, index="xfurda00_calls")

    response = s.execute()

    return render_template('debug.html', debug=json.dumps(response.to_dict()))

@app.route('/json_topics')
def json_topics():
    s = Search(using=client, index="xfurda00_topics")

    response = s.execute()

    return render_template('debug.html', debug=json.dumps(response.to_dict()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=2021)
