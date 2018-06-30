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
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conf = None
        
    def config( self, conf ):
        self.conf = conf

    def getIgnoreExceptions(self):
        assert self.conf != None
        return self.conf.getIgnoreExceptions()

    def run( self, message ):
        raise NotImplementedError()

