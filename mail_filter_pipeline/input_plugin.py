import logging

class InputPluginType(type):
    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        try:
            if cls.__name__ != "InputPlugin": # base class
                if not cls.pluginName in cls.registry.keys():
                    cls.registry[ cls.pluginName ] = cls
                else:
                    raise TypeError("Another InputPlugin with name '{}' is already registered.".format(cls.pluginName))
        except AttributeError:
            raise TypeError( "Please implement the class variable 'pluginName' if your class inherits from InputPlugin" ) from None

    def __iter__(cls):
        return iter(cls.registry)
    
    def getClassByName( cls, name ):
        if name in cls.registry.keys():
            return cls.registry[ name ]
        raise KeyError()

    def havePlugin( cls, name ):
        return name in cls.registry.keys()


class InputPlugin( object, metaclass=InputPluginType ):
    
    def __init__(self, mailQueue):
        self.name = ""
        self.mailQueue = mailQueue
        self.logger = logging.getLogger(__name__)

    def setName( self, name ):
        self.name = name
    
    def start( self ):
        raise NotImplementedError()
    
    def stop( self ):
        raise NotImplementedError()

    def config( self, conf ):
        raise NotImplementedError()

