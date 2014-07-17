#!/usr/bin/env python

import sys
import alerter.config

alerter.config.setup(sys.argv[1:])

import alerter.log
import alerter.alert
