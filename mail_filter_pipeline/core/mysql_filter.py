from mail_filter_pipeline.filter_plugin import FilterPlugin
from mail_filter_pipeline.errors import FilterRuntimeError

import logging
import re
import datetime
import email
import mysql.connector

# TODO: make configurable which columns should be inserted

class MysqlFilter( FilterPlugin ):
    pluginName = "mysql"
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.host = None
        self.port = 3306
        self.user = None
        self.password = None
        self.database = None
        self.table = None
        self.dateReg = re.compile("\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s\d{2}:\d{2}(?::\d{2})\s+[+-]\d{4}")

    def requireConfig(self, conf, key):
        if not key in conf:
            raise FilterRuntimeError("MYSQL filter configuration key '{}' is mandatory".format(key) )
        return conf[ key ]

    def getConfig(self, conf, key, fallback):
        if key in conf:
            return conf[ key ]
        return fallback

    def config( self, conf ):
        super().config(conf)
        myConf = conf.getPluginConfig()
        self.host     = self.requireConfig( myConf, "host")
        self.port     = self.getConfig(     myConf, "port", self.port )
        self.user     = self.requireConfig( myConf, "user")
        self.password = self.requireConfig( myConf, "password")
        self.database = self.requireConfig( myConf, "database")
        self.table    = self.requireConfig( myConf, "table")
        
    def guessReceivedDate(self, msg ):
        r = msg.get_all("Received")
        if len(r) == 0:
            return None
        r = r[0]
        m = self.dateReg.search( r )
        if m == None:
            return None
        d = None
        try:
            d = email.utils.parsedate_to_datetime( m.group(0) )
        finally:
            return d
    
    def getSendDate( self, msg ):
        d = None
        try:
            d = email.utils.parsedate_to_datetime( msg["Date"] )
        finally:
            return d
            
    def getBody(self, msg ):
        body = None
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str( part.get('Content-Disposition') )
                # skip any text/plain (txt) attachments
                if ctype.startswith("text/") and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True).decode()  # decode
                    break
        # not multipart
        else:
            body = msg.get_payload(decode=True).decode()
        return body

    def run(self, message):
        assert self.host != None
        assert self.port != None
        assert self.user != None
        assert self.password != None
        assert self.database != None
        assert self.table != None

        dbgMsg = "saved message to MSQL from={}, to={}, db={}:{}/{}/{}".format(
            message.message.get("From",None), message.message.get("To",None), 
            self.host, self.port, self.database, self.table
        )
        stm = ("INSERT INTO `{}` "
               "(message, date, last_received, from_address, to_address, subject, body, filter_date)"
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
        ).format( self.table )
        msgID = message.message.get("Message-ID",None)
        
        sendDate = self.getSendDate( message.message )
        recDate = self.guessReceivedDate( message.message )
        # Note: parsing failure results in None value, which translates to NULL in SQL
        sendDateStr = None
        recDateStr = None

        if sendDate == None:
            self.logger.error( "Failed to parse 'date:' header, msgID={}".format( msgID ) )
        else:
            sendDateStr = sendDate.strftime('%Y-%m-%d %H:%M:%S')
        if recDate == None:
            self.logger.error( "Failed to parse last 'Received:' header, msgID={}".format( msgID ) )
        else:
            recDateStr = recDate.strftime('%Y-%m-%d %H:%M:%S')
            
        data = ( 
            message.message.as_string(),
            sendDate, recDate,
            message.message.get("From",None),
            message.message.get("To",None),
            message.message.get("Subject",None),
            self.getBody(message.message),
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        myConn = None
        try:
            myConn = mysql.connector.connect(user=self.user, password=self.password,
                                          host=self.host, database=self.database)
            myCur = myConn.cursor(buffered=True)
            myCur.execute( stm, data )
            myConn.commit()
        finally:
            if myConn != None:
                myConn.close()
            
        self.logger.debug( dbgMsg )
