import email
import logging
import queue
import aiosmtpd.controller
import aiosmtpd.handlers

from mail_filter_pipeline.input_plugin import InputPlugin
import mail_filter_pipeline.message

class SmtpInputHandler( aiosmtpd.handlers.Message ):
    
    def __init__(self, inPlugin):
        super().__init__()
        self.plugin = inPlugin
        self.logger = logging.getLogger(__name__)

    async def handle_DATA(self, server, session, envelope):
        # If the server was created with decode_data True, then data will be a
        # str, otherwise it will be bytes.
        data = envelope.content
        if isinstance(data, bytes):
            message = email.message_from_bytes(data, self.message_class)
        else:
            assert isinstance(data, str), ( 'Expected str or bytes, got {}'.format(type(data)))
            message = email.message_from_string(data, self.message_class)
        self.logger.debug( "got message from SMTP: from={}, to={}".format(message["from"], message["to"]) )

        msg = mail_filter_pipeline.message.Message()
        msg.fromMessage( message )
        msg.setSourceName( self.plugin.name )

        try:
            self.plugin.mailQueue.put( msg, block=True, timeout=self.plugin.queueTimeout )
        except queue.Full:
            return '451 Mail queue full'
        return '250 OK'

class SmtpInput( InputPlugin ):
    pluginName = "smtp"
    
    def __init__(self, mailQueue):
        super().__init__( mailQueue )
        self.controller = None
        self.port = 8025
        self.host = "localhost"
        self.queueTimeout = 5
    
    def start( self ):
        self.controller = aiosmtpd.controller.Controller( 
            SmtpInputHandler(self), port=self.port, hostname=self.host )
        self.controller.start()
        self.logger.debug( "started smtp input plugin named '{}'".format(self.name) )
        
    def stop( self ):
        if self.controller != None:
            self.controller.stop()
        self.logger.debug( "stopped smtp input plugin named '{}'".format(self.name) )
        
    def config( self, cnf ):
        # TODO: type checking & warn
        if "port" in cnf:
            self.port = int(cnf["port"])
        if "host" in cnf:
            self.host = cnf["host"]
        if "queue_timeout" in cnf:
            self.queueTimeout = cnf["queue_timeout"]

