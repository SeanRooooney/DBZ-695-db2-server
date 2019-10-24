#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <memory.h>
#include <windows.h>

#include <sqludf.h>
#include <sqlstate.h>

SQL_API_RC SQL_API_FN product ( SQLUDF_DOUBLE *in1,
SQLUDF_DOUBLE *in2,
SQLUDF_DOUBLE *outProduct,
SQLUDF_NULLIND *in1NullInd,
SQLUDF_NULLIND *in2NullInd,
SQLUDF_NULLIND *productNullInd,
SQLUDF_TRAIL_ARGS )
{
*outProduct = (*in1) * (*in2) * 3;
return (0);
}


void gen_random(char *s, const int len) {
    static const char alphanum[] =
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz";

    for (int i = 0; i < len; ++i) {
        s[i] = alphanum[rand() % (sizeof(alphanum) - 1)];
    }

    s[len] = 0;
}



void SQL_API_FN asncdcservice(
    SQLUDF_VARCHAR *asnCommand, /* input */
    SQLUDF_VARCHAR *asnService,
    SQLUDF_CLOB *fileData, /* output */
    /* null indicators */
    SQLUDF_NULLIND *asnCommand_ind, /* input */
    SQLUDF_NULLIND *asnService_ind,
    SQLUDF_NULLIND *fileData_ind,
    SQLUDF_TRAIL_ARGS,
    struct sqludf_dbinfo *dbinfo)
{


    int strcheck = 0;
    char cmdstring[256];


    /// create temp file for CLOB
    char szRnd[10];
    gen_random(szRnd, 8) ;
    char szASNcdctmpFile[256];
    char* szDb2temppath  = getenv( "TEMP" );
    strcheck = sprintf(szASNcdctmpFile, "%s\\%s.txt" , szDb2temppath, szRnd);

    // create db2 bin path
    char* szDb2path = getenv( "ProgramFiles" );
    char szDb2BinPath[256];
    strcheck = sprintf(szDb2BinPath, "%s\\IBM\\SQLLIB\\BIN\\" , szDb2path);

    //  read dbname form sqludf_dbinfo *dbinfo
    char dbname[129];
    memset(dbname, '\0', 129);
    strncpy(dbname, (char *)(dbinfo->dbname), dbinfo->dbnamelen);
    dbname[dbinfo->dbnamelen] = '\0';


    int callcheck;

    if (strcmp(asnService, "asncdc") == 0)
    {

        if (strcmp(asnCommand, "start") == 0)
        {
            strcheck = sprintf(cmdstring,  "START \"\" \"%sasncap.exe\" capture_schema=%s capture_server=%s  > %s", szDb2BinPath, asnService, dbname, szASNcdctmpFile);
            callcheck = system(cmdstring);
            Sleep(3000);
        }
        if ((strcmp(asnCommand, "prune") == 0) ||
            (strcmp(asnCommand, "reinit") == 0) ||
            (strcmp(asnCommand, "suspend") == 0) ||
            (strcmp(asnCommand, "resume") == 0) ||
            (strcmp(asnCommand, "status") == 0) ||
            (strcmp(asnCommand, "stop") == 0))
        {
                strcheck = sprintf(cmdstring, "\"%sasnccmd.exe\" capture_schema=%s capture_server=%s %s > %s", szDb2BinPath, asnService, dbname, asnCommand, szASNcdctmpFile);
                callcheck = system(cmdstring);
 
        }


    }

    // read temp file for CLOB return
    FILE *f = NULL;
    f = fopen(szASNcdctmpFile, "rb");
    struct stat sFileStatus;
    int         nStatus;
    int fileSize = 0;
    size_t readCnt = 0;
    int   nReturnValue = 0; 
    memset(&sFileStatus, 0x0, sizeof(struct stat));
    nStatus = stat(szASNcdctmpFile, &sFileStatus);
    fileSize =sFileStatus.st_size;
    fileData->length = fileSize ;
    readCnt = fread(fileData->data, 1, fileSize, f);
    fclose(f);
    // delete temp file
    remove(szASNcdctmpFile);
}
