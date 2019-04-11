from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from flask import request
from models.facet import Facet
import copy, json


client = Elasticsearch()


class IndexSearch:
    def __init__(self, index, highlight, fields):
        self.debug = None

        self.index = index
        self.highlight = highlight
        self.fields = fields

        self.search_raw = self.buildSearch()    # Raw query
        self.search = self.buildAggregationsSearch()  # Query with facets aggregations
        #self.response = self.search.execute()
        self.response = None

        #self.layout_data = self.prepareLayoutData()
        self.layout_data = None


    def execute(self):
        self.response = self.search.execute()
        self.layout_data = self.prepareLayoutData()


    def buildSearch(self):
        # Init Elasticsearch search instance
        es_search = Search(using=client, index=self.index)
        es_search = es_search.highlight(self.highlight)


        # Prepare query string
        if request.args.has_key('query') and request.args.get('query') != '':
            query = request.args.get('query')
        else:
            query = '*'

        query_string_query = Q('query_string', query=query, fields=self.fields)
        filters_query = IndexSearch.getFiltersQuery()

        es_search = es_search.query('bool', must=[query_string_query, filters_query])

        return es_search


    @staticmethod
    def getFiltersQuery():
        filter_queries = []

        # Loop through every GET argument
        for arg_name, arg_value in request.args.iteritems(True):
            facet = Facet.getByName(arg_name)
            if facet is not None: # If argument name corresponds to a facet
                facet_values = json.loads(arg_value)
                facet_name = facet.underscoreField()

                value_queries = []
                for facet_value in facet_values:
                    value_queries.append(Q('match', **{facet_name: facet_value['value']}))

                filter_queries.append(Q('bool', should=value_queries))

        return Q('bool', must=filter_queries)


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

            checkedOptions = []
            if facet.name in request.args:
                checkedOptions = json.loads(request.args.get(facet.name))
            facet_dict.update({'checkedOptions': checkedOptions})

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

    @staticmethod
    def createForIndex(index):
        if index == 'projects':
            return IndexSearch('xstane34_projects',
                              'objective',
                              ['acronym^6', 'title^5', 'objective^3', 'fundedUnder.subprogramme^2', 'website.origWeb'])
        if index == 'deliverables':
            return IndexSearch('xstane34_deliverables',
                              'deliv.plainText',
                              ['deliv.sourceInfo.title^3', 'deliv.plainText'])

        if index == 'topics':
            return IndexSearch('xfurda00_topics',
                              'description',
                              ['identifier^6', 'title^5', 'tags^3', 'description'])

    @staticmethod
    def createForEveryIndex():
        return {
            'projects': IndexSearch.createForIndex('projects'),
            'deliverables': IndexSearch.createForIndex('deliverables'),
            'topics': IndexSearch.createForIndex('topics')
        }

    @staticmethod
    def getSearchType():
        if request.args.get('type') == 'deliverables' or request.args.get('type') == 'topics':
            return request.args.get('type')

        return 'projects'

    @staticmethod
    def executeMany(searches):
        for (name, search) in searches.items():
            search.execute()