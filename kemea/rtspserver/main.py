import atexit
import socket

from kemea.rtspserver import serverinfo
from kemea.rtspserver.listener import Listener
from kemea.rtspserver.util.logger import applogger

serverinfo.HOST=socket.gethostbyname(socket.getfqdn())
def cleanup():
    applogger.info('Closing RTSP Server')

atexit.register(cleanup)
listener=Listener(serverinfo.HOST, serverinfo.PORT)
listener.listen()