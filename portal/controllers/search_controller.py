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
from elasticsearch_dsl import Search, Q
from models.index_search import IndexSearch
import json, copy


search_controller = Blueprint('search', __name__)
client = Elasticsearch()


@search_controller.route('/')
def index():
    searches = IndexSearch.createForEveryIndex()
    IndexSearch.executeMany(searches)

    results = {
        'projects': searches['projects'].response,
        'deliverables': searches['deliverables'].response,
        'topics': searches['topics'].response
    }

    return render_template('search/index.html',
                           layout_data=searches[IndexSearch.getSearchType()].layout_data,
                           results=results,
                           searches=searches,
                           search_type=IndexSearch.getSearchType(),
                           debug=searches[IndexSearch.getSearchType()].search.to_dict()
                           )