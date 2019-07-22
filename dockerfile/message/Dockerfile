FROM python:3.7-slim as message_base
COPY source/requirements.txt /requirements.txt
RUN apt-get update && \
    apt-get install gcc -y && \
    pip install -r /requirements.txt && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

FROM message_base
add source /message
WORKDIR /message
ENTRYPOINT ["python3","entrypoint.py"]
