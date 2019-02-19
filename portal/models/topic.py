from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

client = Elasticsearch()


class Topic:
    def __init__(self, topic_id):
        self.id = topic_id

    def projects_query(self):
        projects_search = Search(using=client,
                                 index="xstane34_projects")
        projects_search = projects_search.query("match", callForPropos=self.id)
        return projects_search

    def projects(self):
        projects_response = self.projects_query().execute()
        return projects_response