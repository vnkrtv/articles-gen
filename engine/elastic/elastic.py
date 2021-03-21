from typing import List, Dict, Any

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError


class ElasticEngine:
    es: Elasticsearch

    def __init__(self, es: Elasticsearch):
        self.es = es

    @classmethod
    def connect(cls, host: str, port: Any, user: str, password: str):
        es = Elasticsearch(f'http://{user}:{password}@{host}:{port}/')
        if not es.ping():
            raise ConnectionError('ping failed')
        return cls(es)

    def add_index(self, name: str, number_of_shards: int = 1, number_of_replicas: int = 2):
        self.es.indices.create(index=name, body={
            "settings": {
                "index": {
                    "number_of_shards": number_of_shards,
                    "number_of_replicas": number_of_replicas,
                    "analysis": {
                        "analyzer": {
                            "t9_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": [
                                    "lowercase",
                                    "custom_edge_ngram"
                                ]
                            }
                        },
                        "filter": {
                            "custom_edge_ngram": {
                                "type": "edge_ngram",
                                "min_gram": 2,
                                "max_gram": 10
                            }
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "text": {
                        "type": "text",
                        "analyzer": "t9_analyzer",
                        "search_analyzer": "standard"
                    }
                }
            }
        })

    def add_doc(self, index_name: str, text: str):
        self.es.index(index=index_name, body={
            'text': text
        })

    def get(self, index_name: str, phrase: str, count: int = 10) -> List[str]:
        sentences = [
            doc['_source']['text']
            for doc in self.es.search(
                index=index_name,
                body={
                    "query": {
                        "match_phrase": {
                            "text": phrase
                        }
                    },
                    "size": count
                })['hits']['hits']
        ]
        return [
            sentence[sentence.find(phrase):]
            for sentence in sentences
        ]
