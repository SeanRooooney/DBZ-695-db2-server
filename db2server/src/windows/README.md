## Install windows C compiler on your windows system

https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019


## Compile asncdc
Open Db2 Command Windows - Administrator
got to the src\windows\asncdc.c directory 
```
cd .......src\windows\
```
Setup Cl copmiler environment
```
"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
```
Compile asncdc.c to asncdc.dll
bldrtn.bat compile and copy the ddl to the SQLLIB/FUNCTION directory
```
bldrtn.bat asncdc
```
