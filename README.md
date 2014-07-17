# alerter #

stupid library for sending alerts either to pagerduty or to be run as
an exec module from collectd.

config file is assumed to be /etc/alerter.conf, but can be overriden
with -c (--config_file) flag.

config file is ini-format, with a DEFAULT section that is merged into
every utilties config path.  Overrides can come from long command line
flags matching the config value.

valid config options:

* log_syslog (default False): should we log to syslog?
* syslog_facility (default local7): what facility if syslogging?
* log_alerts (default False): should we log all alerts in addition to alerting?
* log_logfile (default False): should we log to file?
* log_dir (default /var/log): base path for logfile if logging to file
* log_file (default <prog>.log): filename for logfile is logging to file
* log_stderr (default true): should we log to stderr?
* log_level (default warning): python logging level of logger
* log_format (default %(asctime)s %(message)s) log file format
* date_format (default %Y-%m-%dT%H:%M:%S) date format for log
* config_file (default /etc/alerter.conf) override with --config_file
* alerter (default collectd) either collectd or pagerduty
* secondary_alerter (default None) alerter to call when 'alerter' fails.
* pagerduty_domain subdomain for pagerduty site (xxx.pagerduty.com)
* service_key apiable pagerduty service key

sample program:

~~~~
#!/usr/bin/env python

import alerter

CONF = alerter.config.CONF
ALERTER = alerter.alert.ALERTER
LOG = alerter.log.LOG

LOG.info('starting alerting run')
ALERTER.failure('sda', 'low disk space', description='out of disk space on /dev/sda')
LOG.info('done alerting')
~~~~
