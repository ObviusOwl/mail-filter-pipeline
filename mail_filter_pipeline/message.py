
class Message( object ):

    def __init__(self):
        self.originalMessage = None
        self.message = None
        self.sourceName = ""
        self.data = {}
    
    def fromMessage(self, msg):
        self.originalMessage = msg.as_string()
        self.message = msg
    
    def setSourceName(self, name ):
        self.sourceName = name

    def getSourceName(self):
        return self.sourceName
