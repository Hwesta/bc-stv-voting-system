#!/usr/bin/env python
from django.core.management import setup_environ
from django.core import management
from StringIO import StringIO
import settings
setup_environ(settings)
import os, os.path
apps = []
uniqapps = {}
for idx, tl in enumerate(settings.TABLE_DUMP_ORDER):
    tl = map(lambda s: s.partition('.')[0], tl)
    for _ in tl:
		if _ not in uniqapps:
			apps.append(_) 
			uniqapps[_] = True
buf = StringIO()
management.call_command('sql', *apps, verbosity=1, indent=2, format='json', stdout=buf)
buf.seek(0)
print buf.read(), "\n"
