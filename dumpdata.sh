#!/bin/bash
i=0
dumpcmd='python manage.py dumpdata --format=json --indent=2'
egrep -v '^#|^$' models-deptree.txt | while read line ; do 
	$dumpcmd $line >test_data_`printf %03d $i`.json
	i=$(( $i + 1 ))
done
# loaddata will complain about files that are just "[]"
# So we remove them
find -name 'test_data_*.json' -size -10c -exec rm -f \{} \;
