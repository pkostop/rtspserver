import subprocess
import os
from pathlib import Path

from kemea.rtspserver import serverinfo
from kemea.rtspserver.streams import streams
from kemea.rtspserver.util.atomic_counter import AtomicCounter


SERVER_PORT_COUNTER=AtomicCounter(11000)

def options(request, session):
    session.client_ip = request.client_ip
    return f"RTSP/1.0 200 OK\r\nCSeq: {request.headers['CSeq']}\r\nPublic: DESCRIBE, SETUP, TEARDOWN, PLAY, PAUSE, OPTIONS\r\nServer: KEMEA RTSP SERVER/1.0\r\n\r\n"


def describe(request, session):
    sdp=None
    if request.addr is not None:
        tokens=request.addr.split('/')
        if tokens and len(tokens)>=5:
            sessionId=tokens[4]
            sdp=streams[sessionId].sdp
            session.request_stream_session_id=sessionId
    stream=streams[session.request_stream_session_id]
    if "video 0" in sdp:
        sdp=sdp.replace("video 0", f"video {stream.server_rtp_port}")

    return f"RTSP/1.0 200 OK\r\nCSeq: 2\r\nContent-Type: application/sdp\r\nContent-Length: {len(sdp)}\r\n\r\n{sdp}"

def setup(request, session):
    if request.headers['Transport']:
        tokens=request.headers['Transport'].split(';')
        if tokens and len(tokens)>=1:
            session.protocol=tokens[0]
        if tokens and len(tokens)>=2:
            if '=' in tokens[2]:
                ports=tokens[2].split('=')[1]
                if '-' in ports:
                    session.rtp_port=ports.split('-')[0]
                    session.rtcp_port = ports.split('-')[1]
    if session.rtp_port and session.rtp_port:
        session.server_rtp_port=SERVER_PORT_COUNTER.increment()
        session.server_rtcp_port = SERVER_PORT_COUNTER.increment()
    print(f"pull session info {session}")
    return f"RTSP/1.0 200 OK\r\nCSeq: 3\r\nTransport: RTP/AVP;unicast;client_port={session.rtp_port}-{session.rtcp_port}\r\nSession: {session.id}\r\n\r\n"


def start_relaying(stream, outgoing_session):
    sdp_file_path=f"{Path.home()}\\kemea-rtsp-server\\{stream.id}.sdp"
    os.makedirs(f"{Path.home()}/kemea-rtsp-server", exist_ok=True)
    sdp=stream.sdp
    if "video 0" in sdp:
        sdp=sdp.replace("video 0", f"video {stream.server_rtp_port}")
    with open(sdp_file_path, "w") as f:
        f.write(sdp)
    cmd=f"ffmpeg -protocol_whitelist file,tcp,udp,rtp -i {sdp_file_path} -c copy -f rtp rtp://{serverinfo.HOST}:{outgoing_session.rtp_port}"
    print(cmd)
    subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def play(request, session):
    if streams[session.request_stream_session_id]:
        start_relaying(streams[session.request_stream_session_id], session)

    return f"RTSP/1.0 200 OK\r\nCSeq: 4\r\nSession: {session.id}\r\nRTP-Info: url=rtsp://{serverinfo.HOST}:{serverinfo.PORT}/pull/trackID=1;seq=0;rtptime=0\r\n\r\n"


def teardown(request, session):
    pass


def pull_request_handler(request, session):
    if request and request.method:
        if request.method == 'ANNOUNCE':
            pass
        if request.method == 'DESCRIBE':
            return describe(request, session)
        if request.method == 'GET_PARAMETER':
            pass
        if request.method == 'OPTIONS':
            return options(request,session)
        if request.method == 'PAUSE':
            pass
        if request.method == 'PLAY':
            return play(request, session)
        if request.method == 'PLAY_NOTIFY':
            pass
        if request.method == 'REDIRECT':
            pass
        if request.method == 'SETUP':
            return setup(request,session)
        if request.method == 'SET_PARAMETER':
            pass
        if request.method == 'RECORD':
            pass
        if request.method == 'TEARDOWN':
            return teardown(request,session)
    return 'RTSP/1.0 200 OK'
