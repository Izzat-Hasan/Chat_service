class ChatServer:
    def __init__(self):
        # master dict {transport: {'remote': ('127.0.0.1', 76678), 'login-name': 'omari', 'rooms': [public, room1]}
        self.clients = {}
        self.rooms = [{'name': 'public',
                       'owner': 'system',
                       'description': 'The public room which acts as broadcast, all logged-in users are in public room by default'}
                      ]

    def lru(self):
        lru = [r['login-name'] for r in self.clients.values() if r['login-name']]
        return lru

    def login(self, login_name, transport):
        all_login_names = [v['login-name'] for v in self.clients.values()]
        if login_name in all_login_names:
            raise Exception()

        client_record = self.clients[transport]
        client_record['login-name'] = login_name

    def add_client(self, transport):
        self._remote_addr = transport.get_extra_info('peername')
        self.clients[transport] = {'remote': self._remote_addr, 'login-name': None, 'rooms': ['public']}

    def remove_client(self, transport):
        del self.clients[transport]

    def l_rooms(self):
        return self.rooms

    def post_msg(self, room, msg):

        transports = [k for k, v in self.clients.items() if room in v['rooms']]

        msg_to_send = '/MSG {}$'.format(msg)
        for transport in transports:
            transport.write(msg_to_send.encode('utf-8'))
