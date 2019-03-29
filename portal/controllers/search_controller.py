#!/usr/bin/env python2

from flask import Blueprint, request, abort, url_for, redirect, render_template
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from models.base_search import BaseSearch
import json, copy

search_controller = Blueprint('search', __name__)
client = Elasticsearch()


@search_controller.route('/')
def index():
    baseSearch = BaseSearch()

    results = groupResults(baseSearch)

    return render_template('search/index.html',
                           layout_data=baseSearch.layout_data,
                           results=results,
                           )

def groupResults(baseSearch):
    result = {}

    for index in baseSearch.indices:
        subsearch = copy.copy(baseSearch.search_raw)
        subsearch = subsearch.query(Q('term', _index=index))
        result.update({index: subsearch.execute()})

    return result

