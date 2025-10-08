import uuid


class IncomingSession:
    def __init__(self):
        self.id=uuid.uuid1().hex
        self.sdp=None
        self.client_ip=None
        self.rtp_port=None
        self.rtcp_port=None
        self.setup_prot=None
        self.setup_mode=None
        self.server_rtp_port=None
        self.server_rtcp_port=None
        self.ssrc=None
        self.status=0

    def __str__(self):
        return (f"IncomingSession(id={self.id}, sdp={self.sdp}, client_ip={self.client_ip}, rtp_post={self.rtp_port}, "
                f"rtcp_port={self.rtcp_port}, setup_prot={self.setup_prot}, setup_mode={self.setup_mode}, server_rtp_port={self.server_rtp_port}, server_rtcp_port={self.server_rtcp_port}, "
                f"ssrc={self.ssrc}, status={self.status})")

