import logging
import logging.handlers
import queue
import os
import copy

from .config import Config
from .input_plugin import InputPlugin
from .pipeline import Pipeline
from .pipeline_executor import PipelineExecutor
from .core import *
from .errors import *

class MailFilterDaemon( object ):

    def __init__(self):
        self.rootLogger = logging.getLogger( os.path.basename(os.path.dirname(__file__)) )
        self.logger = logging.getLogger(__name__)
        self.logVerbosity = None
        self.logDriver = None
        self.logDestination = None

        self.conf = Config()
        self.inputPlugins = []
        self.mailQueue = None
        self.pipelineQueue = None
        self.pipelineExecutors = []
    
    def loadConfigFile(self, fileName ):
        self.conf.loadFile( fileName )
    
    def setLogVerbosity(self, verb ):
        self.logVerbosity = verb

    def setLogDriver(self, name ):
        if name in ["syslog","file"]:
            self.logDriver = name

    def setLogDestination(self, dest ):
        self.logDestination = dest
    
    def initLogging(self):
        # TODO: check config file log verbosity
        if self.logVerbosity != None:
            logVerbosity = self.logVerbosity
        else:
            logVerbosity = logging.WARNING
            
        logFormatter = logging.Formatter('{levelname}:{name}: {message}', style='{')

        # default to stderr logging
        logHandler = logging.StreamHandler()
        if self.logDriver == "file" and self.logDestination != None:
            logHandler = logging.FileHandler( self.logDestination )
        elif self.logDriver == "syslog":
            logHandler = logging.handlers.SysLogHandler( "/dev/log" )

        logHandler.setLevel( logVerbosity  )
        logHandler.setFormatter( logFormatter )
        self.rootLogger.setLevel( logVerbosity )
        self.rootLogger.addHandler( logHandler )
    
    def initInputPlugins(self):
        for inCnf in self.conf.getInputPlugins():
            inputPluginName = inCnf.getPluginName()
            if InputPlugin.havePlugin( inputPluginName ):
                myPlugin = InputPlugin.getClassByName( inputPluginName )( self.mailQueue )
                myPlugin.setName( inCnf.getName() )
                myPlugin.config( inCnf.getPluginConfig() )
                self.inputPlugins.append( myPlugin )
            else:
                self.logger.error( "failed to find input plugin '{}'. Plugin does not exists or is not loaded.".format(inputPluginName) )
        if len(self.inputPlugins) == 0:
            self.logger.warning( "No input plugin was defined, no mail will be recieved".format(inputPluginName) )

    def makePipelines(self, message):
        assert self.conf != None
        pipelines = []
        pipeConfs = self.conf.getPipelines()
        msgSrc = message.getSourceName()

        for pipeCnf in pipeConfs:
            if msgSrc in pipeCnf.getInputNames():
                # only load pipelines subscribed to the input ('inputs' config key)
                pipe = Pipeline()
                # pipelines run multithreaded, each thread should get it's copy of the data
                pipe.setConf( copy.deepcopy(pipeCnf) )
                pipe.setMessage( copy.deepcopy(message) )
                pipelines.append( pipe )
        return pipelines

    def main(self):
        assert self.conf != None
        try:
            self.mailQueue = queue.Queue( maxsize=self.conf.getMailQueueSize() )
            self.pipelineQueue = queue.Queue( maxsize=self.conf.getPipelineQueueSize() )
            
            self.initLogging()
            # load input plugins but not start them yet
            self.initInputPlugins()
            # load pipelines
            # TODO: run checks on all pipelines and filters: config, plugin loaded
            
            # start worker threads for the pipelines
            for i in range( self.conf.getPipelineThreadCount() ):
                self.pipelineExecutors.append( PipelineExecutor(self.pipelineQueue) )

            # start input plugins. Make sure all plugins handle their threads and do not block
            for plugin in self.inputPlugins:
                plugin.start()

            self.logger.debug("started main loop")
            while True:
                # get the new message
                msg = self.mailQueue.get( block=True )
                # create the pipeline objects, this alos makes copies of the message and conf
                pipelines = self.makePipelines( msg )
                for pipeline in pipelines:
                    # submit pipeline to the worker queue
                    self.pipelineQueue.put( pipeline, block=True )
                self.mailQueue.task_done()
        except KeyboardInterrupt:
            self.logger.debug("caught keyboard interrupt")
        except FilterRuntimeError as e:
            print( "FilterRuntimeError: see log for details" )
            self.logger.exception( e.message )
            raise SystemExit(1)
        except Exception:
            print( "Error: uncaught exception, see log for details" )
            self.logger.exception("uncaught exception")
            raise SystemExit(1)
        finally:
            self.logger.debug("stopping main loop")
            for plugin in self.inputPlugins:
                plugin.stop()
            # wait for all pipelines to stop
            self.pipelineQueue.join()
