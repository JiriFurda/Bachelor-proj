#!/usr/bin/env python2

from flask import Flask, render_template, request, abort
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from flask_paginate import Pagination, get_page_args
from collections import OrderedDict
import pprint
import json

app = Flask(__name__)
client = Elasticsearch()


@app.route('/')
def results():

    # Available facets for filter
    facets = OrderedDict([
        ('programme',
            {
                'label': 'Programme',
                'field': 'fundedUnder.programme.keyword',
            }),
        ('subprogramme',
            {
                'label': 'Subprogramme',
                'field': 'fundedUnder.subprogramme.keyword',
            }),
        ('topic',
            {
                'label': 'Topic',
                'field': 'topics.title.keyword',
            }),
        ('funding',
            {
                'label': 'Funding scheme',
                'field': 'fundingScheme.code.keyword',
            }),
        ('coordinator',
            {
                'label': 'Coordinator',
                'field': 'coordinator.name.keyword',
            }),
        ('coordcountry',
            {
                'label': 'Coord. Country',
                'field': 'coordinator.country.keyword',
            }),
        ('year',
            {
                'label': 'Year',
                'field': 'year',
            })
    ])

    search = Search(using=client, index='xstane34_projects')
    #search = Search(using=client, index='xstane34_deliverables')
    search = search.highlight('objective')


    # Process query send through GET request
    if request.args.has_key('query') and request.args.get('query') != '':
        search = search.query(
            Q('multi_match', query=request.args.get('query'),
              fields=['acronym^6', 'title^5', 'objective^3', 'fundedUnder.subprogramme^2', 'website.origWeb']))



    # Process facet filters sent through GET request
    facets_query = None

    for arg_name, arg_value in request.args.iteritems(True):  # Walk through every GET argument
        if arg_name in facets:  # If GET argument key is in facets dictionary
            field = facets[arg_name]['field']
            field = field.replace('.', '__')    # Access nested fields @see https://elasticsearch-dsl.readthedocs.io/en
                                                # /latest/search_dsl.html#dotted-fields

            if facets_query is None:
                facets_query = Q("match", **{field: arg_value})  # Create new query
            else:
                facets_query = facets_query | Q("match", **{field: arg_value})  # Append to existing query

    if facets_query is not None:  # If any facet is used
        search = search.query(facets_query)


    # Create facets aggregations (facet specific count in sidebar)
    for facet_name, facet_attributes in facets.items():
        search.aggs.bucket(facet_name, 'terms', field=facet_attributes['field'], size=6)


    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 10
    paginate_from = (page-1)*per_page
    paginate_to = paginate_from+per_page
    search = search[paginate_from:paginate_to] # @todo Change to scan API becuase of large amount of data

    # Execute the search

    response = search.execute()


    total = response.hits.total
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')

    #
    for facet_name, facet_attributes in facets.items():
        facet_attributes['data'] = eval('response.aggregations.' + facet_name).buckets

    return render_template('results.html', results=response, facets=facets, get_arguments=request.args, page=page, per_page=per_page, pagination=pagination)


@app.route('/projects/<int:project_id>')
def projects_show(project_id):
    s = Search(using=client, index="xstane34_projects") \
        .query("match", id=project_id)
    response = s.execute()

    if response.success() == False or response.hits.total == 0:
        abort(404)

    return render_template('projects_show.html', project=response.hits[0])


@app.route('/json')
def json_results():
    s = Search(using=client, index="xstane34_projects") \
        .query("match", title="emotions")

    response = s.execute()

    return render_template('debug.html', debug=json.dumps(response.hits[0].to_dict()))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=2021)
