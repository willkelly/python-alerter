from setuptools import setup

version = '0.0.1'

setup(
    name = 'alerter',
    version = version,
    author = 'Ron Pedde',
    author_email = 'ron@pedde.com',
    description = 'pagerduty/collectd framework for python scripts',
    packages = ['alerter'],
    classifiers = ['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.7'],
    install_requires = ['pygerduty'])
