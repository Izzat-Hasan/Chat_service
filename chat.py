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
        sender, msg = (await chat_client.get_user_msg()).split('&')
        print('\n\n\t\tRECEIVED MESSAGE FROM {}: {}'.format(sender, msg))


async def handle_user_input(chat_client, loop):
    while True:
        print('\n\n')
        print('< 1 > closes connection and quits')
        print('< 2 > list logged-in users')
        print('< 3 > login')
        print('< 4 > list rooms')
        print('< 5 > post message to a room')
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
                room_choice = await aioconsole.ainput('enter the room you want to post a message to: ')
                if room_choice:
                    user_message = await aioconsole.ainput('enter your message: ')
                    await chat_client.post(user_message, room_choice)
                else:
                    print('Room name does not exist.')
            except Exception as e:
                print('error posting message {}'.format(e))

        elif command == '6':
            room_name = await aioconsole.ainput('enter room name: ')
            room_description = await aioconsole.ainput('enter room descriptions: ')
            special_characters = "!@#$%^&*())_+=|}{:?><[];' ,./,"

            try:
                if len(room_name) > 10 or any(c in special_characters for c in room_name):
                    print("error! you must enter a name less than 10 characters, with no spaces or special symbols.")
                    continue
                result = await chat_client.crooms(room_name, room_description)
                click.echo(result)

            except Exception as e:
                print('error, you are not logged in. Please log in and try again.')

        elif command == '7':
            room_name = await aioconsole.ainput('enter room name: ')
            result = await chat_client.join_room(room_name)
            click.echo(result)

        elif command == '8':
            room_name = await aioconsole.ainput('enter room name: ')
            result = await chat_client.leave_room(room_name)
            click.echo(result)

        elif command == '9':
            try:
                if not login_name:
                    print()
                else:
                    # grabs all users logged in
                    users = await chat_client.lru()
                    if not users:
                        print("There are no users online.")
                    else:
                        print("\n Select a user to message directly.")
                        usernumber = 0
                        # prints list of users and assigns a number to them
                        for u in users:
                            usernumber += 1
                            print(str(usernumber) + ") " + str(u))
                        dm_choice = await aioconsole.ainput("Choice: ")
                        # prints recipient to for clarity
                        recipient = users[int(dm_choice) - 1]
                        if recipient == login_name:
                            print("You can't DM yourself.")
                        else:
                            dm_message = await aioconsole.ainput("Enter your message: ")
                            result = await chat_client.dm(recipient, dm_message)
            except UnboundLocalError:
                print("You must be logged in to DM a user.")


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
