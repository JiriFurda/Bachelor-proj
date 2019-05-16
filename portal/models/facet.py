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
#--- Soubor: facet.py                                         Verze: 1.0 ---#
#-------- http://knot.fit.vutbr.cz/wiki/index.php/rrs_eu_projects14 --------#
#--------------------- Licence: BUT Open source licence --------------------#
#---------------------------------------------------------------------------#


class Facet:
    def __init__(self, name, title, field):
        self.name = name
        self.title = title
        self.field = field
        self.field_no_keyword = field.replace('.keyword', '')


    @staticmethod
    def all():
        ''' Returns all available Facet instances '''
        facets_list = [
                #Facet('index', 'Index', '_index'),
                Facet('programme', 'Programme', 'fundedUnder.programme.keyword'),
                Facet('subprogramme', 'Subprogramme', 'fundedUnder.subprogramme.keyword'),
                Facet('call', 'Call for Proposal', 'callForPropos.keyword'),
                Facet('topic', 'Topic', 'topics.code.keyword'),
                Facet('funding', 'Funding scheme', 'fundingScheme.code.keyword'),
                Facet('coordinator', 'Coordinator', 'coordinator.name.keyword'),
                Facet('coordcountry', 'Coord. Country', 'coordinator.country.keyword'),
                Facet('participant', 'Participant', 'participant.name.keyword'),
                Facet('partcountry', 'Part. Country', 'participant.country.keyword'),
                Facet('year', 'Beginning year', 'year'),
                Facet('tag', 'Tag', 'tags.keyword'),
                Facet('callStatus', 'Status', 'callStatus.keyword'),
                Facet('deadlineModel', 'Deadline Model', 'deadlineModel.keyword'),
            ]
        return facets_list

    @classmethod
    def get(cls, searched_name):
        ''' Retrieves one specific Facet instance '''
        for facet in cls.all():
            if facet.name == searched_name:
                return facet

        return None


    def toDict(self):
        ''' Converts Facet to dict '''
        dict = {
            'name': self.name,
            'title': self.title,
            'field': self.field,
        }

        return dict


    def underscoreField(self):
        ''' Convert nested facet filed names for usage as function argument '''
        return self.field.replace('.', '__')
