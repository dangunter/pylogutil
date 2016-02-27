"""
Functions for easy, flexible, structured logging in Python.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'

# stdlib
import ConfigParser
import logging
import logging.config
import time
from datetime import datetime
import six
# third-party
try:
    import yaml
except ImportError:
    yaml = None

###
# Constants
###

# This flag controls whether the messages should include
# their own timestamp. You would want to set this to False if
# the main log message already has a timestamp.
include_timestamp = True

# Default logging level for log_{start, end, event}.
# This is just for convenience.
DEFAULT_LEVEL = logging.INFO

# Message format constants
# You can set these to whatever you like, these are just the defaults.
_KVPSECSEP = ' ; '  # between message and key/value section
_KVPSEP = ','  # between one key=value and another
_KVSEP = '='  # between key and value
_MESSAGE_FORMATS = [
    {'entry': '{func_name}.begin' + _KVPSECSEP + '{kvp}',
     'exit' : '{func_name}.end ({dur})' + _KVPSECSEP + '{kvp}',
     'exit_nodur' : '{func_name}.end' + _KVPSECSEP + '{kvp}',
     'event': '{func_name}' + _KVPSECSEP + '{kvp}'},
    {'entry': '{timestamp} {func_name}.begin' + _KVPSECSEP + '{kvp}',
     'exit' : '{timestamp} {func_name}.end ({dur})' + _KVPSECSEP + '{kvp}',
     'exit_nodur' : '{func_name}.end' + _KVPSECSEP + '{kvp}',
     'event': '{timestamp} {func_name}' + _KVPSECSEP + '{kvp}'},
]

###
# Exported functions
###

def event(logger, name, level=None, fmt=None, **kvp):
    """Log a single message.

    Args:
        logger (logging.Logger): Target Python logger instance
        name (str): Name of the event
        level (int): Logging level (uses module's DEFAULT_LEVEL if not given)
        fmt (str): Message format; usually you will not set this
        kvp (dict): Key/value pairs for message content.
    Return:
         (float) Logged time as UNIX timestamp (seconds since 1/1/1970)
    """
    t0 = time.time()
    kvp_str = _format_kvp(kvp) if kvp else ''
    d = dict(timestamp=format_timestamp(t0),
             func_name=name, kvp=kvp_str)
    fmt = fmt or _default_message('event')
    msg = fmt.format(**d)
    if level is None:
        level = DEFAULT_LEVEL
    logger.log(level, msg)
    return t0

#
def start(logger, name, level=None, **kvp):
    """Log the start of some activity.

    Args:
        logger (logging.Logger): Target Python logger instance
        name (str): Name of the event
        level (int): Logging level (uses module's DEFAULT_LEVEL if not given)
        kvp (dict): Key/value pairs for message content.
    Return:
         (float) Logged time as UNIX timestamp (seconds since 1/1/1970)
    """
    t0 = time.time()
    kvp_str = _format_kvp(kvp) if kvp else ''
    d = dict(timestamp=format_timestamp(t0),
             func_name=name, kvp=kvp_str)
    fmt = _default_message('entry')
    msg = fmt.format(**d)
    if level is None:
        level = DEFAULT_LEVEL
    logger.log(level, msg)
    return t0

def end(logger, name, t0=None, level=None, status_code=0, **kvp):
    """Log the end of some activity.

    Args:
        logger (logging.Logger): Target Python logger instance
        name (str): Name of the event
        t0 (float): UNIX timestamp from `start()`. If this is not set,
                    no duration will be reported.
        level (int): Logging level (uses module's DEFAULT_LEVEL if not given)
        status_code (int): Indicate success (0) or other condition (non-zero)
                           with a status code.
        kvp (dict): Key/value pairs for message content.
    """
    t1 = time.time()
    kvp_str = _format_kvp(kvp) if kvp else ''
    d = dict(timestamp=format_timestamp(t1),
             func_name=name,
             kvp=kvp_str,
             status=status_code)
    if t0 is not None:
        d['dur'] = '{:.6f}'.format(t1 - t0)
        fmt = _default_message('exit')
    else:
        fmt = _default_message('exit_nodur')
    if level is None:
        level = DEFAULT_LEVEL
    logger.log(level, fmt.format(**d))

def wrap_method(logger, name=None, level=logging.INFO, **kvp):
    """Wrap a method in a start() / end().

    Args:
        logger (logging.Logger): Target Python logger instance
        name (str): Name for the wrapped activity; will use the name of
                        the function by default.
        level (int): Logging level
        kvp (dict): Key/value pairs for message content.
    """

    def real_decorator(method):
        # choose name for logged event
        func_name = name or method.__name__

        # create wrapper
        def method_wrapper(self, *args, **kwds):
            t0 = start(logger, func_name, level=level, **kvp)
            returnval = method(self, *args, **kwds)
            end(logger, func_name, t0, level=level, **kvp)
            return returnval

        # return wrapper
        return method_wrapper

    return real_decorator

def wrap_func(logger, name=None, level=logging.INFO, **kvp):
    """Wrap a function in a start() / end().

    Args:
        logger (logging.Logger): Target Python logger instance
        name (str): Name for the wrapped activity; will use the name of
                        the function by default.
        level (int): Logging level
        kvp (dict): Key/value pairs for message content.
    """

    def real_decorator(func):
        # choose name for cogged event
        func_name = name or func.__name__

        # create wrapper
        def func_wrapper(*args, **kwds):
            t0 = start(logger, func_name, level=level, **kvp)
            returnval = func(*args, **kwds)
            end(logger, func_name, t0, level=level, **kvp)
            return returnval

        # return wrapper
        return func_wrapper

    return real_decorator


def configure(cfg):
    """Configure logging from YAML or ConfigParser file, or
    a dictionary (presumably parsed from one of these files).

    If input is a filename, both types of parsing will be tried
    (assuming the yaml package is available), unless the file ends
    with '.yaml', in which case it's an error if it cannot be parsed as YAML.

    Args:
        cfg (str or dict): Path to configuration file, or config dict
    Raises:
        IOError, if file cannot be opened or parsed
        ValueError, if input is a dict and the logging module dislikes it

    """
    if isinstance(cfg, dict):
        logging.config.dictConfig(cfg)
        return
    try:
        is_yaml, force_yaml = False, cfg.endswith('.yaml')
        if yaml is None:
            if force_yaml:
                raise IOError('Configuration file ended in ".yaml", but '
                              'The third-party "yaml" package was not found. To fix, '
                              'either use a ConfigParse-style file, or add the yaml '
                              'package (e.g., "pip install pyyaml").')
        else:
            try:
                cfgdict = yaml.load(open(cfg, 'r'))
                is_yaml = True
                logging.config.dictConfig(cfgdict)
            except yaml.error.YAMLError:
                if force_yaml:
                    raise IOError('Cannot parse as YAML')
        if not is_yaml:
            try:
                logging.config.fileConfig(cfg)
            except ConfigParser.Error:
                raise IOError('Cannot parse as either YAML '
                              'or ConfigParse format')
    except Exception as err:
        raise IOError('Error configuring from file "{}": {}'.format(
                cfg, err))

###
# Internal functions
###

def _default_message(mtype):
    return _MESSAGE_FORMATS[include_timestamp][mtype]

def _format_kvp(d):
    """Format key-value pairs as a string.

    Args:
        d (dict): Key/value pair dictionary
    """
    pairs, sep = [], _KVPSEP
    for k, v in d.items():
        if isinstance(v, six.string_types):
            if sep in v:
                v = v.replace(',', '\\,')
            elif len(v) == 0:
                v = "''"
        pairs.append((k, v))
    s = sep.join(['{}{}{}'.format(k, _KVSEP, v) for k, v in pairs])
    return s

# Format a timestamp as an ISO8601 string.
format_timestamp = lambda t: datetime.fromtimestamp(t).isoformat()
