from server.chat_server import ChatServer
from aiohttp import web
from remote_apis.rest_api.rest_handlers import Handlers


class RestApp:

    def __init__(self, chat_server: ChatServer, port, loop):
        self.chat_server = chat_server
        self.port = port
        self.handlers = Handlers(chat_server=chat_server)
        self.loop = loop

        self.app = web.Application(loop=loop)
        self.app.router.add_routes([web.get('/rooms', self.handlers.get_rooms),
                                    web.get('/users', self.handlers.get_users)])


    def start(self):
        print('starting REST API server at {}'.format(self.port))
        site = self.app.make_handler()
        coro = self.loop.create_server(site, '0.0.0.0', self.port)
        self.loop.run_until_complete(coro)
