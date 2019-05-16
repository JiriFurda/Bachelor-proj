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
#--- Soubor: project_controller.py                            Verze: 1.0 ---#
#-------- http://knot.fit.vutbr.cz/wiki/index.php/rrs_eu_projects14 --------#
#--------------------- Licence: BUT Open source licence --------------------#
#---------------------------------------------------------------------------#


from flask import Blueprint, Flask, render_template, request, abort
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MoreLikeThis
from models.index_search import IndexSearch


project_controller = Blueprint('projects', __name__, url_prefix='/projects')
client = Elasticsearch()


@project_controller.route('/<int:project_id>')
def show(project_id):
    ''' Shows project detail page '''

    # Search project with given id
    s = Search(using=client, index="xstane34_projects") \
        .query("match", id=project_id)
    response = s.execute()

    # Check if project was found
    if response.success() == False or response.hits.total == 0:
        abort(404)

    project = response.hits[0]

    # Search for similar projects
    similar_search = Search(using=client, index="xstane34_projects")
    similar_search = similar_search.query(MoreLikeThis(like={'_id': project.id, '_index': 'xstane34_projects'}))
    similar_response = similar_search.execute()

    # Create search for current search type
    index_search = IndexSearch.createForIndex(IndexSearch.getSearchType())
    index_search.execute()

    return render_template('projects/show.html',
                           layout_data=index_search.layout_data,
                           project=project,
                           similar_projects=similar_response[:3]
                           )