FROM docker.elastic.co/elasticsearch/elasticsearch:7.2.0

COPY readonlyrest-1.18.2_es7.2.0.zip /plugins/readonlyrest-1.18.2_es7.2.0.zip

COPY readonlyrest.yml /usr/share/elasticsearch/config/readonlyrest.yml

RUN sed '2 ased -i "s/message:message/$es_user:$es_passwd/g" /usr/share/elasticsearch/config/readonlyrest.yml' -i /usr/local/bin/docker-entrypoint.sh && \
    echo -e "y" | /usr/share/elasticsearch/bin/elasticsearch-plugin install file:///plugins/readonlyrest-1.18.2_es7.2.0.zip
