#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Upgrade all Trac instances
#
# Author: Elan Ruusamäe <glen@delfi.ee>
# Date: 2010-09-13

import sys
from glob import glob
from trac.env import open_environment
from trac.core import TracError

for file in glob('/var/lib/trac/*/conf/trac.ini'):
	# strip conf/trac.ini from path
	project = file[:-14]

	try:
		env = open_environment(project)

		# Trac 0.11: add [inherit] section
		changes = False
		is_present = env.config.has_option('inherit', 'file')
		if not is_present:
			env.config.set('inherit', 'file', '/etc/webapps/trac/trac.ini')
			print 'Set [inherit] file to /etc/webapps/trac/trac.ini in %s' % project
			changes = True

		if changes:
			env.config.save()
	except TracError, e:
		print e.message
