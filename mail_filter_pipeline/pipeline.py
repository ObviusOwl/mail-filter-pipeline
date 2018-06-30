
from mail_filter_pipeline.filter_plugin import FilterPlugin
from mail_filter_pipeline.errors import FilterRuntimeError

class Pipeline( object ):
    
    def __init__(self):
        self.conf = None
        self.message = None
        self.filters = []
    
    def setConf( self, conf ):
        self.conf = conf
    
    def setMessage( self, message ):
        self.message = message
    
    def initFilters(self):
        assert self.conf != None
        for filtCnf in self.conf.getFilters():
            pluginName = filtCnf.getPluginName()
            if FilterPlugin.havePlugin( pluginName ):
                myPlugin = FilterPlugin.getClassByName( pluginName )()
                myPlugin.config( filtCnf )
                self.filters.append( myPlugin )
            else:
                self.logger.error( "failed to find filter plugin '{}'. Plugin does not exists or is not loaded.".format(pluginName) )
    
    def run(self):
        for filter in self.filters:
            if filter.getIgnoreExceptions():
                try:
                    filter.run( self.message )
                except Exception as e:
                    self.logger.exception("Ignored exception in filter")
            else:
                filter.run( self.message )
