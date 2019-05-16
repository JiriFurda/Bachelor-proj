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
#--- Soubor: search_controller.py                             Verze: 1.0 ---#
#-------- http://knot.fit.vutbr.cz/wiki/index.php/rrs_eu_projects14 --------#
#--------------------- Licence: BUT Open source licence --------------------#
#---------------------------------------------------------------------------#


from flask import Blueprint, request, abort, url_for, redirect, render_template
from elasticsearch import Elasticsearch
from models.index_search import IndexSearch
from models.topic import Topic


search_controller = Blueprint('search', __name__)
client = Elasticsearch()


@search_controller.route('/')
def index():
    ''' Shows search results page '''

    # Create and execute searches
    search_type = IndexSearch.getSearchType()
    searches = IndexSearch.createForEveryIndex()
    IndexSearch.executeMany(searches)

    # Cast results to models
    casted_results = []
    if search_type == 'topics':
        casted_results = Topic.castFromResponse(searches['topics'].response)

    return render_template('search/index.html',
                           layout_data=searches[IndexSearch.getSearchType()].layout_data,
                           searches=searches,
                           search_type=search_type,
                           casted_results=casted_results,
                           )