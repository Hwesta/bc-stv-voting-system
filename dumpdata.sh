#!/bin/bash
i=0
grep -v '^#' models-deptree.txt | while read line ; do 
	python manage.py dumpdata $line >test_data_`printf %03d $i`.json
	i=$(( $i + 1 ))
done
# loaddata will complain about files that are just "[]"
# So we remove them
find -name 'test_data_*.json' -size -10c -exec rm -f \{} \;
