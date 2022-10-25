import json
from aiohttp import web
from server.chat_server import ChatServer

class Handlers:
    def __init__(self, chat_server: ChatServer):
        self.chat_server = chat_server


    async def get_rooms(self, request):
        rooms = self.chat_server.l_rooms()
        return web.json_response(rooms)

    async def get_users(self, request):
        users = self.chat_server.lru()
        return web.json_response(users)