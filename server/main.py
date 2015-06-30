import sys, atexit
#from signal import SIGTERM
#import logging
#import logging.handlers

import modules
from core.feeder import Feeder

if __name__ == "__main__":
    #logger = logging.getLogger()
    #logger.setLevel(logging.DEBUG)
    #filehandler = logging.handlers.TimedRotatingFileHandler('/tmp/daemon.log',when='midnight',interval=1,backupCount=10)
    #filehandler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    #logger.addHandler(filehandler)

    daemon = Feeder(host='192.168.10.2',pidfile='/tmp/python-daemon.pid',stdout='/tmp/out.log')
    if len(sys.argv) == 2:
#        logger.info('{} {}'.format(sys.argv[0],sys.argv[1]))
 
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        else:
            print ("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
    #    logger.warning('show cmd deamon usage')
        print ("Usage: {} start|stop|restart".format(sys.argv[0]))
        sys.exit(2)
 
