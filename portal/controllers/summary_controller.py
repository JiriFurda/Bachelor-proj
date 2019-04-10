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

summary_controller = Blueprint('projects', __name__, url_prefix='/')
client = Elasticsearch()


@summary_controller.route('/')
def index():
    query = request.get

    projects = project_controller.search(query)
    deliverables = deliverables_controller.search(query)


