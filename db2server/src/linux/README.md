## Install gcc compiler on your windows system

yum install gcc


## Compile asncdc
open shell as db2instace owner 
got to the src\linux\asncdc.c directory 
```
cd .......src\linux\
```

Compile asncdc.c to asncdc.dll
bldrtn compile and copy the ddl to the sqllib/function directory
```
bldrtn asncdc
```
