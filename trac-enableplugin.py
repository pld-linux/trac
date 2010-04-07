#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Enable components specified in commandline in all trac instances unless it is
# already configured.
#
# Author: Elan Ruusamäe <glen@delfi.ee>
# Date: 2010-04-07

import sys
from glob import glob
from trac.env import open_environment

components = sys.argv[1:]
for file in glob('/var/lib/trac/*/conf/trac.ini'):
    # strip conf/trac.ini from path
    project = file[:-14]

    env = open_environment(project)

    # trac/admin/web_ui.py
    changes = False
    for component in components:
        is_present = env.config.has_option('components', component.lower())
        if not is_present:
            env.config.set('components', component, 'enabled')
            print 'Enabling component %s in %s' % (component, project)
            changes = True

    if changes:
        env.config.save()
