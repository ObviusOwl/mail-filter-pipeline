from mail_filter_pipeline.input_plugin import InputPlugin

class NoopInput( InputPlugin ):
    pluginName = "noop"
    
    def __init__(self, mailQueue):
        super().__init__( mailQueue )
    
    def start( self ):
        self.logger.debug( "started noop input plugin named '{}'".format(self.name) )
        
    def stop( self ):
        self.logger.debug( "stopped noop input plugin named '{}'".format(self.name) )
        
    def config( self, cnf ):
        msg = "plugin config: {}".format( str(cnf) )
        self.logger.debug( msg )
