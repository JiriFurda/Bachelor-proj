

class Facet:
    def __init__(self, name, title, field):
        self.name = name
        self.title = title
        self.field = field

    @staticmethod
    def all():
        facets_list = [
                Facet('programme', 'Programme', 'fundedUnder.programme.keyword'),
                Facet('subprogramme', 'Subprogramme', 'fundedUnder.subprogramme.keyword'),
                Facet('topic', 'Topic', 'topics.title.keyword'),
                Facet('funding', 'Funding scheme', 'fundingScheme.code.keyword'),
                Facet('coordinator', 'Coordinator', 'coordinator.name.keyword'),
                Facet('coordcountry', 'Coord. Country', 'coordinator.country.keyword'),
                Facet('year', 'Year', 'year')
            ]
        return facets_list

    @classmethod
    def get(cls, searched_name):
        for facet in cls.all():
            if facet.name == searched_name:
                return facet
        return None