#!/usr/bin/env python

import sys

sys.path.append('.')

import alerter

CONF = alerter.config.CONF
ALERTER = alerter.alert.ALERTER
LOG = alerter.log.LOG

##
LOG.info('starting polling loop')
ALERTER.warning('cpu0', 'high cpu', description='high cpu on cpu0')
LOG.info('done processing')
