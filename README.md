# pylogutil

Some Python logging utility code, for re-use across projects.

## Installation

Everything is in the file `logutil.py`. Copy this where you need it, rename 
it as you see fit.

## Usage

In general, the module just defines a few functions that layer on top of the 
existing Python logging system and provide some standard formatting for 
key/value pairs and for log messages that bracket some activity.

A basic example is:

    # imports
    import logging; logging.basicConfig()
    import logutil
    
    # standard Python logging setup
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    
    # write some log messages
    t0 = logutil.start(log, "program", file=__file__)
    logutil.event(log, "one event")
    logutil.end(log, "program", t0, file=__file__)

The output of this example will look similar to this:

    INFO:root:2016-02-27T03:04:23.611474 program.begin ; file=basic.py
    INFO:root:2016-02-27T03:04:23.611672 one event ; 
    INFO:root:2016-02-27T03:04:23.611754 program.end (0.000280) ; file=basic.py

See the 'examples' directory for more complicated examples.

## License

See LICENSE file in this repository.

## Contact

For questions or suggestions contact Dan Gunter <dkgunter@lbl.gov>.