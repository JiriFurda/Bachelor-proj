import json

class Facet:
    def __init__(self, name, title, field):
        self.name = name
        self.title = title
        self.field = field
        self.field_no_keyword = field.replace('.keyword', '')


    @staticmethod
    def all():
        facets_list = [
                Facet('index', 'Index', '_index'),
                Facet('programme', 'Programme', 'fundedUnder.programme.keyword'),
                Facet('subprogramme', 'Subprogramme', 'fundedUnder.subprogramme.keyword'),
                Facet('call', 'Call for Proposal', 'callForPropos.keyword'),
                Facet('topic', 'Topic', 'topics.code.keyword'),
                Facet('funding', 'Funding scheme', 'fundingScheme.code.keyword'),
                Facet('coordinator', 'Coordinator', 'coordinator.name.keyword'),
                Facet('coordcountry', 'Coord. Country', 'coordinator.country.keyword'),
                Facet('participant', 'Participant', 'participant.name.keyword'),
                Facet('partcountry', 'Part. Country', 'participant.country.keyword'),
                Facet('year', 'Year', 'year'),
                Facet('tag', 'Tag', 'tags.keyword'),
            ]
        return facets_list


    @staticmethod
    def getByName(name):
        facets = Facet.all()

        for facet in facets:
            if facet.name == name:
                return facet

        return None


    @classmethod
    def get(cls, searched_name):
        for facet in cls.all():
            if facet.name == searched_name:
                return facet
        return None


    def toDict(self):
        dict = {
            'name': self.name,
            'title': self.title,
            'field': self.field,
        }

        return dict


    def underscoreField(self):
        return self.field.replace('.', '__')
