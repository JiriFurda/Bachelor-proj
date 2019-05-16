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
#----------------------- Poslední úpravy: 16.5.2019 ------------------------#
#--- Soubor: topics_extractor.py                              Verze: 1.0 ---#
#-------- http://knot.fit.vutbr.cz/wiki/index.php/rrs_eu_projects14 --------#
#--------------------- Licence: BUT Open source licence --------------------#
#---------------------------------------------------------------------------#


import urllib
import json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Text, Index, Nested, InnerDoc, Integer, Keyword, Object, Date, Search
from elasticsearch_dsl.connections import connections
import re
import sys
import getopt


# Create Elasticsearch connections
client = Elasticsearch()
connections.create_connection()


class Topic(Document):
    ''' Elasticsearch mapping for Topic document'''
    identifier = Text(fields={'keyword': Keyword()})
    title = Text(fields={'keyword': Keyword()})
    tags = Text(fields={'keyword': Keyword()})
    ccm2Id = Integer()
    subCallId = Integer()
    callForPropos = Text(fields={'keyword': Keyword()})
    call_title = Text(fields={'keyword': Keyword()})
    callStatus = Text(fields={'keyword': Keyword()})
    openingDate = Date()
    deadlineModel = Text(fields={'keyword': Keyword()})
    deadlines = Date()
    description = Text()
    description_html = Text()
    fundedUnder = Object(
        properties=dict(
            subprogramme=Text(fields={'keyword': Keyword()}),
            programme=Text(fields={'keyword': Keyword()})
        ),
        required=True)

    class Index:
        name = 'xfurda00_topics'


    @classmethod
    def findOrCreate(cls, input_topic):
        '''
        Searches for an existing document of the topics and retrieves it.
        Creates a new one if wasn't found
        '''
        # Search for existing document
        s = Search(using=client, index="xfurda00_topics") \
            .query("match", subCallId=int(input_topic['subCallId']))
        response = s.execute()

        if response.success() is True and response.hits.total > 0:
            # Return existing document if found
            meta_id = response.hits[0].meta.id
            return cls.get(id=meta_id)
        else:
            # Return new instance if haven't found
            return cls()


    def fillInfo(self, input_topic):
        ''' Fills in topic information from parsed JSON file '''
        self.identifier = input_topic['identifier']
        self.title = input_topic['title']
        self.ccm2Id = int(input_topic['ccm2Id'])
        self.subCallId = int(input_topic['subCallId'])
        self.call_title = input_topic['callTitle']
        self.callStatus = input_topic['callStatus']
        self.openingDate = input_topic['plannedOpeningDateLong']
        self.deadlineModel = input_topic['actions'][0]['deadlineModel']
        self.deadlines = input_topic['deadlineDatesLong']
        self.fundedUnder = FundedUnder(programme=input_topic['callProgramme'],
                                               subprogramme=input_topic['mainSpecificProgrammeLevelCode'])
        if 'tags' in input_topic:
            self.tags = input_topic['tags']

        self.fillDescription()


    def fillDescription(self):
        ''' Fills in topic description from a new API call '''
        # Send an API request
        url = 'http://ec.europa.eu/research/participants/portal/data/call/topics/{0}.json'.format(
            self.identifier.lower())
        print('Reading URL "{0}"'.format(url))
        response = urllib.urlopen(url)

        # Parse API result
        data = json.loads(response.read())
        self.description_html = data['description']
        self.description = re.sub('<[^>]*>', '', data['description'])


class Extractor:
    '''
    Main logic of the data extracting process
    '''
    def __init__(self, url, overwrite):
        self.url = url
        self.overwrite = overwrite
        self.run()


    def run(self):
        ''' Executes extraction '''
        # Prepare database
        if self.overwrite:
            self.reset_database()
        self.create_database()

        # Start parsing
        data = self.read_url(self.url)
        self.parse_data(data)


    def read_url(self, url):
        ''' Sends and reads API request '''
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        print('Read URL "{0}"'.format(url))
        return data


    def reset_database(self):
        ''' Removes database if it already exists '''
        topics_index = Index('xfurda00_topics', using=client)
        if topics_index.exists():
            print('Reseting index')
            topics_index.delete(ignore=404, request_timeout=30)


    def create_database(self):
        ''' Creates database if it not yet existing '''
        topics_index = Index('xfurda00_topics', using=client)
        if topics_index.exists() is False:
            print('Creating index')
            topics_index = Index('xfurda00_topics', using=client)
            topics_index.document(Topic)
            topics_index.create(request_timeout=30)


    def parse_data(self, input):
        ''' Main process of data parsing '''
        input_topics = input['topicData']['Topics']
        print('Found {0} topics'.format(len(input_topics)))

        # Iterate over the topics in JSON file
        for input_topic in input_topics:
            # Get Topic class instance
            if self.overwrite is False:
                output_topic = Topic.findOrCreate(input_topic)
            else:
                output_topic = Topic()

            # Fill topic with data and save
            output_topic.fillInfo(input_topic)
            output_topic.save()

            # Information message
            print('Saved topic {0}'.format(output_topic.identifier))

        # Parsing finished
        print('All topics saved')


def printHelp():
    ''' Prints program's usage and exits '''
    print('Usage: topics_extractor.py [-h] [-r] [-u]')
    print('Arguments:')
    print('-h, --help     Prints program\'s usage and exits')
    print('-r, --reset    Resets database and starts filling it with topics')
    print('-u, --update   Creates or updates topics in the database')
    sys.exit(1)


def loadArguments():
    ''' Loads program arguments '''
    # Try parsing arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ruh', ['reset', 'update', 'help'])
    except getopt.GetoptError:
        printHelp()
        sys.exit(1)

    # Check if arguments are present
    if len(sys.argv) == 1:
        printHelp()

    # Parse arguments
    for opt, arg in opts:
        if opt in ('-r', '--reset'):
            return True
        elif opt in ('-u', '--update'):
            return False
        elif opt in ('-h', '--help'):
            printHelp()
        else:
            printHelp()


def main():
    ''' Main function of the module, executes extracting '''
    overwrite = loadArguments()
    url = 'http://ec.europa.eu/research/participants/portal/data/call/h2020/topics.json'
    Extractor(url, overwrite)


if __name__ == "__main__":
    main()





