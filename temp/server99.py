# 99server.py
import os
from tempfile import TemporaryDirectory
import sys
import socket
from socket import SHUT_RDWR
import threading
import json
import copy
from random import shuffle
from list99 import master_list
from get_local_info import get_os # get_ip


class Server():
    '''A class to store a connection - a server socket and pertinent information'''

    def __init__(self):

        self.host_ip = 20.161.81.66
        self.host_os = get_os()

        self.initialize_socket()
        self.initialize_game()

    def initialize_socket(self):
        print(f'Server starting on {self.host_ip}')
        self.host_port = 80  # unused port 6812
        # self.host_addr is the tuple needed for binding socket to server (Windows)
        self.host_addr = (self.host_ip, self.host_port)
        # print(f'self.host_addr is: {self.host_addr}')
        self.socket_path = './socketpath'

        if os.path.exists(self.socket_path):
            os.rmdir(self.socket_path)

        os.mkdir(self.socket_path)

        self.encoder = 'utf-8'
        self.bytesize = 2048
        self.buffer = 1024
        self.header = 32

    def initialize_game(self):
        self.client_sockets = []
        self.client_ips = []
        # self.cards = []
        self.players = []
        self.current_player = 0
        self.player1 = ''
        self.player2 = ''
        self.player3 = ''
        self.game_winner = ''
        self.game_list = copy.deepcopy(master_list)

        self.cards = [str(i) for i in range(100)]

        shuffle(self.cards)

    def start(self):
        print(f'Host OS: {self.host_os}')
        # create the socket
        if self.host_os == "win32":
            self.host_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            # Check whether socket exists
            try:
                self.host_socket.bind((self.host_addr))

            except (OSError):
                print(f'exception to host_socket.bind: {OSError}')
                self.host_socket.connect((self.host_addr))
                self.host_socket.shutdown(SHUT_RDWR)
                self.host_socket.close()
                os._exit(0)

            else:
                # Create a thread to continously listen for connections and accept them
                print(f'Creating listen_thread.')
                listen_thread = threading.Thread(target=self.listening)
                listen_thread.start()

        else:
            # Linux system sockets
            self.host_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            # print(f'Socket object: {dir(self.host_socket)}')
            print(f'self.host_addr: {self.host_addr}')

            # # Check whether socket exists
            try:
                self.host_socket.bind((self.host_addr))

            except (OSError):
                print(f'exception to host_socket.bind: {OSError}')
                # self.host_socket.connect(self.socket_path)
                # self.host_socket.shutdown(SHUT_RDWR)
                self.host_socket.close()
                os._exit(0)

            else:
                # Create a thread to continously listen for connections and accept them
                print(f'Creating listen_thread.')
                listen_thread = threading.Thread(target=self.listening)
                listen_thread.start()
                # self.host_socket.close()
                # os._exit(0)

        # self.host_socket.bind((self.host_addr))

        # # Create a thread to continously listen for connections and accept them
        # listen_thread = threading.Thread(target=self.listening)
        # listen_thread.start()

        # # Add 'try' block to check whether socket exists
        # try:
        #     self.host_socket.bind(self.host_addr)

        # except (OSError):
        #     print(f'exception to host_socket.bind: {OSError}')
        #     self.host_socket.connect((self.host_addr))
        #     self.host_socket.shutdown(SHUT_RDWR)
        #     self.host_socket.close()
        #     os._exit(0)

    def stop(self):
        '''Begin the process of ending the server'''
        # Alert all users that the server is closing
        print(f'List of players has {len(self.players)} entries')
        message_json = self.create_message(
            'DISCONNECT', 'Admin (broadcast)', message='Server is closing...')
        self.broadcast_message(message_json)

        try:
            self.host_socket.shutdown(socket.SHUT_RDWR)

        except (OSError):  # [WinError 10057]
            # history_listbox.insert(
            #     0, f'[ENDING] Server has no connections.  Socket closes on app exit.')
            print(
                'Server exited because no connections were active while stopping.  PLEASE RESTART THE SERVER.')
            os._exit(0)
            # sys.exit()
        else:
            self.host_socket.close()

        # end_button.config(state=DISABLED)
        # start_button.config(state=NORMAL)

    def listening(self):
        '''Connect an incoming client to the server'''

        self.host_socket.listen()
        # history_listbox.insert(
        #     0, f'[LISTENING] Server is listening for IPv4 connections')

        while True:
            client_socket, client_addr = self.host_socket.accept()
            # This (blocks) waits for a new connection to the server.  When it does the address+port will be stored in addr,
            # and client_socket is a socket object to send information back to the client.
            thread = threading.Thread(
                target=self.new_connection, args=(client_socket, client_addr))
            thread.start()
            threading.enumerate()
            print(f'Active client connections: {threading.active_count() - 2}')
            self.client_sockets.append(client_socket)
            self.client_ips.append(client_addr[0])

    # new_connection runs once for each connected client in its own thread
    def new_connection(self, client_socket, client_addr):
        # history_listbox.insert(
        #     0, f'[NEW CONNECTION] Someone connected from {client_addr[0]}.')
        connected = True
        print(
            f'Begin new_connection while loop to receive from {client_addr[0]}')
        while connected:
            try:
                # tells us how long the msg is that's coming - the header
                msg_length = client_socket.recv(
                    self.header).decode(self.encoder)
            except (OSError):
                print('From new_connection: Client socket not detected.')
                connected = False
                break
            else:
                if msg_length:
                    msg_length = int(msg_length)
                    msg = client_socket.recv(msg_length).decode(self.encoder)
                    # print(f'Received from [{client_addr}] {msg}')
                    # if msg == 'SEEK':
                    #     client_socket.send('FOUND')
                    #     return
                    self.process_message(msg, client_socket, client_addr)
            try:
                # tells us how long the msg is that's coming - the header
                msg_length = client_socket.recv(
                    self.header).decode(self.encoder)
            except (OSError):
                print('From new_connection: Client socket not detected.')
                connected = False
                break
            else:
                if msg_length:
                    msg_length = int(msg_length)
                    msg = client_socket.recv(msg_length).decode(self.encoder)
                    # print(f'Received from [{client_addr}] {msg}')
                    # if msg == 'SEEK':
                    #     client_socket.send('FOUND')
                    #     return
                    self.process_message(msg, client_socket, client_addr)

    def next_turn(self):
        print(
            f'NEXT_TURN EXECUTING: Current player is {self.current_player}, game.winner: {self.game_winner}')
        count = len(self.players)
        if self.current_player == count:
            next_player = 1
        else:
            next_player = self.current_player + 1
        print(f'Next player return value is {next_player}')

        return next_player

    # create_message requires 4 positional arguments, up to 6 key word arguments
    def create_message(self, flag, player_name, message, tile_no='', player_id='', new_card='', card_played='', game_over=False, next_player='', player1='', player2='', player3=''):
        '''Return a message packet JSON to be sent'''
        message_packet = {
            'flag': flag,
            'player_name': player_name,
            'message': message,
            'tile_no': tile_no,
            'player_id': player_id,
            'new_card': new_card,
            'card_played': card_played,
            'game_over': game_over,
            'next_player': next_player,
            'player1': player1,
            'player2': player2,
            'player3': player3
        }

        message_json = json.dumps(message_packet)
        return message_json

    def send(self, message_json, client_socket):
        '''Send a message to the server'''
        message = message_json.encode(self.encoder)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.encoder)
        # adds spaces (in binary) to pad the message to header length
        send_length += b' ' * (self.header - len(send_length))
        # Add try - except here
        try:
            client_socket.send(send_length)
        except:
            print('   Exception: send message length')
        else:
            try:
                client_socket.send(message)
            except:
                print(f'  Exception: send message to {self.client_ips}\n')

    def private_message(self, message_json, client_socket):
        self.send(message_json, client_socket)

    def broadcast_message(self, message_json):
        '''Send a message to all client sockets connected to the server...ALL JSON ARE ENCODED'''
        print(
            f'broadcast_message to {len(self.players)} players')
        # print(
        # f'broadcast_message to {len(self.players)} players: {message_json}')
        if self.players:
            for client_socket in self.client_sockets:
                self.send(message_json, client_socket)

    def process_message(self, message_json, client_socket, client_address=(0, 0)):
        '''Update server information based on an incoming message packet flag'''
        message_packet = json.loads(message_json)
        flag = message_packet['flag']  # required
        player_name = message_packet['player_name']  # required
        message = message_packet['message']  # required
        print(f'Received from [{player_name}@{client_address}] {flag} {message}')

        if flag == 'MESSAGE':
            # Broadcast the given message
            self.broadcast_message(message_json)

            # # Update the server UI
            # history_listbox.insert(0, f'{player_name}: {message}')
            return

        elif flag == 'JOIN':
            # Add the new client information to the appropriate lists
            # self.client_sockets.append(client_socket)
            # self.client_ips.append(client_address[0])
            if player_name == 'Admin':
                print(f'Admin detected')
                player_id = 9
                message_json = self.create_message(
                    'MESSAGE', 'Server', f'Lists: {len(self.players)} players, {len(self.client_ips)} IPs, {len(self.client_sockets)} sockets')
                self.private_message(message_json, client_socket)
                return
            else:
                if player_name in self.players:
                    message_json = self.create_message(
                        'MESSAGE', 'Admin (private)', f'Unable to join.  {player_name}  active.')
                    self.private_message(message_json, client_socket)
                    # history_listbox.insert(0, f'{player_name}: {message}')
                    return
                if len(self.players) == 3:
                    message_json = self.create_message(
                        'MESSAGE', 'Admin (private)', f'Unable to join game.  Maximum number of players is 3')
                    self.private_message(message_json, client_socket)
                    # history_listbox.insert(0, f'{player_name}: {message}')
                    return

                else:
                    self.players.append(player_name)
                    player_id = len(self.players)

                # set the first player to have the first turn
                if player_id == 1:
                    self.current_player = 1
                    self.player1 = player_name
                elif player_id == 2:
                    self.player2 = player_name
                elif player_id == 3:
                    self.player3 = player_name

                # Broadcast the new client joining and update GUI
                message_json = self.create_message(
                    'UPDATE', f'{player_name}', f'{player_name} has joined the game as player {player_id}', player_id=player_id, next_player=self.current_player, player1=self.player1, player2=self.player2, player3=self.player3)
                self.broadcast_message(message_json)

                # Send private message to new client
                message_json = self.create_message(
                    'ASSIGN', 'Admin (private)', f'You have joined the game as player {player_id}', player_id=player_id, next_player=self.current_player)
                self.private_message(message_json, client_socket)

                # # Update server UI
                # client_listbox.insert(
                #     END, f'Name: {player_name}        IP Addr: {client_address[0]}')
                # history_listbox.insert(0, f'{player_name}: {message}')
                return

        elif flag == 'DRAW':
            player_id = message_packet['player_id']

            drawn_card = self.cards.pop(0)

            # Send new_card to player
            drawn_json = self.create_message(
                'DRAWN', player_name, message='Here is the new card', new_card=drawn_card)

            self.private_message(drawn_json, client_socket)

            self.current_player = player_id

            next_player = self.next_turn()

            # Broadcast the client drawing a new card and update GUI
            message_json = self.create_message(
                'DRAW', '(broadcast)', f'{player_name} has drawn a card.  Turn passed to {next_player}', next_player=next_player)
            self.broadcast_message(message_json)
            # # Update the server UI
            # history_listbox.insert(0, f'{player_name}: {message}')
            return

        elif flag == 'DUMP':
            player_id = message_packet['player_id']
            card_played = message_packet['card_played']
            # print(f'DUMP ----> {message}')
            # Broadcast the client dumping a card
            message_json = self.create_message(
                'DUMP', '(broadcast)', message, card_played=card_played, player_id=player_id)
            self.broadcast_message(message_json)
            # return     uncomment this if needed

        elif flag == 'PLAY':
            # Broadcast the given message
            self.broadcast_message(message_json)

            # # Update the server UI
            # history_listbox.insert(0, f'{player_name}: {message}')

        elif flag == 'TAG':
            game_over = False
            tile_no = message_packet['tile_no']
            tile = int(tile_no)
            player_id = message_packet['player_id']
            card_played = message_packet['card_played']
            i = 0     # corresponds to straights

            # Update game_dict and Compute winner

            # Tier 1, tagged-square   (Tier not necessary, but is included for structure of data)
            for i in range(len(self.game_list)):
                for j in range(len(self.game_list[i])):    # Tier 2, straights
                    count = 0
                    # Tier 3, tiles
                    for k in range(len(self.game_list[i][j])):
                        # print(f'tile:  {type(tile)}  {tile}')
                        if self.game_list[i][j][k][0] == tile:
                            self.game_list[i][j][k][1] = player_id
                        if self.game_list[i][j][k][1] == player_id:
                            count += 1
                        if count == 5:
                            # Compute next player for next game
                            next_player = self.next_turn()
                            game_over = True
                            win_msg = f'Playing card {card_played} to 99, {player_name} tagged tile {tile_no} to WIN!!!'
                            self.game_winner = player_name
                            message_json = self.create_message(
                                'TAG', player_name, f'Playing {card_played} {player_name} tagged tile{tile_no}', tile_no=tile_no,
                                player_id=player_id, card_played=card_played, game_over=game_over, next_player=next_player)
                            self.broadcast_message(message_json)
                            message_json = self.create_message(
                                'WIN', player_name, win_msg, tile_no=tile_no,
                                player_id=next_player, card_played=card_played, game_over=game_over)
                            self.broadcast_message(message_json)
                            # history_listbox.insert(
                            print(f'{win_msg} straight includes {i+1}')
                            return

            # Compute next player
            self.current_player = player_id

            next_player = self.next_turn()

            message_json = self.create_message(
                'TAG', player_name, f'Playing {card_played} {player_name} tagged tile{tile_no}', tile_no=tile_no,
                player_id=player_id, card_played=card_played, game_over=game_over, next_player=next_player)
            self.broadcast_message(message_json)
            # Broadcast the given message
            # broadcast_message(self, message_json)

            # # Update the server UI
            # history_listbox.insert(0, f'{player_name}: {message}')

        elif flag == 'NEW':
            print(
                f'------------------------------- NEW GAME REQUESTED by {player_name}  ----------------------------------')

            game_over = False
            next_player = self.next_turn()
            self.game_winner = ''
            self.cards.clear()
            self.cards = [str(i) for i in range(100)]
            shuffle(self.cards)
            self.game_list = copy.deepcopy(master_list)

            # # Reset tile ownership for new game
            # # self.game_list = master_list.copy()
            # # # Tier 1 not necessary, but is included for structure of data
            # for i in range(len(self.game_list)):
            #     for j in range(len(self.game_list[i])):    # Tier 2, straights
            #         # Tier 3, tiles
            #         for k in range(len(self.game_list[i][j])):
            #             self.game_list[i][j][k][1] = 0

            # set the first player to have the first turn
            if len(self.players) == 1:
                self.current_player = 1
            message_json = self.create_message(
                'NEW', 'Admin (Broadcast)', f'Game has begun at server.',
                game_over=game_over, next_player=next_player)
            self.broadcast_message(message_json)
            return

        elif flag == 'LEAVE':
            player_id = message_packet['player_id']
            if player_name == 'Admin':
                print(f'Admin leaving')
                # return

            # Close/remove client socket and IP address from lists
            index = self.client_sockets.index(client_socket)
            print(
                f'from process_message LEAVE block, index: {type(index)} {index}')

            #   ERROR here:  An operation was attempted on something that is not a socket
            client_socket.close()
            print('CLIENT_SOCKET.CLOSE HAS EXECUTED')

            self.client_sockets.remove(client_socket)

            # consider using remove method in this block of code
            self.client_ips.pop(index)
            # client_listbox.delete(index)

            try:
                p_index = self.players.index(player_name)
            except ValueError:
                print(f'{player_name} is not in list')
            else:
                self.players.pop(p_index)

            # Alert any users that the client has left
            if self.players:
                self.broadcast_message(message_json)
                if self.current_player == player_id:
                    self.current_player = self.next_turn()
            else:
                # self.initialize_game()
                self.cards.clear()
                self.cards = [str(i) for i in range(100)]
                shuffle(self.cards)

                # Reset tile ownership for new game
                # Tier 1 not necessary, but is included for structure of data
                for i in range(len(self.game_list)):
                    # Tier 2, straights
                    for j in range(len(self.game_list[i])):
                        # Tier 3, tiles
                        for k in range(len(self.game_list[i][j])):
                            self.game_list[i][j][k][1] = 0

            print(f'Length of lists AFTER removal: {len(self.players)} players, {len(self.client_ips)} IPs, {len(self.client_sockets)} sockets')


        elif flag == 'CLEARALLPLAYERS':
            # player_id = message_packet['player_id']
            # if player_name == 'Admin':
            #     print(f'Admin leaving')
                # return

            # Close/remove player names, client sockets and IP addresses from lists
            for p in self.players:
                print(p)
            for i in self.client_ips:
                print(i)
            for s in self.client_sockets:
                print(f'socket: {s}')
                s.close()
                print('CLIENT_SOCKET.CLOSE HAS EXECUTED')            
            self.players.clear()
            self.client_ips.clear()
            self.client_sockets.clear()

            # return

            #   ERROR here:  An operation was attempted on something that is not a socket

            # self.client_sockets.remove(client_socket)

            # # consider using remove method in this block of code
            # self.client_ips.pop(index)
            # # client_listbox.delete(index)

            # try:
            #     p_index = self.players.index(player_name)
            # except ValueError:
            #     print(f'{player_name} is not in list')
            # else:
            #     self.players.pop(p_index)

            # # Alert any users that the client has left
            # if self.players:
            #     self.broadcast_message(message_json)
            #     if self.current_player == player_id:
            #         self.current_player = self.next_turn()
            # else:
            # self.initialize_game()
            # self.cards.clear()
            # self.cards = [str(i) for i in range(100)]
            # shuffle(self.cards)

            # # Reset tile ownership for new game
            # # Tier 1 not necessary, but is included for structure of data
            # for i in range(len(self.game_list)):
            #     # Tier 2, straights
            #     for j in range(len(self.game_list[i])):
            #         # Tier 3, tiles
            #         for k in range(len(self.game_list[i][j])):
            #             self.game_list[i][j][k][1] = 0

            print(f'Length of lists AFTER removal: {len(self.players)} players, {len(self.client_ips)} IPs, {len(self.client_sockets)} sockets')

        else:
            print('Error processing message...')


if __name__ == '__main__':
    server = Server()
    server.start()
