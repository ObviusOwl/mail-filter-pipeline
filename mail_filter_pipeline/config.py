import os
import os.path
import yaml
import logging

from mail_filter_pipeline.errors import ConfigError

class Config( object ):
    def __init__( self ):
        self.confFile = None
        self.conf = None
        self.logVerbosityMap = { "error": logging.ERROR, "warning": logging.WARNING, "debug":logging.DEBUG }
    
    def loadFile( self, confFile ):
        # TODO: raise on syntax error + catch and log
        self.confFile = confFile
        with open(confFile,'r') as cf:
            self.conf = yaml.safe_load( cf )

    def getDaemonConfig(self, key, fallback=None):
        if "daemon_config" in self.conf and key in self.conf["daemon_config"]:
            return self.conf["daemon_config"][key]
        return fallback
    
    def _getInputPluginsConfig(self):
        if not "inputs" in self.conf:
            return []
        return self.conf["inputs"]

    def getInputPlugins(self):
        cnfList = self._getInputPluginsConfig()
        cnfList2 = []
        for cnf in cnfList:
            cnf2 = InputConfig( cnf )
            cnfList2.append( cnf2 )
        return cnfList2

    def _getPipelinesConfig(self):
        if not "pipelines" in self.conf:
            return []
        return self.conf["pipelines"]

    def getPipelines(self):
        cnfList = self._getPipelinesConfig()
        cnfList2 = []
        for cnf in cnfList:
            cnf2 = PipelineConfig( cnf )
            cnfList2.append( cnf2 )
        return cnfList2
    
    def getPluginPaths(self):
        if not "plugins" in self.conf:
            return []
        return self.conf["plugins"]

    def getMailQueueSize(self):
        return self.getDaemonConfig("mail_queue_size",fallback=5)

    def getPipelineQueueSize(self):
        return self.getDaemonConfig("pipeline_queue_size",fallback=5)

    def getPipelineThreadCount(self):
        return self.getDaemonConfig("pipeline_threads",fallback=5)

    def getLoggingVerbosity(self):
        verb = self.getDaemonConfig("log_verbosity")
        if verb in self.logVerbosityMap.keys():
            return self.logVerbosityMap[verb]
        return None

class InputConfig( object ):
    def __init__( self, conf ):
        self.conf = conf
        self.reservedKeys = ["name"]
        self.stablePluginConfigKey = None
    
    def getName( self ):
        for key in self.conf.keys():
            if key == "name":
                return self.conf[key]
        return ""
    
    def getPluginName( self ):
        if self.stablePluginConfigKey != None:
            # cached key
            return self.stablePluginConfigKey
        # set default, in case no key can be found
        self.stablePluginConfigKey = None
        # non-reserved keys define the plugin name (like ansible modules in tasks)
        # search for the first one and pin it as our one and only plugin name
        for key in self.conf.keys():
            if not key in self.reservedKeys:
                self.stablePluginConfigKey = key
        return self.stablePluginConfigKey

    def getPluginConfig( self ):
        key = self.getPluginName()
        if key in self.conf.keys():
            return self.conf[key]
        return None


class PipelineConfig( object ):

    def __init__( self, conf ):
        self.conf = conf
        self.reservedKeys = ["name","ignore_exceptions"]
    
    def getName( self ):
        if "name" in self.conf:
            return self.conf["name"]
        return ""
    
    def getInputNames(self):
        if "inputs" in self.conf:
            # TODO: check if have list of strings
            return self.conf["inputs"]
        return []
    
    def getFilters(self):
        filters = []
        if not "filters" in self.conf:
            return filters
        # TODO: check if have list
    
        for filterConf in self.conf["filters"]:
            filterKey = None
            for key in list( filterConf.keys() ):
                if key not in self.reservedKeys:
                    filterKey = key
            if filterKey == None:
                continue
            pluginConf = filterConf[ filterKey ]
            cnf = FilterConfig(filterConf, pluginConf, filterKey)
            filters.append( cnf )
        return filters

class FilterConfig( object ):

    def __init__( self, filterConf, pluginConf, pluginName ):
        self.pluginConf = pluginConf
        self.filterConf = filterConf
        self.pluginName = pluginName

    def getFilterConfig(self):
        return self.filterConf
    
    def getPluginConfig(self):
        return self.pluginConf
    
    def getPluginName(self):
        return self.pluginName

    def getIgnoreExceptions(self):
        if "ignore_exceptions" in self.pluginConf:
            return self.pluginConf["ignore_exceptions"]
        return False

