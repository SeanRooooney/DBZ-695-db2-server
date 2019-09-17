https://hub.docker.com/r/ibmcom/db2


docker build . -t ibmcom/db2-cdc

docker run -itd --name db2cdclocal --privileged=true -p 50000:50000 -e LICENSE=accept -e DB2INST1_PASSWORD=pass29Aug -e DBNAME=testdb -v /Users/urb/Documents/DB2Dev/psvoldb2:/database ibmcom/db2-cdc



db2 connect to testdb
db2 -tvmf asncdctables.sql
db2 -tvmf basetable.sql 

db2 import from data1.csv of del replace into BBANK.DONORS
db2 import from data2.csv of del replace into DEMO.SIMPLE


insert into DEMO.SIMPLE (USERNAME, NAME, MAIL, ID)  VALUES ('MY','MARIA','M@ALL.CH',1000);