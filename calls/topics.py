#!/usr/bin/env python2
import urllib, json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Text, Index, Nested, InnerDoc, Integer, Keyword, Object
import re
from pprint import pprint

client = Elasticsearch()
topics_index = Index('xfurda00_topics', using=client)
if topics_index.exists():
    print('Index already exists!')
    topics_index.delete(ignore=404, request_timeout=30)

class FundedUnder(InnerDoc):
    subprogramme = Text(fields={'keyword': Keyword()})
    programme = Text(fields={'keyword': Keyword()})

class Topic(Document):
    identifier = Text(fields={'keyword': Keyword()})
    title = Text(fields={'keyword': Keyword()})
    tags = Text()
    ccm2Id = Integer()
    callForPropos = Text(fields={'keyword': Keyword()})
    call_title = Text(fields={'keyword': Keyword()})
    description = Text()
    fundedUnder = Object(
        properties=dict(
            subprogramme=Text(fields={'keyword': Keyword()}),
            programme=Text(fields={'keyword': Keyword()})
        ),
        required=True)

topics_index.document(Topic)
topics_index.create(request_timeout=30)

class Extractor:
    def read_url(self, url):
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        print('Read URL "{0}"'.format(url))
        return data

    def parse_data(self, input):
        input_topics = input['topicData']['Topics']
        print('Found {0} topics'.format(len(input_topics)))

        for input_topic in input_topics:
            output_topic = Topic()
            output_topic.identifier = input_topic['identifier']
            output_topic.title = input_topic['title']
            output_topic.ccm2Id = int(input_topic['ccm2Id'])
            output_topic.callForPropos = input_topic['callIdentifier']
            output_topic.call_title = input_topic['callTitle']

            output_topic.fundedUnder = FundedUnder(programme=input_topic['callProgramme'], subprogramme=input_topic['mainSpecificProgrammeLevelCode'])

            if 'tags' in input_topic:
                output_topic.tags = input_topic['tags']

            url = 'http://ec.europa.eu/research/participants/portal/data/call/topics/{0}.json'.format(output_topic.identifier.lower())
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            print('Read URL "{0}"'.format(url))
            output_topic.description = data['description']

            output_topic.save()
            print('Saved topic {0}'.format(output_topic.identifier))
        print('All topics saved')




extractor = Extractor()

url = 'http://ec.europa.eu/research/participants/portal/data/call/h2020/topics.json'
data = extractor.read_url(url)
parsed = extractor.parse_data(data)