#! python

import subprocess

subprocess.call(["python", "manage.py", "syncdb", "--noinput"])

files=[0,1,2,3,4,5,6,7,8]

for value in files:
    subprocess.call(["python", "manage.py", "loaddata", "test_data_00"+str(value)+".json"])
