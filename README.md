https://hub.docker.com/r/ibmcom/db2


docker build . -t ibmcom/db2-cdc

docker run -itd --name db2cdclocal --privileged=true -p 50000:50000 -e LICENSE=accept -e DB2INST1_PASSWORD=xxxxxxxxxx -e DBNAME=testdb -v /Users/urb/Documents/DB2Dev/psvoldb2:/database ibmcom/db2-cdc



db2 connect to testdb
db2 -tvmf /asncdctools/src/asncdctables.sql
db2 -tvmf /asncdctools/src/basetable.sql 

db2 import from /asncdctools/src/data1.csv of del replace into BBANK.DONORS
db2 import from /asncdctools/src/data2.csv of del replace into DEMO.SIMPLE

# register tables in ASN

python3.6 /asncdctools/src/asntable.py -a   -s BBANK -t DONORS
python3.6 /asncdctools/src/asntable.py -a   -s DEMO -t SIMPLE

db2 update db cfg for TESTDB using logarchmeth1 logretain 
db2 backup db TESTDB to /dev/null
db2 restart db TESTDB


/opt/ibm/db2/V11.5/bin/asncap capture_schema=ASNCDC capture_server=TESTDB  logstdout=y

# stop it ( ^C )  wait until stoped. (take some seconds)

Change in ASNCDC.IBMSNAP_REGISTER STATE for all tables the STATE to 'A' 

# start asncap again 

/opt/ibm/db2/V11.5/bin/asncap capture_schema=ASNCDC capture_server=TESTDB  logstdout=y

# insert sample
insert into DEMO.SIMPLE (USERNAME, NAME, MAIL, ID)  VALUES ('MY','MARIA','M@ALL.CH',1000);
