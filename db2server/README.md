This is a README for the creation of a test source database for the debezium DB2 source connector. This source connector assumes that the ASN feature of DB2
is enabled at the source such that the tables to be captured are generated
in specific CDC tables. The connector then polls these tables to capture changes.

We describe here the steps involved in creating this source system

GETTING DB2
======================
DB2 is available from Docker Hub. https://hub.docker.com/r/ibmcom/db2
Each edition can be enabled via a license key and limitations are lifted by applying a different activation key as described in Change Db2 license Key.


BUILDING THE DOCKER CONTAINER
==============================

Some additional utility features are added to the image. In particular we
add some python scripts to configure the ASN tools

docker build . -t ibmcom/db2-cdc


STARTING THE DOCKER CONTAINER
==============================

The user starts the container passing the following configuration:

--name <SOME UNIQUE STRING>
--privileged=true 
-p <HOST DB2 PORT:CONTAINER DB2 PORT>
-e LICENSE=accept 
-e DB2INST1_PASSWORD=<PASSWORD TO BE USED FOR DB2INST1> 
-e DBNAME=<TEST_DATABASE_NAME> 
-v <HOST DB2 DIRECTORY LOCATION:CONTAINER DB2 DIRECTORY LOCATION>


Example:

$ docker run -itd --name db2cdclocal --privileged=true -p 50000:50000 -e LICENSE=accept -e DB2INST1_PASSWORD=xxxxxxxxxx -e DBNAME=testdb -v /Users/urb/Documents/DB2Dev/psvoldb2:/database ibmcom/db2-cdc

Additional options are availble in the base DB2 image

CONFIGURING ASN ON DB2
==============================

Connect to container
$ docker exec -it <CONTAINER ID> /bin/bash

Change to db2inst1 user
$ su db2inst1

Connect to DB2
$ db2 connect to <TEST_DATABASE_NAME>


CDC is only possible when the log property "logarchmeth1" is NOT off. There are many modes
for the transactiopn log we have been using "logretain".
In addition this require
taking a backup on the database such that there is an initial checkpoint

$ db2 update db cfg for TESTDB using logarchmeth1 logretain 
$ db2 backup db TESTDB to /dev/null
$ db2 restart db TESTDB


Run the script that sets up ASN, this creates all the control tables that ASN expects

$ db2 -tvmf /asncdctools/src/asncdctables.sql


Run the script that create some simple test tables

$ db2 -tvmf /asncdctools/src/basetable.sql 

Load some data into the test tables

$ db2 import from /asncdctools/src/data1.csv of del replace into BBANK.DONORS
$ db2 import from /asncdctools/src/data2.csv of del replace into DEMO.SIMPLE

# register tables in ASN

cd /asncdctools/src/

edit connection.json and update values for the db2 connection

python3.6 /asncdctools/src/asntable.py -a   -s BBANK -t DONORS
python3.6 /asncdctools/src/asntable.py -a   -s DEMO -t SIMPLE


If you get the following error, it might be that the you need to bind
certain functions in public mode
SRO: Don't undertstand this need to investigate


com.ibm.db2.jcc.a.SqlException: DB2 SQL error: SQLCODE: -443, SQLSTATE: 38553, SQLERRMC: SYSIBM.SQLCOLUMNS (SCI95599)

Do the following on the database:

$ cd sqllib/bnd
$ db2 connect to TESTDB
$ db2 bind db2schema.bnd blocking all grant public sqlerror continue 

We start the ASN Capture service

/opt/ibm/db2/V11.5/bin/asncap capture_schema=ASNCDC capture_server=TESTDB  logstdout=y

The capture servers populates the CDC tables, but registers the tables in inactive mode 
(i.e STATE 'I'). The state need to be changed to active 'A'.


First we stop the ASN service: stop it ( ^C )  wait until stoped. (take some seconds)
Then we change in ASNCDC.IBMSNAP_REGISTER STATE all tables to the STATE 'A'. 

We can check the state of all registered tables:

$ cd /asncdctools/src/
$ python3.6 /asncdctools/src/asntablestate.py 

and then change them:

$ update all tables with the STATE to A
$ python3.6 /asncdctools/src/asntablestate.py -a

We then need to restart asncap 

$ /opt/ibm/db2/V11.5/bin/asncap capture_schema=ASNCDC capture_server=TESTDB  logstdout=y

The DB2 debezium connector can  then be started and the tables are snapshotted.
Any changes in the ASN Capture tables will then be propated.

For example:

# insert sample
insert into DEMO.SIMPLE (USERNAME, NAME, MAIL, ID)  VALUES ('MY','MARIA','M@ALL.CH',1000);
