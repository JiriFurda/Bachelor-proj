#!/usr/bin/env python2
import urllib, json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Text, Index, Nested, InnerDoc

client = Elasticsearch()
callsIndex = Index('xfurda00_calls', using=client)
if callsIndex.exists():
    print('Index already exists!')
    callsIndex.delete(ignore=404)

class Topic(InnerDoc):
    topicIdentifier = Text()
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
        inputCalls = input['callData']['Calls']
        print('Found {0} calls'.format(len(inputCalls)))

        for inputCall in inputCalls:
            outputCall = Call()
            outputCall.callId = inputCall['CallIdentifier']['CallId']
            outputCall.programme = inputCall['FrameworkProgramme']
            outputCall.title = inputCall['Title']
            outputCall.save()
            print('Saved call {0}'.format(outputCall.callId))

        print('All calls saved')




extractor = Extractor()

url = 'http://ec.europa.eu/research/participants/portal/data/call/h2020/calls.json'
data = extractor.read_url(url)
parsed = extractor.parse_data(data)