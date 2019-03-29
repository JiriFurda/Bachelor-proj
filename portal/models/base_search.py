from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from flask import request
from models.facet import Facet
import copy, json


client = Elasticsearch()


class BaseSearch:
    def __init__(self):
        self.indices = ['xstane34_projects', 'xstane34_deliverables']
        self.search_raw = self.buildSearch()    # Raw query
        self.search = self.buildAggregationsSearch()  # Query with facets aggregations
        self.response = self.search.execute()
        self.layout_data = self.prepareLayoutData()


    def buildSearch(self):
        es_search = Search(using=client, index=self.indices)
        es_search = es_search.query(
            Q('query_string', query=request.args.get('query', '*'),
              fields=['acronym^6', 'title^5', 'objective^3', 'fundedUnder.subprogramme^2', 'website.origWeb']))

        return es_search


    def buildAggregationsSearch(self):
        es_search = copy.copy(self.search_raw)

        facets = Facet.all()
        for facet in facets:
            es_search.aggs.bucket(facet.name, 'terms', field=facet.field, size=6)

        return es_search


    def prepareLayoutData(self):
        facets = Facet.all()

        vue_facets = ''
        for facet in facets:
            facet_dict = facet.toDict()
            facet_dict.update({'checkedOptions': []})

            aggregation = eval('self.response.aggregations.' + facet.name).buckets
            option_list = []
            for option in aggregation:
                option_list.append({
                    'value': option.key,
                    'text': option.key,
                    'count': option.doc_count,
                })
            facet_dict.update({'mostFrequentOptions': option_list})

            vue_facets += json.dumps(facet_dict)
            vue_facets += ','
        vue_facets = '[' + vue_facets[:-1] + ']'

        result = {
            'vue_facets': vue_facets,
            'vue_elastic_search': json.dumps(self.search_raw.to_dict()),
            'get_arguments': request.args
        }

        return result