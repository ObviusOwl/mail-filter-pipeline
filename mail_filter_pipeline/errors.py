
class ConfigError( Exception ):
    def __init__(self, fileName, message):
        super().__init__(self, message)
        self.fileName = fileName

class FilterRuntimeError( Exception ):
    def __init__(self, message):
        super().__init__(self, message)
