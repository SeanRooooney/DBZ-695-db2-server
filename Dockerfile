FROM ibmcom/db2

MAINTAINER  Peter Urbanetz

ARG ARTIFACTORY_USER
ARG ARTIFACTORY_PASSWORD

ADD asncdc.service /etc/systemd/system

RUN yum install librdkafka  librdkafka-devel mlocate gcc -y

RUN yum install https://centos7.iuscommunity.org/ius-release.rpm -y
RUN yum install python36u python36u-devel python36u-pip -y

RUN python3.6 -m pip install --upgrade pip 
RUN python3.6 -m pip install ibm_db

#MSSQL
#RUN python3.6 -m pip install pyodbc

RUN python3.6 -m pip install requests
#RUN python3.6 -m pip install avro-python3
#avro bug since version 1.9 https://github.com/confluentinc/confluent-kafka-python/issues/610
RUN python3.6 -m pip install avro-python3==1.8.2
RUN python3.6 -m pip install confluent_kafka

RUN mkdir -p /asncdctools/src

ADD src /asncdctools/src

RUN chown -R  db2inst1.db2iadm1  /asncdctools
