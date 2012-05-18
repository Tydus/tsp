#!/usr/bin/python

from time import time,ctime,gmtime
from mongoengine import *
from mongoengine.connection import ConnectionError
from sys import stderr
from os import fork,path
from urllib import quote
from argparse import ArgumentParser
from socket import error as SocketError

from tornado.web import StaticFileHandler,Application,RequestHandler,asynchronous,HTTPError
from tornado.httpclient import AsyncHTTPClient
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from common import *

def strtime(tm=None):
    return "%04d-%02d-%02d %02d:%02d:%02d"%gmtime(tm or time())[:6]

# Log
LOG_FATAL=0
LOG_ERROR=1
LOG_WARNING=2
LOG_INFO=3
LOG_VERBOSE=4
def log(level,s,*args):
    if level<=verbosity:
        print >>logfd,"[%19s][%d]"%(strtime(),level)+s%tuple(args)
        logfd.flush()

def parse_args():
    ap=ArgumentParser(description='TSP Backend Server')

    ap.add_argument('-l','--listen', help='Listen port',default=8080,type=int)

    ap.add_argument('--no-fork', help='Run in forground, for debug use',action='store_true')
    ap.add_argument('-v','--verbose', help='Run in verbose mode, use more to be more verbosity',action='count',default=LOG_INFO)
    ap.add_argument('-q','--quiet', help='Run in quiet mode',action='count',default=0)
    #ap.add_argument('-p','--pid-file', help='PID file',default='/var/run/tsp.pid')
    ap.add_argument('--log-file', help='Log file, use - for stderr',default='/var/log/tsp.log')

    ap.add_argument('--db-host', help='Database host name', default='127.0.0.1')
    ap.add_argument('--db-port', help='Database port', default=27017,type=int)
    ap.add_argument('--db-name', help='Database name', default='osudl')
    ap.add_argument('--db-user', help='Database user name')
    ap.add_argument('--db-pass', help='Database password')

    return ap.parse_args()

def main():
    args=parse_args()

    # Fork
    if not args.no_fork and fork():
        exit(0)

    global logfd, verbosity, osz_dir, url_prefix
    # Assign Log File Descriptor
    try:
        logfd=open(args.log_file,'a') if args.log_file != '-' else stderr
    except Exception:
        print >>stderr, 'FATAL: Cannot write to Log file %s'%args.log_file
        exit(-1)

    # Calc verbosity
    verbosity=args.verbose-args.quiet

    # Connect to DB
    try:
        connect(         args.db_name,
                host    =args.db_host,
                port    =args.db_port,
                username=args.db_user,
                password=args.db_pass,
               )
    except ConnectionError:
        log(LOG_FATAL, 'Cannot connect to DB at mongodb://%s:%d/%s'%(
            args.db_host,
            args.db_port,
            args.db_name,
           ))
        exit(-1)

    # Run Server

    global leafHandlers
    static_path=path.join(path.dirname(__file__),'static')
    leafHandlers=[(r'/(.*\..*)',StaticFileHandler,{'path':static_path})]+leafHandlers
    server=HTTPServer(Application(leafHandlers,cookie_secret='(HY$WGIH(&$#*)I*5yhr)*HG)Oh59878ehT%08'))
    try:
        server.listen(args.listen)
    except SocketError:
        log(LOG_FATAL, 'Cannot listen at 127.0.0.1:%d', args.listen)
        exit(-1)

    log(LOG_INFO, '*'*80)
    log(LOG_INFO, 'TSP Backend Server Started')
    log(LOG_INFO, 'Listening at 127.0.0.1:%d', args.listen)
    log(LOG_INFO, 'Daemon: %s', not args.no_fork)
    log(LOG_INFO, 'Log File: %s', args.log_file if args.log_file != '-' else '<stderr>')
    log(LOG_INFO, 'Log Verbosity: %d', verbosity)
    log(LOG_INFO, '*'*80)

    IOLoop.instance().start()

if __name__=='__main__':
    main()

