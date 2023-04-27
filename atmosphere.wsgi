#!/usr/bin/python3
import sys
sys.path.insert(0,"/var/www/atmosphere/")
sys.path.insert(0,"/var/www/atmosphere/atmosphere/")

import logging
logging.basicConfig(stream=sys.stderr)

from atmosphere import app as application
