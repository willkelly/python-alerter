#!/usr/bin/env python

import pygerduty
import socket
import time
import sys
import socket

import alerter

LOG = alerter.log.LOG
CONF = alerter.config.CONF


class Alert(object):
    def __init__(self):
        self.last_severities = {}

    # severity: failure, warning, okay
    def alert(self, severity, component,
              alert_type='Generic', host=None,
              description='<unknown>'):
        pass

    def should_suppress(self, host, component, severity):
        # only alert on state transitions or restarts
        if self.last_status(host, component) == severity:
            return True
        return False

    def last_status(self, host, component):
        # we return "new" here if the item is not in the dict so we
        # will always send a message on restart.
        return self.last_severities.get((host, component), "new")

    def update_status(self, host, component, severity):
        self.last_severities[(host, component)] = severity

    def failure(self, component, alert_type='Generic', host=None,
                description=None):
        self.alert('failure', component, alert_type=alert_type,
                   host=host, description=description)

    def warning(self, component, alert_type='Generic', host=None,
                description='warning'):
        self.alert('warning', component, alert_type=alert_type,
                   host=host, description=description)

    def okay(self, component, alert_type='Generic', host=None,
             description='warning'):
        self.alert('okay', component, alert_type=alert_type,
                   host=host, description=description)


class PagerDutyAlert(Alert):
    def __init__(self):
        super(PagerDutyAlert, self).__init__()
        for value in ['pagerduty_domain', 'service_key']:
            if not value in CONF:
                LOG.error('missing "%s" in config' % value)
                sys.exit(1)

        self.pager = pygerduty.PagerDuty(CONF['pagerduty_domain'], 'unused')

    def alert(self, severity, component,
              alert_type='Generic', host=None,
              description='<unknown>'):

        if host is None:
            host = socket.gethostname()

        incident_key = '%s-%s' % (host, component)
        incident_key = incident_key.replace(' ', '_')

        if not self.should_suppress(host, component, severity):
            action = None

            if severity.lower() == 'failure':
                action = 'trigger'
            elif severity.lower() == 'warning':
                action = 'trigger'
            elif severity.lower() == 'okay':
                action = 'resolve'

            if action is not None:
                LOG.debug('sending pagerduty alert')
                self.pager.create_event(CONF['service_key'],
                                        description,
                                        action,
                                        None,  # details
                                        incident_key,
                                        client=CONF['prog'])

                # if successful, update the state
                self.update_status(host, component, severity)


class CollectdAlert(Alert):
    def __init__(self):
        super(CollectdAlert, self).__init__()

    def alert(self, severity, component,
              alert_type='Generic', host=None,
              description='<unknown>'):
        if host is None:
            host = socket.gethostname()

        if not self.should_suppress(host, component, severity):
            sys.stdout.write('PUTNOTIF message="%s" severity=%s time=%d'
                             ' host=%s\n' % (description,
                                             severity,
                                             int(time.time()),
                                             host))
            sys.stdout.flush()

            self.update_status(host, component, severity)

if not 'alerter' in CONF:
    LOG.error('missing "alerter" in config')
    sys.exit(1)

if CONF['alerter'].lower() == 'collectd':
    ALERTER = CollectdAlert()
elif CONF['alerter'].lower() == 'pagerduty':
    ALERTER = PagerDutyAlert()
else:
    LOG.error('invalid "alerter" type in config')
    sys.exit(1)
