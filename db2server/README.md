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

db2-cdc image 
=============

ASN CDC via SQL

## asn capture 
```
VALUES ASNCDC.ASNCDCSERVICES('start','asncdc');
VALUES ASNCDC.ASNCDCSERVICES('status','asncdc');
VALUES ASNCDC.ASNCDCSERVICES('stop','asncdc');
```
If you add new CDC table
```
VALUES ASNCDC.ASNCDCSERVICES('reinit','asncdc');
```

If you need suspend the capture for havy load on db, you could suspend and resume it
```
VALUES ASNCDC.ASNCDCSERVICES('suspend','asncdc');
VALUES ASNCDC.ASNCDCSERVICES('resume','asncdc');
```

## ADD REMOVE a table form capture service

```
CALL ASNCDC.ADDTABLE('BBANK', 'DONORS' ); 
CALL ASNCDC.REMOVETABLE('BBANK', 'DONORS' );
```

### check STATUS of CDC registered table 
STATE: 
I --> inactiv  
A --> active

get all registered tables
```
SELECT SOURCE_OWNER,SOURCE_TABLE, STATE FROM ASNCDC.IBMSNAP_REGISTER WHERE SOURCE_OWNER  <> '' ;
```

update all table to active
```
UPDATE ASNCDC.IBMSNAP_REGISTER SET STATE = 'A' WHERE SOURCE_OWNER  <> '';
``` 
## CDC test tables
it include two table with data for testing:

BBANK.DONORS
DEMO.SIMPLE




### insert sample
insert into DEMO.SIMPLE (USERNAME, NAME, MAIL, ID)  VALUES ('MY','MARIA','M@ALL.CH',1000);


