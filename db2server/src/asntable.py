#!/usr/bin/python

import ibm_db
import time
import sys
import json


import sys
import getopt



with open('connection.json') as f:
    connections = json.load(f)

print(connections['db2']['host'])    

ASN_SCHEMA = connections['db2']['asnschema']

connectionStr = ''
security = ''
if (connections['db2']['host'].lower() == 'y'):
    security = ';SECURITY=SSL;SSLClientKeystoredb=/opt/ibm/db2/GSK8Store/keyclient.kdb;SSLClientKeystash=/opt/ibm/db2/GSK8Store/keyclient.sth; '
connectionStr = "DATABASE=" + connections['db2']['database']
connectionStr = connectionStr + ";HOSTNAME=" + connections['db2']['host']
connectionStr = connectionStr + ";PORT=" + connections['db2']['port']
connectionStr = connectionStr + ";PROTOCOL=TCPIP;UID=" + connections['db2']['user']
connectionStr = connectionStr + ";PWD=" + connections['db2']['pwd']
connectionStr = connectionStr + security
try:
    conn = ibm_db.connect(connectionStr, "", "")
except:

    print(ibm_db.conn_errormsg())
else:
    print("db2 connected")



def cdctable(cdcdo, cdcschema, cdctable):
    if cdcdo == 'add' :
        sql = ''
        #stmt = ibm_db.exec_immediate(sourceconn, sql)
        cd_Table = cdcschema + "_" + cdctable
    
        sql = "CREATE TABLE " + ASN_SCHEMA + ".CDC_" + cd_Table + " AS ( SELECT CAST('' AS VARCHAR ( 16 )  FOR BIT DATA) AS  IBMSNAP_COMMITSEQ,  CAST('' AS VARCHAR ( 16 )  FOR BIT DATA) AS  IBMSNAP_INTENTSEQ, CAST ('' AS CHAR(1)) AS IBMSNAP_OPERATION,  t.* FROM " + cdcschema + "." + cdctable + " as t)  WITH NO  DATA ORGANIZE BY ROW"
        stmt = ibm_db.exec_immediate(conn, sql)
        sql = "ALTER TABLE " + ASN_SCHEMA + ".CDC_" + cd_Table + " ALTER COLUMN IBMSNAP_COMMITSEQ SET NOT NULL"
        stmt = ibm_db.exec_immediate(conn, sql)
        sql = "ALTER TABLE " + ASN_SCHEMA + ".CDC_" + cd_Table + " ALTER COLUMN IBMSNAP_INTENTSEQ SET NOT NULL"
        stmt = ibm_db.exec_immediate(conn, sql)
        sql = "ALTER TABLE " + ASN_SCHEMA + ".CDC_" + cd_Table + " ALTER COLUMN IBMSNAP_OPERATION SET NOT NULL"
        stmt = ibm_db.exec_immediate(conn, sql)
        sql = "CREATE  UNIQUE  INDEX " + ASN_SCHEMA + ".IXCDC_" + cd_Table + " ON " + ASN_SCHEMA + ".CDC_" + cd_Table + "( IBMSNAP_COMMITSEQ ASC, IBMSNAP_INTENTSEQ ASC ) PCTFREE 0 MINPCTUSED 0"
        stmt = ibm_db.exec_immediate(conn, sql)
        sql = "ALTER TABLE  " + ASN_SCHEMA + ".CDC_" + cd_Table + "  VOLATILE CARDINALITY"
        stmt = ibm_db.exec_immediate(conn, sql)
        #register DC Table
        sql =   "INSERT INTO " + ASN_SCHEMA + ".IBMSNAP_REGISTER (SOURCE_OWNER, SOURCE_TABLE, " \
                "SOURCE_VIEW_QUAL, GLOBAL_RECORD, SOURCE_STRUCTURE, SOURCE_CONDENSED, "\
                "SOURCE_COMPLETE, CD_OWNER, CD_TABLE, PHYS_CHANGE_OWNER,  "\
                "PHYS_CHANGE_TABLE, CD_OLD_SYNCHPOINT, CD_NEW_SYNCHPOINT,  "\
                "DISABLE_REFRESH, CCD_OWNER, CCD_TABLE, CCD_OLD_SYNCHPOINT,  "\
                "SYNCHPOINT, SYNCHTIME, CCD_CONDENSED, CCD_COMPLETE, ARCH_LEVEL,  "\
                "DESCRIPTION, BEFORE_IMG_PREFIX, CONFLICT_LEVEL,  "\
                "CHG_UPD_TO_DEL_INS, CHGONLY, RECAPTURE, OPTION_FLAGS, "\
                "STOP_ON_ERROR, STATE, STATE_INFO ) VALUES( "\
                "'" + cdcschema + "', "\
                "'" + cdctable + "', "\
                "0, "\
                "'N', "\
                "1, "\
                "'Y', "\
                "'Y', "\
                "'" + ASN_SCHEMA + "', "\
                "'CDC_" + cd_Table + "', "\
                "'" + ASN_SCHEMA + "', "\
                "'CDC_" + cd_Table + "', "\
                "null, "\
                "null, "\
                "0, "\
                "null, "\
                "null, "\
                "null, "\
                "null, "\
                "null, "\
                "null, "\
                "null, "\
                "'0801', "\
                "null, "\
                "null, "\
                "'0', "\
                "'Y', "\
                "'N', "\
                "'Y', "\
                "'NNNN', "\
                "'Y', "\
                "'A',"\
                "null ) "
        stmt = ibm_db.exec_immediate(conn, sql)

   
        sql =   "INSERT INTO " + ASN_SCHEMA + ".IBMSNAP_PRUNCNTL ( " \
                "TARGET_SERVER,  " \
                "TARGET_OWNER,  " \
                "TARGET_TABLE,  " \
                "SYNCHTIME,  " \
                "SYNCHPOINT,  " \
                "SOURCE_OWNER,  " \
                "SOURCE_TABLE,  " \
                "SOURCE_VIEW_QUAL,  " \
                "APPLY_QUAL,  " \
                "SET_NAME,  " \
                "CNTL_SERVER ,  " \
                "TARGET_STRUCTURE ,  " \
                "CNTL_ALIAS ,  " \
                "PHYS_CHANGE_OWNER ,  " \
                "PHYS_CHANGE_TABLE ,  " \
                "MAP_ID  " \
                ") VALUES ( " \
                "'" + 'KAFKA' + "', " \
                "'" + cdcschema + "', " \
                "'" + cdctable + "', " \
                "NULL, " \
                "NULL, " \
                "'" + cdcschema + "', " \
                "'" + cdctable + "', " \
                "0, " \
                "'" + "KAFKAQUAL" + "', " \
                "'" + "SET001" + "', " \
                "'" + connections['db2']['database'].upper() + "', " \
                "8, " \
                "'" + connections['db2']['database'].upper() + "', " \
                "'" + ASN_SCHEMA + "', " \
                "'CDC_" + cd_Table + "', " \
                " ( SELECT CASE WHEN max(CAST(MAP_ID AS INT)) IS NULL THEN CAST(1 AS VARCHAR(10)) ELSE CAST(CAST(max(MAP_ID) AS INT) + 1 AS VARCHAR(10))  END AS MYINT from  " + ASN_SCHEMA + ".IBMSNAP_PRUNCNTL ) " \
                "    )"
        stmt = ibm_db.exec_immediate(conn, sql)
        sql =  " "


        # alter primary key
        sql =   "select constname, tabschema,tabname from SYSCAT.TABCONST "\
                "where  tabschema='" + cdcschema + "' " \
                "and TABNAME='" + cdctable + "' and TYPE='P'"
        stmt = ibm_db.exec_immediate(conn, sql)
        dictionary = ibm_db.fetch_both(stmt)
        pks = ''
        while dictionary != False:      #PK exist
            constrainname = dictionary["CONSTNAME"]
           
            sql =   "SELECT NAME " \
                    "FROM SYSIBM.SYSCOLUMNS SC " \
                    "WHERE SC.TBNAME = '" + cdctable + "' " \
                    "AND sc.identity	='N' " \
                    "AND sc.tbcreator='" + cdcschema + "' " \
                    "AND sc.keyseq IS NOT NULL ORDER BY sc.keyseq"
            stmt2 = ibm_db.exec_immediate(conn, sql)
            dictionary2 = ibm_db.fetch_both(stmt2)
            while dictionary2 != False:
                pks = pks + dictionary2["NAME"] + ','
                dictionary2 = ibm_db.fetch_both(stmt2)
            pks = pks[:-1]
            #sql =   "ALTER TABLE " + cdcschema + "." + cdctable + " " \
            #        "ADD CONSTRAINT " + cdcschema + "_" + cdctable + "_PK " \
            #        "PRIMARY KEY (" + pks + ")"
            #stmt2 = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_both(stmt)
    
                
        sql =   "SELECT * from SYSCAT.COLUMNS WHERE TABSCHEMA='" + cdcschema + "' " \
                "AND TABNAME = '" + cdctable + "' ORDER BY COLNO "
        stmt = ibm_db.exec_immediate(conn, sql)
        dictionary = ibm_db.fetch_both(stmt)
        pksarray = pks.split(",")
        while dictionary != False: 
            colname = dictionary["COLNAME"]
            if colname in pksarray:
                key = 'Y'
            else:
                key = 'N'
            sql =   "INSERT INTO  " + ASN_SCHEMA + ".IBMSNAP_SUBS_COLS (APPLY_QUAL, SET_NAME, WHOS_ON_FIRST, TARGET_OWNER, TARGET_TABLE, " \
                    "COL_TYPE, TARGET_NAME, IS_KEY, COLNO, EXPRESSION) VALUES (" \
                    "'" + "KAFKAQUAL" + "', '" +  "SET001" + "', 'S', " \
                    "'" + cdcschema  + "', " \
                    "'" + cdctable  + "', 'A', " \
                    "'" + colname + "', '" + key + "'," + str(dictionary["COLNO"]+1) + ", '" + colname + "')"
            stmtinsert = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_both(stmt)
    
    
    
    
                
        sql =   "INSERT INTO  " + ASN_SCHEMA + ".IBMSNAP_SUBS_MEMBR (APPLY_QUAL, SET_NAME, WHOS_ON_FIRST, SOURCE_OWNER, SOURCE_TABLE, "\
                "  SOURCE_VIEW_QUAL, TARGET_OWNER, TARGET_TABLE, TARGET_CONDENSED, "\
                "  TARGET_COMPLETE, TARGET_STRUCTURE, PREDICATES, MEMBER_STATE, "\
                "  TARGET_KEY_CHG, UOW_CD_PREDICATES, JOIN_UOW_CD, LOADX_TYPE, "\
                "  LOADX_SRC_N_OWNER, LOADX_SRC_N_TABLE "\
                ") VALUES ( "\
                "'" + "KAFKAQUAL" + "', "\
                "'" + "SET001" + "', "\
                "'S', "\
                "'" + cdcschema  + "', "\
                "'" + cdctable + "', "\
                "0, "\
                "'" + cdcschema + "', "\
                "'" + cdctable + "', "\
                "'Y', "\
                "'Y', "\
                "8, "\
                "NULL, "\
                "'L', "\
                "'N', "\
                "NULL, "\
                "NULL, "\
                "3,	"\
                "'" + ASN_SCHEMA + "', " \
                "'CDC_" + cd_Table +  \
                "')"

        stmt = ibm_db.exec_immediate(conn, sql)
                





    if cdcdo == 'remove':
        #delete all entry
        #check ASN.IBMSNAP_PRUNCTL / source
        sql = "SELECT * FROM " + ASN_SCHEMA + ".IBMSNAP_PRUNCNTL WHERE SOURCE_OWNER='" + cdcschema + "' AND SOURCE_TABLE='" + cdctable + "'"
        stmt = ibm_db.exec_immediate(conn, sql)
        try: 
            deleteSet = ibm_db.fetch_both(stmt)   # it is only one entry 
        except:
            pass


        # delete ASN.IBMSNAP_PRUNCTL entries / source
        sql = "DELETE FROM " + ASN_SCHEMA + ".IBMSNAP_PRUNCNTL WHERE SOURCE_OWNER='" + cdcschema + "' AND SOURCE_TABLE='" + cdctable + "'"
        stmt = ibm_db.exec_immediate(conn, sql)
        # delete ASN.IBMSNAP_Register entries / source
        sql = "DELETE FROM " + ASN_SCHEMA + ".IBMSNAP_REGISTER WHERE SOURCE_OWNER='" + cdcschema + "' AND SOURCE_TABLE='" + cdctable + "'"
        try:
            stmt = ibm_db.exec_immediate(conn, sql)                           
        except:
            pass
        #drop CD Table / source
        sql = "DROP TABLE " + ASN_SCHEMA + "." + deleteSet["PHYS_CHANGE_TABLE"]
        try:
            stmt = ibm_db.exec_immediate(conn, sql) 
        except:
            pass

        # delete ASN.IBMSNAP_SUBS_COLS entries /target
        sql = "DELETE FROM " + ASN_SCHEMA + ".IBMSNAP_SUBS_COLS WHERE TARGET_OWNER='" + deleteSet["TARGET_OWNER"] + "' AND TARGET_TABLE='" + deleteSet["TARGET_TABLE"] + "'"
        try:
            stmt = ibm_db.exec_immediate(conn, sql) 
        except:
            pass
        # delete ASN.IBMSNAP_SUSBS_MEMBER entries /target
        sql = "DELETE FROM " + ASN_SCHEMA + ".IBMSNAP_SUBS_MEMBR WHERE TARGET_OWNER='" + deleteSet["TARGET_OWNER"] + "' AND TARGET_TABLE='" + deleteSet["TARGET_TABLE"] + "'"
        try:
            stmt = ibm_db.exec_immediate(conn, sql) 
        except:
            pass




def main(argv):
    cdc_schema = ''
    cdc_table = ''
    cdc_tabledo = ''
    if (('-a' in argv)or ('-r' in argv)) and ('-t' in argv) and ('-s' in argv):
        if ('-a' in argv):
            cdc_tabledo = 'add'
        if ('-r' in argv):
            cdc_tabledo = 'remove'
        cdc_schema =(argv[argv.index('-s') + 1 ])
        cdc_table =(argv[argv.index('-t') + 1 ])

        cdctable(cdc_tabledo, cdc_schema, cdc_table )
    else:
        print('add a Table:')
        print ('asntable.py -a -s <SCHEMA> -t <TABLE>')
        print()
        print('remove a Table:')
        print ('asntable.py -r -s <SCHEMA> -t <TABLE>')


    print (cdc_tabledo + ' ' + cdc_schema + '.' + cdc_table )


if __name__ == "__main__":
    main(sys.argv[1:])



    


