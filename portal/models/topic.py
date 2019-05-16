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
#----------------------- Poslední úpravy: 13.5.2019 ------------------------#
#--- Soubor: topic.py                                         Verze: 1.0 ---#
#-------- http://knot.fit.vutbr.cz/wiki/index.php/rrs_eu_projects14 --------#
#--------------------- Licence: BUT Open source licence --------------------#
#---------------------------------------------------------------------------#


from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MoreLikeThis
import arrow


client = Elasticsearch()


class Topic:
    ''' Class used for easier working with topic document '''
    def __init__(self, body):
        self.body = body


    def projects_query(self):
        ''' Creates Elasticsearch query to get projects with this topic '''
        projects_search = Search(using=client,
                                 index="xstane34_projects")
        projects_search = projects_search.query('match', topics__code__keyword=self.body.identifier)

        return projects_search


    def projects(self):
        ''' Executes Elasticsearch query to get projects with this topic '''
        projects_response = self.projects_query().execute()
        return projects_response


    @classmethod
    def castFromResponse(cls, response):
        ''' Creates instance of this class from Elasticsearh results '''
        result = []
        for hit in response.hits:
            result.append(Topic(hit))
        return result


    def statusSummary(self):
        ''' Generates topic status summary '''
        result = self.body.callStatus

        if self.body.callStatus != 'Closed':
            result += ' - Deadline '

        diff_for_humans = arrow.get(self.closestDeadline()).humanize()
        result += ' '+diff_for_humans

        return result

    def closestDeadline(self):
        ''' Returns closest deadline of the topic '''
        rawDeadlines = self.body.deadlines
        rawDeadlines.sort()

        now = arrow.utcnow()
        for rawDeadline in rawDeadlines:
            parsedDeadline = arrow.get(rawDeadline)
            if now < parsedDeadline:
                return rawDeadline

        return rawDeadlines[-1]

    def similar(self, count):
        ''' Search for similar topics '''
        similar_search = Search(using=client,
                                index="xfurda00_topics")
        similar_search = similar_search.query(MoreLikeThis(like={
            '_id': self.body.meta.id,
            '_index': 'xfurda00_topics',
            'fields': ['tags', 'title^3'],
        }))

        similar_response = similar_search.execute()
        return similar_response[:count]
