#!/usr/bin/env python2

from flask import Blueprint, Flask, render_template, request, abort
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MoreLikeThis
from flask_paginate import Pagination, get_page_args
from collections import OrderedDict
from models.facet import Facet
from topic_controller import index as topic_index
import json

project_controller = Blueprint('projects', __name__, url_prefix='/projects')
client = Elasticsearch()


@project_controller.route('/')
def index():
    if request.args.has_key('search') and request.args.get('search') == 'topics':
        return topic_index()


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
    search_deliv = Search(using=client, index='xstane34_deliverables')
    search = search.highlight('objective')
    search_deliv = search_deliv.highlight('deliv.plainText')

    # Process query send through GET request
    if request.args.has_key('query-new') and request.args.get('query-new') != '':
         search = search.query(
            Q('query_string', query=request.args.get('query-new'),
              fields=['acronym^6', 'title^5', 'objective^3', 'fundedUnder.subprogramme^2', 'website.origWeb']))

    if request.args.has_key('query-new') and request.args.get('query-new') != '':
         search_deliv = search_deliv.query(
            Q('query_string', query=request.args.get('query-new'),
              fields=['deliv.plainText']))
    """
    # Process query send through GET request
    if request.args.has_key('query') and request.args.get('query') != '':
        search = search.query(
            Q('multi_match', query=request.args.get('query'),
              fields=['acronym^6', 'title^5', 'objective^3', 'fundedUnder.subprogramme^2', 'website.origWeb']))
    """

    # Process facet filters sent through GET request
    facets_query = None

    """
    for arg_name, arg_value in request.args.iteritems(True):  # Walk through every GET argument
        if arg_name in facets:  # If GET argument key is in facets dictionary
            field = facets[arg_name]['field']
            field = field.replace('.',
                                  '__') # Access nested fields @see https://elasticsearch-dsl.readthedocs.io/en
                                        # /latest/search_dsl.html#dotted-fields

            if facets_query is None:
                facets_query = Q("match", **{field: arg_value})  # Create new query
            else:
                facets_query = facets_query | Q("match", **{field: arg_value})  # Append to existing query
    """

    if facets_query is not None:  # If any facet is used
        search = search.query(facets_query)

    search_without_facets = search

    # Create facets aggregations (facet specific count in sidebar)
    for facet_name, facet_attributes in facets.items():
        search.aggs.bucket(facet_name, 'terms', field=facet_attributes['field'], size=6)

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 10
    paginate_from = (page - 1) * per_page
    paginate_to = paginate_from + per_page
    search = search[paginate_from:paginate_to]  # @todo Change to scan API becuase of large amount of data

    # Execute the search

    response = search.execute()
    response_deliv = search_deliv.execute()

    total = response.hits.total
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')

    #
    facets_data = {}
    for facet_name, facet_attributes in facets.items():
        facets_data[facet_name] = eval('response.aggregations.' + facet_name).buckets

    facets = Facet.all()
    vue_facets = ''
    for facet in facets:
        facet_dict = facet.toDict()
        facet_dict.update({'checkedOptions': []})

        option_list = []
        for option in facets_data[facet.name]:
            option_list.append({
                'value': option.key,
                'text': option.key,
                'count': option.doc_count,
            })
        facet_dict.update({'mostFrequentOptions': option_list})

        vue_facets += json.dumps(facet_dict)
        vue_facets += ','
    vue_facets = '['+vue_facets[:-1]+']'

    return render_template('projects/index.html',
                           results=response,
                           facets=Facet.all(),
                           facets_data=facets_data,
                           get_arguments=request.args,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           search_dict=search_without_facets.to_dict(),
                           es_query=json.dumps(search_without_facets.to_dict()),
                           vue_facets=vue_facets,
                           response_deliv=response_deliv,
                           debug=None)


@project_controller.route('/<int:project_id>')
def show(project_id):
    s = Search(using=client, index="xstane34_projects") \
        .query("match", id=project_id)
    response = s.execute()

    if response.success() == False or response.hits.total == 0:
        abort(404)

    project = response.hits[0]

    similar_search = Search(using=client, index="xstane34_projects") #{'_id': project.id, '_index': 'xstane34_projects'}
    similar_search = similar_search.query(MoreLikeThis(like={'_id': project.id, '_index': 'xstane34_projects'}))
    similar_response = similar_search.execute()


    return render_template('projects/show.html', project=project, similar_projects=similar_response[:3])