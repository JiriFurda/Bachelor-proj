#!/usr/bin/env python2

from flask import Flask, render_template, request, abort
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import pprint

app = Flask(__name__)
client = Elasticsearch()


@app.route('/')
def results():
    # Available facets for filter
    facets = {
        'year':
            {
                'label': 'Year',
                'field': 'year',
            },
        'programme':
            {
                'label': 'Programme',
                'field': 'fundedUnder.programme',
            },
        'subprogramme':
            {
                'label': 'Subprogramme',
                'field': 'fundedUnder.subprogramme',
            },
    }

    search = Search(using=client, index='xstane34_projects')
    search = search.highlight('objective')

    # Process query send through GET request
    if request.args.has_key('query'):
        search = search.query(
            Q('multi_match', query=request.args.get('query'), fields=['title', 'objective', 'acronym']))

    # Process facet filters sent through GET request
    facets_query = None

    for arg_name, arg_value in request.args.iteritems(True):  # Walk through every GET argument
        if arg_name in facets:  # If GET argument key is in facets dictionary
            field = facets[arg_name]['field']
            field = field.replace('.',
                                  '__')  # Access nested fields @see https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#dotted-fields

            if facets_query is None:
                facets_query = Q("match", **{field: arg_value})  # Create new query
            else:
                facets_query = facets_query | Q("match", **{field: arg_value})  # Append to existing query

    if facets_query is not None:  # If any facet is used
        search = search.query(facets_query)

    # Create facets aggregations (facet specific count in sidebar)
    for facet_name, facet_attributes in facets.items():
        search.aggs.bucket(facet_name, 'terms', field=facet_attributes['field'])

    # Execute the search
    response = search.execute()

    #
    for facet_name, facet_attributes in facets.items():
        facet_attributes['data'] = eval('response.aggregations.' + facet_name).buckets

    return render_template('results.html', results=response, facets=facets, get_arguments=request.args,
                           debug=Q("match").to_dict())


@app.route('/projects/<int:project_id>')
def projects_show(project_id):
    s = Search(using=client, index="xstane34_projects") \
        .query("match", id=project_id)
    response = s.execute()

    if response.success() == False or response.hits.total == 0:
        abort(404)

    return render_template('projects_show.html', project=response.hits[0])


@app.route('/json')
def json_results():
    s = Search(using=client, index="xstane34_projects") \
        .query("match", title="emotions")

    response = s.execute()

    return render_template('debug.html', debug=pprint.pprint(response.to_dict))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=2020)
