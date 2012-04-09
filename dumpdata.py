#!/usr/bin/env python
from django.core.management import setup_environ
from django.core import management
from StringIO import StringIO
import settings
setup_environ(settings)
import os, os.path
for idx, tl in enumerate(settings.TABLE_DUMP_ORDER):
    output_file = "test_data_%03d.json" % (idx, )
    buf = StringIO()
    management.call_command('dumpdata', *tl, verbosity=1, indent=2, format='json', stdout=buf)
    if buf.pos > 4:
        buf.write("\n")
        f = open(output_file, 'w')
        buf.seek(0)
        f.write(buf.read())
        f.close()
    elif os.path.exists(output_file):
        os.unlink(output_file)
