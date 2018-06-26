import sys
from cx_Freeze import setup, Executable

#This is the script used to generate the .exe file for the YSDI project (AmI 2018) 


setup(  name = "Userclient", #This is the name of our main python script file 
        version = "0.1", #We actually did a lot of version
        description = "YSDI 2018 executable file",
        #options = {"build_exe": build_exe_options},
        executables = [Executable("Userclient.py")])