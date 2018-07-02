import logging

class FilterPluginType(type):
    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        try:
            if cls.__name__ != "FilterPlugin": # base class
                if not cls.pluginName in cls.registry.keys():
                    cls.registry[ cls.pluginName ] = cls
                else:
                    raise TypeError("Another FilterPlugin with name '{}' is already registered.".format(cls.pluginName))
        except AttributeError:
            raise TypeError( "Please implement the class variable 'pluginName' if your class inherits from FilterPlugin" ) from None

    def __iter__(cls):
        return iter(cls.registry)
    
    def getClassByName( cls, name ):
        if name in cls.registry.keys():
            return cls.registry[ name ]
        raise KeyError()

    def havePlugin( cls, name ):
        return name in cls.registry.keys()


class FilterPlugin( object, metaclass=FilterPluginType ):
    """ Base class for all filter plugins
    
    Any plugin, which implements a filter should inherit from this class.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conf = None
        
    def config( self, conf ):
        """ Routine for configuring the instance of the plugin.
        
        Args:
            conf (FilterConfig): configuration object for this filter's instance
            
        Use this method for configuration initialisation. It is called once per lifetime
        of the plugin's instance, including once at program start up to check if 
        the instance is functional.
        
        For missing mandatory configuration keys or other fatal problems, raise
        an exception here to make the daemon fail fast at start up.
        """
        self.conf = conf

    def getIgnoreExceptions(self):
        """ Check if exceptions raised during run() should make the pipeline fail""""
        assert self.conf != None
        return self.conf.getIgnoreExceptions()

    def run( self, message ):
        """ This is the main routine of the plugin.
        
        Args:
            message (Message): Message object of the message passing through the pipeline
        
        This is where the plugin does it's duty. 
        
        Exceptions raised here make the complete pipeline fail (if getIgnoreExceptions() return true)
        or are catched outside and the pipeline continues to run.
        """
        raise NotImplementedError()

