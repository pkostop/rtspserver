from kemea.rtspserver.streams import streams
from kemea.rtspserver.util.atomic_counter import AtomicCounter
from kemea.rtspserver.util.logger import applogger

SERVER_PORT_COUNTER=AtomicCounter(10000)

def options(request, session):
    session.client_ip=request.client_ip
    return "RTSP/1.0 200 OK\r\nCSeq: 1\r\nPublic: OPTIONS, ANNOUNCE, SETUP, RECORD, TEARDOWN\r\nServer: KEMEA RTSP SERVER/1.0\r\n\r\n"

def announce(request, session):
    session.sdp=request.body
    if request.headers['CSeq']:
        return f"RTSP/1.0 200 OK\r\nCSeq: {request.headers['CSeq']}\r\nSession: 1234567\r\n\r\n"
    else:
        return f"RTSP/1.0 200 OK\r\nCSeq: 1\r\nSession: 1234567\r\n\r\n"

def setup(request, session):
    tokens=request.headers['Transport'].split(';')
    session.setup_prot=tokens[0]
    session.server_rtp_port=SERVER_PORT_COUNTER.increment()
    session.server_rtcp_port = session.server_rtp_port+1
    if tokens[2]:
        subtokens=get_value(tokens[2]).split('-')
        session.rtp_port=int(subtokens[0].strip())
        session.rtcp_port = int(subtokens[1].strip())

    session.setup_mode=get_value(tokens[3])

    if request.headers['CSeq']:
        return f"RTSP/1.0 200 OK\r\nCSeq: {request.headers['CSeq']}\r\nTransport: RTP/AVP;unicast;client_port= {session.rtp_port}-{session.rtcp_port};server_port={session.server_rtp_port}-{session.server_rtcp_port};ssrc=1234\r\nSession: {session.id}\r\n\r\n"
    else:
        return f"RTSP/1.0 200 OK\r\nCSeq: 1\r\n"


def record(request, session):
    session.status=1
    streams[session.id]=session
    print(f"session {session.id} is established")
    print(f"session info: {session}")
    return f"RTSP/1.0 200 OK\r\nCSeq: {request.headers['CSeq']}\r\nSession: {session.id}\r\n\r\n"


def push_request_handler(request, session):
    if request and request.method:
        if request.method == 'ANNOUNCE':
            return announce(request, session)
        if request.method == 'DESCRIBE':
            pass
        if request.method == 'GET_PARAMETER':
            pass
        if request.method == 'OPTIONS':
            return options(request, session)
        if request.method == 'PAUSE':
            pass
        if request.method == 'PLAY':
            pass
        if request.method == 'PLAY_NOTIFY':
            pass
        if request.method == 'REDIRECT':
            pass
        if request.method == 'SETUP':
            return setup(request, session)
        if request.method == 'SET_PARAMETER':
            pass
        if request.method == 'RECORD':
            return record(request, session)
        if request.method == 'TEARDOWN':
            pass
    return 'RTSP/1.0 200 OK'

def get_value(val):
    if val:
        tokens=val.split('=')
        if tokens and len(tokens)>1:
            return tokens[1]
    return ''
