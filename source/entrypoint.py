# -*- coding:utf-8 -*-
from elasticsearch import Elasticsearch
import os

mapping = {
    "mappings": {
        "properties": {
            "ip": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "message": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "mobile": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "respond": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "time": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss"
            },
            "user": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            }
        }
    }
}
es_user = os.getenv('es_user', 'es_user')
es_passwd = os.getenv('es_passwd', 'es_passwd')
es = Elasticsearch(hosts=['es:9200'], http_auth=(es_user, es_passwd))
if not es.indices.exists('m_success_log'):
    es.indices.create('m_success_log', body=mapping)
    es.indices.create('m_error_log', body=mapping)
os.system('echo "message is running" && touch /message/success.log && tail -f /message/success.log')
