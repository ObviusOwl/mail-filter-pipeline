from mail_filter_pipeline.filter_plugin import FilterPlugin

import smtplib
import logging

class SmtpFilter( FilterPlugin ):
    pluginName = "smtp"
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.host = "localhost"
        self.port = 25
        
    def config( self, conf ):
        super().config(conf)
        myConf = conf.getPluginConfig()
        if "host" in myConf:
            self.host = myConf["host"]
        if "port" in myConf:
            self.port = myConf["port"]

    def run(self, message):
        msg = "sending message with SMTP from={}, to={}, host={}:{}".format(
            message.message["from"], message.message["to"], self.host, self.port
        )
        self.logger.debug( msg )

        server = smtplib.SMTP( host=self.host, port=self.port)
        try:
            server.send_message( message.message )
        finally:
            server.quit()
        
