import uuid


class OutgoingSession:
    def __init__(self):
        self.id=uuid.uuid1().hex
        self.incoming_session_id = None
        self.client_ip=None
        self.rtp_port=None
        self.rtcp_port=None
        self.server_rtp_port=None
        self.server_rtcp_port=None
        self.status=0
        self.protocol=None
        self.request_stream_session_id=None

    def __str__(self):
        return (f"id={self.id}, incoming_session_id:{self.incoming_session_id}, client_ip:{self.client_ip}, rtp_port:{self.rtp_port}, "
                f"rtcp_port:{self.rtcp_port}, server_rtp_port:{self.server_rtp_port}, server_rtcp_port:{self.server_rtcp_port}, status:{self.status}, "
                f"protocol:{self.protocol}, request_stream_session_id:{self.request_stream_session_id}")