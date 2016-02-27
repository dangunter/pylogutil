"""
Basic example for logging
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'

# stdlib
import logging
import time
# local
import logutil as lu

_log = logging.getLogger('hello')

lu.include_timestamp = False

def configure(level):
    lu.configure({
        'version'   : 1,
        'formatters': {
            'basic': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers'  : {
            'console': {
                'class'    : 'logging.StreamHandler',
                'formatter': 'basic',
                'stream'   : 'ext://sys.stdout'
            }
        },
        'loggers'   : {
            'hello': {
                'handlers': ['console'],
                'level': level
            }
        }
    })

@lu.wrap_func(_log)
def say_hello():
    print("hello, world!")

def main():
    configure('DEBUG')

    lu.event(_log, 'configured', method='dictConfig')

    lu.start(_log, 'main')

    t = lu.start(_log, 'multiple greetings', n=5)
    for i in range(5):
        say_hello()
        lu.event(_log, 'hello_count', level=logging.DEBUG, num=(i + 1))
        print('-------')
        time.sleep(1)
    lu.end(_log, 'multiple greetings', t, n=5)

    lu.end(_log, 'main')

if __name__ == '__main__':
    main()
