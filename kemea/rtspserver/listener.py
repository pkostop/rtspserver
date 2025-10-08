import selectors
import socket
import types
from selectors import EVENT_READ, EVENT_WRITE
import traceback

from kemea.rtspserver.outgoingsessioninfo import OutgoingSession
from kemea.rtspserver.pull_request_handler import pull_request_handler
from kemea.rtspserver.Session import Session
from kemea.rtspserver.push_request_handler import push_request_handler
from kemea.rtspserver.request import Request
from kemea.rtspserver.incomingsessioninfo import IncomingSession
from kemea.rtspserver.util.logger import applogger

PAYLOAD_SIZE = 512
RTSP_ERROR_RESPONSE = 'HTTP/1.1 500 Internal Server Error\r\n\r\n'


def call_request_handler(request, session):
    if session.incoming_session_info is None and session.outgoing_session_info is None:
        build_session(request, session)
    if request.addr is not None and '/push' in request.addr:
        return push_request_handler(request,session.incoming_session_info)
    elif request.addr is not None and '/pull' in request.addr:
        return pull_request_handler(request,session.outgoing_session_info)
    return None

def build_session(request, session):
    if request.addr is not None and '/push' in request.addr:
        session.incoming_session_info=IncomingSession()
    elif request.addr is not None and 'pull' in request.addr:
        session.outgoing_session_info=OutgoingSession()

class Listener:
    def __init__(self, host, port):
        self.host=host
        self.port=port
        self.selector = selectors.DefaultSelector()
        applogger.info("Listening on %s:%d" % (host, port))

    def accept_connection(self, serversocket):
        connsocket, addr=serversocket.accept()
        connsocket.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=bytearray(), outb=bytearray(), request=Request(), session=Session(None, None))
        self.selector.register(connsocket, EVENT_READ|EVENT_WRITE, data=data)
        applogger.info(f'Accepted connection from {addr}')


    def parse_message(self, payload, request, connsocket):
        if payload is None:
            return None
        msg=payload.decode('ascii')
        lines=msg.split('\r\n')
        if len(lines) >= 0:
            request_line = lines[0]
            tokens = request_line.split(' ')
            if tokens and len(tokens) >= 0:
                request.method=tokens[0]
            if tokens and len(tokens) > 1:
                request.addr=tokens[1]
            if tokens and len(tokens) > 2:
                request.protocol=tokens[2]
        if len(lines) >= 1:
            lines=lines[1:]
            for i in range(0,len(lines)):
                if lines[i] == '':
                    request.body="\r\n".join(lines[i+1:len(lines)])
                    break
                request.add_header(lines[i])
        request.client_ip=connsocket.getpeername()[0]
        request.client_port = connsocket.getpeername()[1]
        return request

    def parse_body(self, payload, request):
        parts=payload.partition(b'\r\n\r\n')
        if parts and parts[2]:
            request.body+=parts[2]


    def service_connection(self, key, mask):
        connsocket = key.fileobj
        payload= None
        if mask & selectors.EVENT_READ:
            payload = connsocket.recv(PAYLOAD_SIZE)
            if payload:
                key.data.outb += payload
            else:
                self.close_connection_socket(connsocket)
        if mask & selectors.EVENT_WRITE:
            if key.data.outb:
                try:
                        self.parse_message(key.data.outb, key.data.request, connsocket)
                        if not key.data.request.is_request_complete():
                            applogger.info('incomplete')
                            key.data.request = Request()
                        else:
                            applogger.info(key.data.request)
                            response=call_request_handler(key.data.request, key.data.session)
                            applogger.info(f'response: {response}')
                            connsocket.sendall(response.encode('ascii'))
                            key.data.outb.clear()
                            key.data.request=Request()
                except Exception as e:
                    traceback.print_exc()
                    self.close_connection_socket(connsocket)

    def close_connection_socket(self, connsocket):
        self.selector.unregister(connsocket)
        connsocket.close()


    def is_request_body_received(request):
        return request.headers.get('CONTENT-LENGTH') is None or len(request.body) >= int(
            request.headers.get('CONTENT-LENGTH'))


    def are_headers_received(payload):
        return payload is not None and len(payload) > 0 and (payload.endswith(b'\r\n\r\n') or payload.endswith(b'\n\n'))


    def listen(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.host,self.port))
        serversocket.listen()
        serversocket.setblocking(False)
        self.selector.register(serversocket, EVENT_READ, data=None)
        applogger.info('The RTSP Server is up and running.')
        try:
            while True:
                events=None
                try:
                    events=self.selector.select(timeout=None)
                except (OSError, ValueError, TypeError) as e:
                    traceback.print_exc()
                key=None
                try:
                    for key, event in events:
                        if key.data is None:
                            self.accept_connection(key.fileobj)
                        else:
                            self.service_connection(key, event)
                except OSError as e:
                    traceback.print_exc()
                    self.close_connection_socket(key.fileobj)
        except KeyboardInterrupt:
            applogger.error('Exiting RTSP Server')
        finally:
            self.selector.close()
            serversocket.close()


