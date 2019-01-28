#!/usr/bin/env python2
import urllib, json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Text, Index, Nested, InnerDoc
import re
from pprint import pprint


client = Elasticsearch()
callsIndex = Index('xfurda00_calls', using=client)
if callsIndex.exists():
    print('Index already exists!')
    callsIndex.delete(ignore=404)

class Topic(InnerDoc):
    topic_identifier = Text()
    title = Text()
    tags = Text()

class Call(Document):
    callId = Text()
    programme = Text()
    title = Text()
    topics = Nested(Topic)

callsIndex.document(Call)
callsIndex.create()

class Extractor:
    def read_url(self, url):
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        print('Read URL "{0}"'.format(url))
        return data

    def parse_data(self, input):
        input_calls = input['callData']['Calls']
        print('Found {0} calls'.format(len(input_calls)))

        for input_call in input_calls:
            output_call = Call()
            output_call.callId = input_call['CallIdentifier']['CallId']
            output_call.programme = input_call['FrameworkProgramme']
            output_call.title = input_call['Title']

            input_call_budgets = input_call['CallBudgetOverview'][0].values()
            for input_call_budget in input_call_budgets:
                for input_topic in input_call_budget['Topic']:

                    match = re.match(r'^(.+) - (.+)$', input_topic)

                    if not match or len(match.groups()) != 2:
                        print('Invalid topic title! {0}'.format(input_topic))
                        continue

                    output_topic = Topic()
                    output_topic.topic_identifier = match.group(1)
                    output_topic.title = match.group(2)
                    output_call.topics.append(output_topic)

            output_call.save()
            print('Saved call {0}'.format(output_call.callId))
        print('All calls saved')




extractor = Extractor()

url = 'http://ec.europa.eu/research/participants/portal/data/call/h2020/calls.json'
data = extractor.read_url(url)
parsed = extractor.parse_data(data)