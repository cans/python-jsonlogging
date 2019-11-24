==============================
Yet another JSON log formatter
==============================

A python module to emit log entries as serialized JSON objects.

Features
""""""""

- the ability to rename standard LogRecord attributes in
  the json output:

  .. code-block:: Python
     :emphasize-lines: 7

      import logging
      import jsonlogging
      import sys

      handler = logging.StreamHandler(sys.stdout)
      handler.setFormatter(jsonlogging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                                 keymap={'asctime': 'timestamp'})
      logger = logging.getLogger('some-logger')
      logger.propagate = False
      logger.addHandler(handler)
      logger.setLevel(logging.DEBUG)

      logger.debug('This is a detail')
      logger.info('This is an information')
      logger.warning('This is suspicious')
      logger.error('This is a problem')

- the ability to use the format style you prefer (prevent
  format mismatches whether you want JSON, text, ...);
- structured stack traces, not just a blob of text;
- support for global extras, like an application name,
  anything you would normally "hardcode" in the log format
  string, e.g. ``'%(asctime)s - %(levelname)s - myapplication - $(message)s'``;
- excellent test coverage;


Example YAML configuration
""""""""""""""""""""""""""

Below is an example of a configuration file you can use with this library.
A configured below, JSON logs will be sent to the file ``/tmp/jsonlogging.log``

Note that we use the same format for both log formatters. The JSON formatter
simply ignores the extraneous text between log record attribute names (here
``asctime``, ``level`` & ``message``)

.. code-block:: YAML

   ---
   logformat: &logfmt
     fmt: '%(asctime)s - %(level)s - %(message)s'
   logging:  # Below is a standard Python logging config
     version: 1
     formatters:
       json:
         (): jsonlogging.Formatter
         <<: *logfmt
         keymap:
           asctime: timestamp
         trunc_path: true
       console:
         class: logging.Formatter
         <<: *logfmt
     handlers:
       console:
         class: logging.StreamHandler
         stream: ext://sys.stdout
         propagate: false
       syslog:
         class: logging.FileHandler
         path: /tmp/jsonlogging.log
         propagate: false
    loggers:
      myapplication:
        level: INFO
      verboselib:
        level: ERROR
    root:
       level: DEBUG
       handlers:
       - console
       - syslog

Note the use of the ``()`` key, in the yaml file, to specify the
formatter class to instanciate. You have to `use this syntax <user>`_
so the configuration function will pass arguments other than ``fmt``,
``datefmt`` and ``style`` to the class constructor. If you use the
``class`` key (see below), only those 3 arguments are passed.

.. code-block::

   ---
   logging:  # Below is a standard Python logging config
     version: 1
     formatters:
       json:
         class: jsonlogging.Formatter
         fmt: '%(message)s'
         datefmt: '%Y%m%d %H%M%S.%f'
         # These arguments will be ignored
         keymap:
           asctime: timestamp
         trunc_path: true

To use the configuration file in your application, you can do as follows:

.. code-block:: Python

   def main(config_path):
       with open(config_path, 'r') as config_file:
           config = yaml.safe_load(config_file)

       logging.config.dictConfig(config['logging'])  # and your set !

       logger = logging.getLogger('myapplication')
       logger.debug('Should not appear')
       logger.info('Should appear in your console and in /tmp/jsonlogging.log')


.. _user: https://docs.python.org/3/library/logging.config.html#user-defined-objects
