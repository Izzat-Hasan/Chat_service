import asyncio
from server.chat_server import ChatServer


class ChatServerProtocol(asyncio.Protocol):

    def __init__(self, chat_server: ChatServer):
        self._pieces = []
        self.server = chat_server

    def _handle_command(self):
        command = ''.join(self._pieces)
        self._pieces = []

        if command.startswith('/lru'):
            # get list of registered users

            lru = self.server.lru()
            response = '/lru '
            for user in lru:
                response += (f'{user}, ')

            response.rstrip(', ')
            response = ''.join([response, '$'])
            self._transport.write(response.encode('utf-8'))

        elif command.startswith('/login '):
            # TODO: check if login-name already exists
            # TODO: what to do when already logged-in

            login_name = command.lstrip('/login').rstrip('$').strip()
            try:
                self.server.login(login_name=login_name, transport=self._transport)
                response = '/login success$'
            except:
                response = '/login already exists$'

            self._transport.write(response.encode('utf-8'))


        elif command.startswith('/lrooms '):
            # response format
            # /lroom public&system&public room\nroom1&omari&room to discuss chat service impl$
            rooms = self.server.l_rooms()

            room_msgs = ['{}&{}&{}'.format(r['name'], r['owner'], r['description']) for r in rooms]
            response = '/lrooms {}$'.format('\n'.join(room_msgs))
            self._transport.write(response.encode('utf-8'))

        elif command.startswith('/post '):
            # expected request format: /post public&hello everyone
            room, msg = command.lstrip('/post').rstrip('$').split('&')
            self.server.post_msg(room=room.strip(), msg=msg)

    def connection_made(self, transport: asyncio.Transport):
        """Called on new client connections"""
        self._remote_addr = transport.get_extra_info('peername')
        self._transport = transport
        print('[+] client {} connected.'.format(self._remote_addr))
        self.server.add_client(transport=transport)

    def data_received(self, data):
        """Handle data"""
        self._pieces.append(data.decode('utf-8'))
        if ''.join(self._pieces).endswith('$'):
            self._handle_command()

    def connection_lost(self, exc):
        """remote closed connection"""
        print('[-] lost connectio to {}'.format(self._remote_addr))
        self.server.remove_client(transport=self._transport)
        self._transport.close()


class TCPChatServer:
    LOCAL_HOST = '0.0.0.0'

    def __init__(self, port, chat_server: ChatServer, loop):
        self.chat_server = chat_server
        self._port: int = port
        self.loop = loop

    def listen(self):
        """start listening"""
        pass

    def start(self):
        """start"""
        print('starting TCP API server at {}'.format(self._port))

        server_coro = self.loop.create_server(lambda: ChatServerProtocol(self.chat_server),
                                              host=TCPChatServer.LOCAL_HOST,
                                              port=self._port)

        self.loop.run_until_complete(server_coro)


if __name__ == '__main__':
    chat_server = TCPChatServer(port=8080)
    chat_server.start()
