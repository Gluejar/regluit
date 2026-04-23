import logging
import logging.handlers
import os

#https://stackoverflow.com/questions/28054864/use-fileconfig-to-configure-custom-handlers-in-python
logging.handlers = logging.handlers

#https://stackoverflow.com/questions/1407474/does-python-logging-handlers-rotatingfilehandler-allow-creation-of-a-group-writa
class GroupWriteRotatingFileHandler(logging.handlers.RotatingFileHandler):    
    def _open(self):
        prevumask = os.umask(0o002)
        #os.fdopen(os.open('/path/to/file', os.O_WRONLY, 0600))
        rtv = logging.handlers.RotatingFileHandler._open(self)
        os.umask(prevumask)
        return rtv
        
# for django, need to do this in settings
#logging.handlers.GroupWriteRotatingFileHandler = GroupWriteRotatingFileHandler
