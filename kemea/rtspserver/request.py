class Request:
    def __init__(self):
        self.method = None
        self.addr = None
        self.protocol = None
        self.headers = dict()
        self.body=b''
        self.client_ip=None
        self.client_port=None

    def add_header(self, header_line):
        if header_line is None:
            return
        name_value=header_line.split(':')
        if len(name_value) > 1:
            self.headers[name_value[0]] = name_value[1].strip().capitalize() if name_value[1] else ''

    def is_request_complete(self):
        if self.method is None or self.method=='':
            return False
        if self.addr is None or self.addr=='':
            return False
        if self.headers is not None and 'Content-Length' in self.headers and (self.body is None or self.body==''):
            return False
        return True

    def __str__(self):
        return f'Request {self.method} {self.addr} {self.protocol} {self.headers} {self.body}'

