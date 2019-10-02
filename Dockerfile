FROM ibmcom/db2

MAINTAINER  Peter Urbanetz

RUN yum install mlocate gcc -y
RUN yum install  yum install python36 -y
RUN yum install  yum install python36-devel -y

RUN python3.6 -m pip install --upgrade pip 
RUN python3.6 -m pip install ibm_db
RUN python3.6 -m pip install requests

RUN mkdir -p /asncdctools/src

ADD src /asncdctools/src

RUN chmod -R  666  /asncdctools
