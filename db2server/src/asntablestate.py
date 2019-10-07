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
    print("db2 connected ...")



def cdctable(cdcdo):
    if cdcdo == 'archive' :
        print('set tables to archive')
        sql = "UPDATE " + ASN_SCHEMA + ".IBMSNAP_REGISTER SET STATE = 'A' WHERE SOURCE_OWNER  <> '' "
        stmt = ibm_db.exec_immediate(conn, sql)
    else:
        sql = "SELECT SOURCE_OWNER,SOURCE_TABLE, STATE FROM " + ASN_SCHEMA + ".IBMSNAP_REGISTER WHERE SOURCE_OWNER  <> '' "
        stmt = ibm_db.exec_immediate(conn, sql)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False: 
            print(dictionary["SOURCE_OWNER"] + "." + dictionary["SOURCE_TABLE"] + "  " + dictionary["STATE"])
            dictionary = ibm_db.fetch_both(stmt)






def main(argv):
    cdc_schema = ''
    cdc_table = ''
    cdc_tabledo = ''
    if (('-a' in argv) or (len(sys.argv) == 1)):
        if ('-a' in argv):
            cdc_tabledo = 'archive'


        cdctable(cdc_tabledo)
    else:
        print('add a Table:')
        print ('asntable.py -a -s <SCHEMA> -t <TABLE>')
        print()
        print('remove a Table:')
        print ('asntable.py -r -s <SCHEMA> -t <TABLE>')





if __name__ == "__main__":
    main(sys.argv[1:])



    


