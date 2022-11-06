import aioconsole
import asyncio
import click

from server.chat_server import ChatServer
from client.chat_client import (
    ChatClient,
    NotConnectedError,
    LoginConflictError,
    LoginError
)


async def display_msgs(chat_client):
    while True:
        msg = await chat_client.get_user_msg()
        print('\n\n\t\tRECEIVED MESSAGE: {}'.format(msg))


async def handle_user_input(chat_client, loop):
    while True:
        print('\n\n')
        print('< 1 > closes connection and quits')
        print('< 2 > list logged-in users')
        print('< 3 > login')
        print('< 4 > list rooms')
        print('< 5 > post message to a room')
        # For the time being, I put these here for visibility's sake, do not input these options - Andrew
        print('< 6 > create private room')
        print('< 7 > join private room')
        print('< 8 > leave room')
        print('< 9 > DM another user')


        print('\tchoice: ', end='', flush=True)

        command = await aioconsole.ainput()
        if command == '1':
            # disconnect
            try:
                chat_client.disconnect()
                print('disconnected')
                loop.stop()
            except NotConnectedError:
                print('client is not connected ...')
            except Exception as e:
                print('error disconnecting {}'.format(e))

        elif command == '2':  # list registered users
            users = await chat_client.lru()
            print('logged-in users: {}'.format(', '.join(users)))

        elif command == '3':
            login_name = await aioconsole.ainput('enter login-name: ')
            try:
                await chat_client.login(login_name)
                print(f'logged-in as {login_name}')

            except LoginConflictError:
                print('login name already exists, pick another name')
            except LoginError:
                print('error logging in, try again')

        elif command == '4':
            try:
                rooms = await chat_client.lrooms()
                for room in rooms:
                    print('\n\t\troom name ({}), owner ({}): {}'.format(room['name'], room['owner'], room['description']))

            except Exception as e:
                print('error getting rooms from server {}'.format(e))

        elif command == '5':
            try:
                user_message = await aioconsole.ainput('enter your message: ')
                await chat_client.post(user_message, 'public')

            except Exception as e:
                print('error posting message {}'.format(e))

        # I added the other option's skeletons below
        # I have an idea that once we get the main "create room" function done
        # I say we can divide and conquer these remaining 3 if that sounds like
        # a good idea to y'all. - Andrew

        elif command == '6':
            special_characters = "!@#$%^&*())_+=|}{:?><[];',./,"
            room_info = await aioconsole.ainput('enter room name, owner, and descriptions separated by &: ')
            parts = room_info.split("&")
            room_name = parts[0]

            try:
                if len(room_name) > 10 or any(c in special_characters for c in room_name):
                    print("error! you must enter a name less than 10 characters with no special symbols")
                    break
                result = await chat_client.crooms(room_info)
                print(f'created room: {result}')

            except Exception as e:
                print('error')

        elif command == '9':
            try:
                # grabs all users logged in
                users = await chat_client.lru()
                print("\n Select a user to message directly.")
                usernumber = 0
                # prints list of users and assigns a number to them
                for u in users:
                    usernumber += 1
                    print(str(usernumber) + ") " + str(u))
                dm_choice = await aioconsole.ainput("Choice: ")
                # prints recipient to for clarity
                recipient = users[int(dm_choice) - 1]
                print(f'Recipient: {recipient}')
                dm_message = await aioconsole.ainput("Enter your message: ")
                # Right now this just is basically posting to the public room. It is a placeholder until I figure
                # out the right way to send a message to a person directly. I noticed in the connections there is
                # a unique number, which could be the answer to this problem, but I haven't found out the
                # correct way to call it yet.
                print(f"Message from {login_name}:")
                await chat_client.post(dm_message, 'public')

            except Exception as e:
                print("error")





        '''elif command == '7':
                    try:
                        # code for when created room is joinable
                    except Exception as e:
                        # error code for when you are either already in a room, or if it doesn't exist'''

        '''elif command == '8':
                    try:
                        # code for leaving private room
                    except Exception as e:
                        # error code for when you are not in a private room (also for trying to leave the
                        public room, as you can simply leave that by logging out using option 1)'''




@click.group()
def cli():
    pass


@cli.command(help="run chat client")
@click.argument("host")
@click.argument("port", type=int)
def connect(host, port):
    chat_client = ChatClient(ip=host, port=port)
    loop = asyncio.get_event_loop()

    loop.run_until_complete(chat_client._connect())

    # display menu, wait for command from user, invoke method on client
    asyncio.ensure_future(handle_user_input(chat_client=chat_client, loop=loop))
    asyncio.ensure_future(display_msgs(chat_client=chat_client))

    loop.run_forever()


@cli.command(help='run chat server')
@click.argument('port', type=int)
def listen(port):
    click.echo('starting chat server at {}'.format(port))
    chat_server = ChatServer(port=port)
    chat_server.start()


if __name__ == '__main__':
    cli()