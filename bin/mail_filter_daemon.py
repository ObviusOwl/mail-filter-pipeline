#!/usr/bin/env python3
import sys
import os
import logging
import argparse

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ) )

from mail_filter_pipeline import mail_filter_daemon

def parseArgs():
    parser = argparse.ArgumentParser(description='Pipeline mail filter daemon')
    parser.add_argument('-c','--config', action='store', dest='config_path', default=None,
                help='Path to config file')
    parser.add_argument('--log-driver', action='store', dest='logDriver', default=None,
                help='Log driver to send log messages to. If not set logs are written to stderr', choices=["syslog","file"] )
    parser.add_argument('--log-dest', action='store', dest='logDest', default=None,
                help='Log destination. Path to a log file for the file logger.' )
    parser.add_argument('-v','--verbosity', action='store', dest='logVerb', default="error",
                help='Logging verbosity.', choices=["error","warning","debug"] )

    return parser.parse_args()
    

if __name__ == '__main__':

    logVerbosityMap = { "error": logging.ERROR, "warning": logging.WARNING, "debug":logging.DEBUG }

    app = mail_filter_daemon.MailFilterDaemon()
    args = parseArgs()

    if args.config_path != None:
        app.loadConfigFile( args.config_path )
    
    if args.logVerb in logVerbosityMap.keys():
        app.setLogVerbosity( logVerbosityMap[args.logVerb] )
    app.setLogDriver( args.logDriver )
    app.setLogDestination( args.logDest )

    app.main()
