import os
import sys
import logging
import logging.handlers
import alerter.config

CONF = alerter.config.CONF

_DEFAULT_LOG_FORMAT = '%(asctime)s %(message)s'
_DEFAULT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

def setup(name):
    log = getLogger(name)

    if CONF.get('log_syslog', False):
        try:
            facility = CONF.get('syslog_facility', 'local7')
            syslog = logging.handlers.SysLogHandler(address='/dev/log',
                                                    facility=facility)
        except IOError as e:
            sys.stderr.write('failed to log to syslog socket: %s' % str(e))
            sys.exit(1)

        log.addHandler(syslog)

    logpath = os.path.join(CONF['log_dir'], CONF['log_file'])
    if CONF.get('log_logfile', False):
        try:
            filelog = logging.handlers.WatchedFileHandler(logpath)
        except IOError as e:
            sys.stderr.write('failed to write to log file %s: %s' % (
                logpath, e))
            sys.exit(1)

        log.addHandler(filelog)

    if CONF.get('log_stderr', True):
        try:
            stderrlog = logging.StreamHandler(stream=sys.stderr)
        except IOError as e:
            sys.stderr.write('failed to log to stderr: %s' % str(e))
            sys.exit(1)

        log.addHandler(stderrlog)

    if len(log.handlers) == 0:
        log.addHandler(logging.NullHandler())

    for handler in log.handlers:
        log_format = CONF.get('log_format', _DEFAULT_LOG_FORMAT)
        date_format = CONF.get('date_format', _DEFAULT_DATE_FORMAT)

        handler.setFormatter(logging.Formatter(fmt=log_format,
                                               datefmt=date_format))

    log_level = CONF.get('log_level', 'WARNING')
    log.setLevel(getattr(logging, log_level.upper(), 'WARNING'))

    return log


def getLogger(name=None):
    if name is None:
        return logging.root
    return logging.getLogger(name)


LOG=setup(CONF['prog'])
