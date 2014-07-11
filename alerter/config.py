import os
import sys
import getopt

# f your configparser

CONF={}

prog = os.path.basename(sys.argv[0]).rsplit('.')[0]

DEFAULTS={
    'log_dir': '/var/log',
    'log_file': '%s.log' % prog,
    'alerter': 'collectd',
    'config_file': '/etc/alerter.conf',
}

_TRUE=['yes', 'true', 1, '1']
_FALSE=['no', 'false', 0, '0']

CONF.update(DEFAULTS)
CONF['prog'] = prog

def regularize_arg(arg):
    arglist = []

    xlat = {'c': '--config_file='}

    if arg[0] == '-' and arg[1] != '-':
        # single dash option
        index = 1
        while index < len(arg):
            if arg[index] in xlat:
                entry = xlat[arg[index]]
                if entry.endswith('='):
                    if index + 1 < len(arg):
                        arglist += [entry[:-1], arg[index + 1:]]
                        return arglist
                    else:
                        arglist.append(entry[:-1])
                        return arglist

                # a non-option arg
                arglist.append(entry)
                arglist.append(1)
            else:
                sys.stderr.write('Bad argument: %s\n' % arg[index])
                sys.exit(1)

            index += 1
    elif arg.startswith('--') and '=' in arg:
        arglist = arg.split('=', 2)
    else:
        arglist.append(arg)

    return arglist


def parse_args(args):
    index=0

    alist = []
    olist = []

    arglist = []
    for arg in args:
        for a in regularize_arg(arg):
            arglist.append(a)

    while(index < len(arglist)):
        arg = arglist[index]

        if arg.startswith('--'):
            arg = arg[2:]
            if index == len(arglist):
                sys.stderr.write('missing opt for arg --%s\n' % arg)
                sys.exit(1)

            index += 1
            olist.append([arg, arglist[index]])
        else:
            alist.append(arg)

        index += 1

    return olist, alist


def type_coerce(a):
    if a in _TRUE:
        return True
    if a in _FALSE:
        return False

    if a.isdigit():
        return int(a)

    return a


def ini_load(file):
    config = {}
    current_section = None

    line_number = 0

    with open(file, 'r') as f:
        for line in f:
            line_number += 1
            line = line.strip()
            if line == '':
                continue

            if line[0] == '#':
                continue

            if line[0] == '[' and line[-1] == ']':
                current_section = line[1:-1]
                config[current_section] = {}
            else:
                if current_section is None:
                    sys.stderr.write('config info not in section heading: line %d\n' % line_number)
                    sys.exit(1)

                if not '=' in line:
                    sys.stderr.write('not key/value pair: line %d\n' % line_number);
                    sys.exit(1)

                key, value = [x.strip() for x in line.split('=', 2)]
                value = type_coerce(value)
                config[current_section][key] = value

    return config

def setup(args):
    olist, alist = parse_args(args)

    for o, a in olist:
        CONF[o] = type_coerce(a)

    CONF['args'] = alist

    if not os.path.isfile(CONF['config_file']):
        sys.stderr.write('missing conf file: %s\n' % CONF['config_file'])
        sys.exit(1)

    config = ini_load(CONF['config_file'])

    if 'DEFAULT' in config:
        CONF.update(config['DEFAULT'])

    if CONF['prog'] in config:
        CONF.update(config[CONF['prog']])
