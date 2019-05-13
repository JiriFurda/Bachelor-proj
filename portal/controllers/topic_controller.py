#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------#
#-----------------             BAKALÁŘSKÁ PRÁCE            -----------------#
#----------------- Aktualizace portálu evropských projektů -----------------#
#-----------------     a jeho rozšíření o identifikaci     -----------------#
#-----------------     výsledků, souvisejících s tématy    -----------------#
#-----------------          nově vypisovaných výzev        -----------------#
#-----------------              FIT VUT v Brně             -----------------#
#----------------- Autor: Jiří Furda (2018-2019)           -----------------#
#----------------- Vedoucí: Doc. RNDr. Pavel Smrž, Ph.D.   -----------------#
#----------------------- Poslední úpravy: 13.5.2019 ------------------------#
#--- Soubor: topic_controller.py                              Verze: 1.0 ---#
#-------- http://knot.fit.vutbr.cz/wiki/index.php/rrs_eu_projects14 --------#
#--------------------- Licence: BUT Open source licence --------------------#
#---------------------------------------------------------------------------#


from flask import Blueprint, Flask, render_template, request, abort
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MoreLikeThis
from flask_paginate import Pagination, get_page_args
from models.topic import Topic
from models.index_search import IndexSearch
import json


topic_controller = Blueprint('topics', __name__, url_prefix='/topics')
client = Elasticsearch()


@topic_controller.route('/')
def index():
    search = Search(using=client, index='xfurda00_topics')

    if request.args.has_key('query') and request.args.get('query') != '':
        search = search.query(
            Q('multi_match', query=request.args.get('query'),
              fields=['identifier^6', 'title^5', 'tags^3', 'description']))

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 10
    paginate_from = (page - 1) * per_page
    paginate_to = paginate_from + per_page
    search = search[paginate_from:paginate_to]  # @todo Change to scan API becuase of large amount of data

    # Execute the search
    response = search.execute()

    total = response.hits.total
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')

    return render_template('topics/index.html', results=response,
                           get_arguments=request.args,
                           page=page,
                           per_page=per_page,
                           pagination=pagination)


@topic_controller.route('/<string:topic_id>')
def show(topic_id):
    s = Search(using=client, index="xfurda00_topics") \
        .query("match", identifier=topic_id)
    response = s.execute()

    if response.success() == False or response.hits.total == 0:
        abort(404)

    topic = response.hits[0]


    searches = IndexSearch.createForEveryIndex()
    for (name, search) in searches.items():
        search.search_raw = search.search_raw.query('match', topics__code__keyword=topic.identifier)
        search.search = search.search.query('match', topics__code__keyword=topic.identifier)
    IndexSearch.executeMany(searches)

    parsed_vue_facets = json.loads(searches['projects'].layout_data['vue_facets'])
    for k, vue_facet in enumerate(parsed_vue_facets):
        if vue_facet['name'] == 'topic':
            parsed_vue_facets[k]['checkedOptions'] = vue_facet['mostFrequentOptions']
    searches['projects'].layout_data['vue_facets'] = json.dumps(parsed_vue_facets)


    similar_search = Search(using=client,
                            index="xfurda00_topics")
    similar_search = similar_search.query(MoreLikeThis(like={'_id': topic.meta.id, '_index': 'xfurda00_topics', 'fields': ['tags', 'title^3']}))

    similar_response = similar_search.execute()

    #projects_response = Topic(topic_id).projects()

    projects_query = Topic(topic_id).projects_query()    # Projects to search in
    projects_query.aggs.bucket('coordinator_country', 'terms', field='coordinator.country.keyword')
    projects_query.aggs.bucket('participant_country', 'terms', field='participant.country.keyword')
    projects_response = projects_query.execute()

    countries_count = {}
    for item in projects_response.aggregations.participant_country.buckets:
        countries_count[item.key] = item.doc_count

    for item in projects_response.aggregations.coordinator_country.buckets:
        if item.key in countries_count:
            countries_count[item.key] += item.doc_count
        else:
            countries_count[item.key] = item.doc_count

    sorted_countries_count = sorted(countries_count.items(), key=lambda x: x[1], reverse=True)

    return render_template('topics/show.html',
                           topic=response.hits[0],
                           similar_topics=similar_response,
                           projects_in_topic=projects_response,
                           countries=sorted_countries_count,
                           layout_data=searches[IndexSearch.getSearchType()].layout_data)