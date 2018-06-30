from mail_filter_pipeline.filter_plugin import FilterPlugin

import logging

class DebugFilter( FilterPlugin ):
    pluginName = "debug"
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def config( self, conf ):
        super().config(conf)
        self.logger.debug( str(conf.getPluginConfig()) )

    def run(self, message):
        msg = "--- begin email ---\n {} \n--- end email ---\n"
        self.logger.debug( msg.format( str(message.message) ) )
