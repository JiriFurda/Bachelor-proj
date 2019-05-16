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
#----------------------- Poslední úpravy: 16.5.2019 ------------------------#
#--- Soubor: topic_controller.py                              Verze: 1.0 ---#
#-------- http://knot.fit.vutbr.cz/wiki/index.php/rrs_eu_projects14 --------#
#--------------------- Licence: BUT Open source licence --------------------#
#---------------------------------------------------------------------------#


from flask import Blueprint, Flask, render_template, request, abort
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from models.index_search import IndexSearch
from models.topic import Topic
import json


topic_controller = Blueprint('topics', __name__, url_prefix='/topics')
client = Elasticsearch()


@topic_controller.route('/<string:topic_id>')
def show(topic_id):
    ''' Shows topic detail page '''

    # Search topic with given id
    s = Search(using=client, index="xfurda00_topics") \
        .query("match", identifier=topic_id)
    response = s.execute()

    # Check if topic was found
    if response.success() == False or response.hits.total == 0:
        abort(404)

    # Cast topic to object
    topic = Topic(response.hits[0])

    # Prepare Elasticsearch query with selected topic
    searches = IndexSearch.createForEveryIndex()
    for (name, search) in searches.items():
        if name != 'topics':
            search.search_raw = search.search_raw.query('match', topics__code__keyword=topic.body.identifier)
            search.search = search.search.query('match', topics__code__keyword=topic.body.identifier)
    IndexSearch.executeMany(searches)

    # Mark the topic as selected in the sidebar
    parsed_vue_facets = json.loads(searches['projects'].layout_data['vue_facets'])
    for k, vue_facet in enumerate(parsed_vue_facets):
        if vue_facet['name'] == 'topic':
            parsed_vue_facets[k]['checkedOptions'] = vue_facet['mostFrequentOptions']
    searches['projects'].layout_data['vue_facets'] = json.dumps(parsed_vue_facets)

    return render_template('topics/show.html',
                           topic=topic,
                           similar_topics=topic.similar(3),
                           layout_data=searches[IndexSearch.getSearchType()].layout_data
                           )