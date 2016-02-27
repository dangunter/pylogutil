"""
Most basic usage example.
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'

import logging
import sys

import logutil as lu

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

prog = sys.argv[0]

t0 = lu.start(log, "program", file=__file__)
lu.event(log, "one event")
lu.end(log, "program", t0, file=prog)

