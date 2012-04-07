#! python

import subprocess

PYTHON_COMMAND="python"

subprocess.call([PYTHON_COMMAND, "manage.py", "syncdb", "--noinput"])

files=[0,1,2,3,4,5,6,7,8,9,10]

for value in files:
    jsonfile="test_data_%03d.json" % (value)
    print "Loading",jsonfile
    subprocess.call([PYTHON_COMMAND, "manage.py", "loaddata", jsonfile])
