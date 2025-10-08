class Session:
    def __init__(self, incoming_session_info, outgoing_session_info):
        self.incoming_session_info=incoming_session_info
        self.outgoing_session_info=outgoing_session_info

    def __str__(self):
        return  self.incoming_session_info.__str__() if self.incoming_session_info is not None else self.outgoing_session_info.__str__()


