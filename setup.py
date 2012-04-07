#! python

import subprocess

PYTHON_COMMAND="python"

subprocess.call([PYTHON_COMMAND, "manage.py", "syncdb", "--noinput"])

files=['00','01','02','03','04','05','06','07','08','09','10']

for value in files:
    jsonfile="test_data_0"+value+".json"
    print "Loading",jsonfile
    subprocess.call([PYTHON_COMMAND, "manage.py", "loaddata", jsonfile])
