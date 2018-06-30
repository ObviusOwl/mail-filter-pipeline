import logging
import threading

class PipelineExecutor( threading.Thread ):
    
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.daemon = True
        self.logger = logging.getLogger(__name__)
        self.start()
    
    def run(self):
        while True:
            pipeline = self.queue.get( block=True )
            try:
                self.logger.debug( "initialising pipeline filters" )
                pipeline.initFilters()
                self.logger.debug( "begin pipeline run" )
                pipeline.run()
                self.logger.debug( "end pipeline run" )
            except Exception as e:
                self.logger.exception("Pipeline failed with exception")
            finally:
                self.queue.task_done()
