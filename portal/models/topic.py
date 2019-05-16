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
import arrow


client = Elasticsearch()


class Topic:
    def __init__(self, body):
        self.body = body

    def projects_query(self):
        projects_search = Search(using=client,
                                 index="xstane34_projects")
        projects_search = projects_search.query('match', topics__code__keyword=self.body.identifier)

        return projects_search


    def projects(self):
        projects_response = self.projects_query().execute()
        return projects_response

    @classmethod
    def castFromResponse(cls, response):
        result = []
        for hit in response.hits:
            result.append(Topic(hit))
        return result

    def statusSummary(self):
        result = self.body.callStatus

        if self.body.callStatus != 'Closed':
            result += ' - Deadline '

        diff_for_humans = arrow.get(self.closestDeadline()).humanize()
        result += ' '+diff_for_humans

        return result

    def closestDeadline(self):
        rawDeadlines = self.body.deadlines
        rawDeadlines.sort()

        now = arrow.utcnow()
        for rawDeadline in rawDeadlines:
            parsedDeadline = arrow.get(rawDeadline)
            if now < parsedDeadline:
                return rawDeadline

        return rawDeadlines[-1]