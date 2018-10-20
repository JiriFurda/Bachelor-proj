#!/usr/bin/env python2

from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import pprint

app = Flask(__name__)
client = Elasticsearch()

@app.route('/')
def index():
	s = Search(using=client, index="xstane34_projects") \
		.query("match", title="emotions")
		
	s.aggs.bucket('per_tag', 'terms', field='year')

	response = s.execute()


	return render_template('index.html', facets = response.aggregations.per_tag.buckets)

@app.route('/results')
def results():
	s = Search(using=client, index="xstane34_projects") \
		.query("match", title=request.args.get('q'))

	s.aggs.bucket('test', 'terms', field='year')
	s.aggs.bucket('year', 'terms', field='year')

	response = s.execute()

	facets = {
			'year' :
				{
					'label' : 'Year',
					'column' : 'year',
				},
			'test' :
				{
					'label' : 'Test',
					'column' : 'year',
				}
		}

	for facet_name, facet_attributes in facets.items():
		facet_attributes['data'] = eval('response.aggregations.'+facet_name).buckets




	return render_template('results.html', results = response, facets = response.aggregations.year.buckets, debug = facets)

@app.route('/json')
def json_results():
	s = Search(using=client, index="xstane34_projects") \
		.query("match", title="emotions")

	response = s.execute()

	return render_template('results.html', results = pprint.pprint(response.to_dict))

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=2020)
