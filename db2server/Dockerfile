FROM ibmcom/db2

MAINTAINER  Peter Urbanetz

RUN yum install mlocate gcc -y

RUN yum install python-pip -y 
RUN pip install ibm_db

RUN mkdir -p /asncdctools/src

ADD src /asncdctools/src

RUN chmod -R  777  /asncdctools
