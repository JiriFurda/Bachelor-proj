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
#--- Soubor: facet_controller.py                              Verze: 1.0 ---#
#-------- http://knot.fit.vutbr.cz/wiki/index.php/rrs_eu_projects14 --------#
#--------------------- Licence: BUT Open source licence --------------------#
#---------------------------------------------------------------------------#


from flask import Blueprint, Flask, render_template, request, abort, jsonify
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import json, ast
from models.facet import Facet


facet_controller = Blueprint('facets', __name__, url_prefix='/facets')
client = Elasticsearch()


@facet_controller.route('/api/<string:facet_name>')
def showApi(facet_name):
    ''' Returns facet values in JSON formaat '''
    # Validate facet name
    facet = Facet.get(facet_name)
    if (facet is None):
        return

    # Load user Elasticsearch query
    search_dict = request.args.get('search_dict')  # Load GET parameter
    search_dict = ast.literal_eval(search_dict)  # Change single quotes to double quotes
    search_dict = json.loads(json.dumps(search_dict))

    # Find corresponding index to search in
    search_type = request.args.get('search_type')
    if search_type == 'deliverables':
        index = 'xstane34_deliverables'
    elif search_type == 'topics':
        index = 'xfurda00_topics'
    else:
        index = 'xstane34_projects'

    # Prepare basic query
    client = Elasticsearch()
    search = Search(using=client, index=index)  # Set search env
    search = search.update_from_dict(search_dict)  # Use main search query used
    search.aggs.bucket(facet.name, 'terms', field=facet.field, size=100)  # Aggregate the field

    # Apply search keyword
    if request.args.get('search_val') is not None:
        search_val = '*' + request.args.get('search_val') + '*'
        search = search.query('query_string', query=search_val, fields=[facet.field_no_keyword])

    # Execute search
    response = search.execute()

    # Process results
    results_es = eval('response.aggregations.' + facet.name).buckets
    results_arr = []
    for result_es in results_es:
        # Filter out non relevant results
        if request.args.get('search_val') is None or result_es.key.lower().find(request.args.get('search_val').lower()) != -1:
            results_arr.append({'text': result_es.key, 'value': result_es.key, 'count': result_es.doc_count})

    return jsonify(results_arr)