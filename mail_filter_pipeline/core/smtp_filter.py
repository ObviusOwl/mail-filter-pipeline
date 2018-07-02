from mail_filter_pipeline.filter_plugin import FilterPlugin

import smtplib
import logging

class SmtpFilter( FilterPlugin ):
    pluginName = "smtp"
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.host = None
        self.port = None

    def requireConfig(self, conf, key):
        if not key in conf:
            raise FilterRuntimeError("SMTP filter configuration key '{}' is mandatory".format(key) )
        return conf[ key ]

    def config( self, conf ):
        super().config(conf)
        myConf = conf.getPluginConfig()
        self.host = self.requireConfig( myConf, "host" )
        self.port = self.requireConfig( myConf, "port" )

    def run(self, message):
        assert self.host != None
        assert self.port != None

        msg = "SMTP submitted message (from={}, to={}) to host {}:{} , ".format(
            message.message["from"], message.message["to"], self.host, self.port
        )

        server = smtplib.SMTP( host=self.host, port=self.port)
        try:
            server.send_message( message.message )
            self.logger.debug( msg )
        finally:
            server.quit()
        
