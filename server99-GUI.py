# 99server.py
import os
import socket
from socket import SHUT_RDWR
import threading
import json
import tkinter as tk
from tkinter import DISABLED, VERTICAL, END, NORMAL
from random import shuffle
from list99 import master_list

# Define window
root = tk.Tk()
root.title('The Game of 99 Server')
root.geometry('580x580')
root.resizable(0, 0)
root.config(bg='light grey')

# Create Frames
controls_frame = tk.Frame(root, bg='light grey')
history_frame = tk.Frame(root, bg='light grey')
client_frame = tk.Frame(root, bg='light grey')
controls_frame.pack(pady=5)
history_frame.pack()
client_frame.pack(pady=5)

# Controls Frame Layout
start_button = tk.Button(controls_frame, text='Start Server', borderwidth=5,
                         width=20, font='Arial', bg='grey', command=lambda: server.start())
end_button = tk.Button(controls_frame, text='End Server', borderwidth=5, width=20,
                       font='Arial', bg='grey', state=DISABLED, command=lambda: server.stop())

start_button.grid(row=0, column=2, padx=5, pady=10)
end_button.grid(row=0, column=3, padx=5, pady=10)

# History Frame Layout
history_scrollbar = tk.Scrollbar(history_frame, orient=VERTICAL)
history_listbox = tk.Listbox(history_frame, height=16, width=55, borderwidth=3,
                             font='Arial', bg='light blue', fg='dark blue', yscrollcommand=history_scrollbar.set)
history_scrollbar.config(command=history_listbox.yview)

history_listbox.grid(row=0, column=0)
history_scrollbar.grid(row=0, column=1, sticky='NS')

# Client Frame Layout
client_scrollbar = tk.Scrollbar(client_frame, orient=VERTICAL)
client_listbox = tk.Listbox(client_frame, height=8, width=55, borderwidth=3,
                            font='Arial', bg='light blue', fg='dark blue', yscrollcommand=client_scrollbar.set)
client_scrollbar.config(command=client_listbox.yview)

client_listbox.grid(row=0, column=0)
client_scrollbar.grid(row=0, column=1, sticky='NS')


class Server():
    '''A class to store a connection - a server socket and pertinent information'''

    def __init__(self):

        self.initialize_socket()
        self.initialize_game()

    def initialize_socket(self):
        # self.host_ip = socket.gethostbyname(
        #     socket.gethostname())  # gets IPv4 of local system
        self.host_ip = '192.168.1.102'
        # hard-coded IP needed due to my own system using multiple IPs for
        # requirements of Virtual Box
        print(type(self.host_ip))
        self.host_port = 9999  # unused port
        # self.host_addr is the tuple needed for binding socket to server
        self.host_addr = (self.host_ip, self.host_port)

        self.encoder = 'utf-8'
        self.bytesize = 2048
        self.buffer = 1024
        self.header = 32

    def initialize_game(self):
        self.client_sockets = []
        self.client_ips = []
        self.cards = []
        self.players = []
        self.current_player = 0
        self.player1 = ''
        self.player2 = ''
        self.player3 = ''
        self.game_winner = ''
        self.game_list = master_list.copy()

        for i in range(0, 100):
            self.cards.append(str(i))

        shuffle(self.cards)

    def start(self):
        # create the socket
        self.host_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)

        # Add 'try' block to check whether socket exists
        try:
            self.host_socket.bind((self.host_addr))

        except (WindowsError):
            self.host_socket.connect((self.host_addr))
            self.host_socket.shutdown(SHUT_RDWR)
            self.host_socket.close()
            os._exit(0)

        else:
            # Create a thread to continously listen for connections and accept them
            listen_thread = threading.Thread(target=self.listening)
            listen_thread.start()

        # Update GUI
        history_listbox.delete(0, END)
        history_listbox.insert(
            0, f'[STARTING] Server started on {self.host_ip}')
        end_button.config(state=NORMAL)
        start_button.config(state=DISABLED)

    def stop(self):
        '''Begin the process of ending the server'''
        # Update GUI
        history_listbox.insert(0, 'Server is ending.')
        end_button.config(state=DISABLED)
        start_button.config(state=NORMAL)
        # Alert all users that the server is closing
        print(f'List of players has {len(self.players)} entries')
        message_json = self.create_message(
            'DISCONNECT', 'Admin (broadcast)', message='Server is closing...')
        self.broadcast_message(message_json)

        try:
            self.host_socket.shutdown(socket.SHUT_RDWR)

        except (WindowsError):  # [WinError 10057]
            history_listbox.insert(
                0, f'[ENDING] Server has no connections.  Socket closes on app exit.')
            print(
                'Server exited because no connections were active while stopping.  PLEASE RESTART THE SERVER.')
            os._exit(0)
            # sys.exit()
        else:
            self.host_socket.close()

        # self.host_socket.close()
        end_button.config(state=DISABLED)
        start_button.config(state=NORMAL)

    def listening(self):
        '''Connect an incoming client to the server'''

        self.host_socket.listen()
        history_listbox.insert(
            0, f'[LISTENING] Server is listening for IPv4 connections')

        while True:
            client_socket, client_addr = self.host_socket.accept()
            # This (blocks) waits for a new connection to the server.  When it does the address+port will be stored in addr,
            # and client_socket is a socket object to send information back to the client.
            thread = threading.Thread(
                target=self.new_connection, args=(client_socket, client_addr))
            thread.start()
            threading.enumerate()
            print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')
            self.client_sockets.append(client_socket)
            self.client_ips.append(client_addr[0])

    # new_connection runs once for each connected client in its own thread
    def new_connection(self, client_socket, client_addr):
        history_listbox.insert(
            0, f'[NEW CONNECTION] Someone connected from {client_addr[0]}.')
        connected = True
        print(
            f'Begin new_connection while loop to receive from {client_addr[0]}')
        while connected:
            try:
                # tells us how long the msg is that's coming - the header
                msg_length = client_socket.recv(
                    self.header).decode(self.encoder)
            except (WindowsError):
                print('From new_connection: Client socket not detected.')
                connected = False
                break
            else:
                if msg_length:
                    msg_length = int(msg_length)
                    msg = client_socket.recv(msg_length).decode(self.encoder)
                    print(f'Received from sender [{client_addr}] {msg}')
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
        client_socket.send(send_length)
        client_socket.send(message)

    def private_message(self, message_json, client_socket):
        self.send(message_json, client_socket)

    def broadcast_message(self, message_json):
        '''Send a message to all client sockets connected to the server...ALL JSON ARE ENCODED'''
        print(
            f'broadcast_message to {len(self.players)} players: {message_json}')
        if len(self.players) != 0:
            for client_socket in self.client_sockets:
                self.send(message_json, client_socket)

    def process_message(self, message_json, client_socket, client_address=(0, 0)):
        '''Update server information based on an incoming message packet flag'''
        message_packet = json.loads(message_json)
        flag = message_packet['flag']  # required
        player_name = message_packet['player_name']  # required
        message = message_packet['message']  # required

        if flag == 'MESSAGE':
            # Broadcast the given message
            self.broadcast_message(message_json)

            # Update the server UI
            history_listbox.insert(0, f'{player_name}: {message}')
            return

        elif flag == 'JOIN':
            # Add the new client information to the appropriate lists
            # self.client_sockets.append(client_socket)
            # self.client_ips.append(client_address[0])
            if player_name in self.players:
                message_json = self.create_message(
                    'MESSAGE', 'Admin (private)', f'Unable to join game.  Name:  {player_name}  already active.')
                self.private_message(message_json, client_socket)
                history_listbox.insert(0, f'{player_name}: {message}')
                return
            if len(self.players) == 3:
                message_json = self.create_message(
                    'MESSAGE', 'Admin (private)', f'Unable to join game.  Maximum number of players is 3')
                self.private_message(message_json, client_socket)
                history_listbox.insert(0, f'{player_name}: {message}')
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

            # Update server UI
            client_listbox.insert(
                END, f'Name: {player_name}        IP Addr: {client_address[0]}')
            history_listbox.insert(0, f'{player_name}: {message}')
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
            # Update the server UI
            history_listbox.insert(0, f'{player_name}: {message}')
            return

        elif flag == 'NEW':
            print(
                f'------------------------------- NEW GAME REQUESTED by {player_name}  ----------------------------------')
            history_listbox.insert(
                0, f'NEW GAME requested by {player_name}')
            # if self.game_winner != '':
            game_over = False
            # self.players.clear()
            # next_player = self.current_player
            # next_player = message_packet['player_id']
            next_player = self.next_turn()
            self.game_winner = ''
            # self.game_list = master_list.copy()
            self.cards.clear()
            for i in range(0, 100):
                self.cards.append(str(i))

            shuffle(self.cards)

            # Reset tile ownership for new game
            # Tier 1 not necessary, but is included for structure of data
            for i in range(len(master_list)):
                for j in range(len(master_list[i])):    # Tier 2, straights
                    # Tier 3, tiles
                    for k in range(len(master_list[i][j])):
                        master_list[i][j][k][1] = 0

            # Update the server UI
            history_listbox.insert(
                0, f'NEW GAME  started.  Turn is given to {next_player}')

            # set the first player to have the first turn
            if len(self.players) == 1:
                self.current_player = 1
            message_json = self.create_message(
                'NEW', 'Admin (Broadcast)', f'Game has begun at server.',
                game_over=game_over, next_player=next_player)
            self.broadcast_message(message_json)
            return

        elif flag == 'PLAY':
            # Broadcast the given message
            self.broadcast_message(message_json)

            # Update the server UI
            history_listbox.insert(0, f'{player_name}: {message}')
            # history_listbox.itemconfig(0, fg=color)

        elif flag == 'TAG':
            game_over = False
            tile_no = message_packet['tile_no']
            player_id = message_packet['player_id']
            card_played = message_packet['card_played']
            i = 0     # corresponds to straights

            # Update game_dict and Compute winner

            # Tier 1, tagged-square   (Tier not necessary, but is included for structure of data)
            for i in range(len(master_list)):
                for j in range(len(master_list[i])):    # Tier 2, straights
                    count = 0
                    for k in range(len(master_list[i][j])):     # Tier 3, tiles
                        if master_list[i][j][k][0] == int(tile_no):
                            master_list[i][j][k][1] = player_id
                        if master_list[i][j][k][1] == player_id:
                            count += 1
                        if count == 5:
                            # Compute next player for next game
                            next_player = self.next_turn()
                            game_over = True
                            win_msg = f'Playing card {card_played} to 99, {player_name} tagged tile {tile_no} and WINS!!!'
                            self.game_winner = player_name
                            message_json = self.create_message(
                                'TAG', player_name, f'Playing {card_played} {player_name} tagged tile{tile_no}', tile_no=tile_no,
                                player_id=player_id, card_played=card_played, game_over=game_over, next_player=next_player)
                            self.broadcast_message(message_json)
                            message_json = self.create_message(
                                'WIN', player_name, win_msg, tile_no=tile_no,
                                player_id=next_player, card_played=card_played, game_over=game_over)
                            self.broadcast_message(message_json)
                            history_listbox.insert(
                                0, f'{player_name}: {win_msg}')
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

            # Update the server UI
            history_listbox.insert(0, f'{player_name}: {message}')

        elif flag == 'LEAVE':
            player_id = message_packet['player_id']
            if self.current_player == player_id:
                self.current_player = self.next_turn()

            # Close/remove client socket and IP address from lists
            index = self.client_sockets.index(client_socket)
            print(
                f'from process_message LEAVE block, index: {type(index)} {index}')

            #   ERROR here:  An operation was attempted on something that is not a socket
            client_socket.close()
            print('CLIENT_SOCKET.CLOSE HAS EXECUTED')

            self.client_sockets.remove(client_socket)
            self.client_ips.pop(index)
            client_listbox.delete(index)

            p_index = self.players.index(player_name)
            self.players.pop(p_index)

            # Alert any users that the client has left
            if len(self.players) > 0:
                self.broadcast_message(message_json)
            else:
                # self.initialize_game()
                self.cards.clear()
                for i in range(0, 100):
                    self.cards.append(str(i))

                shuffle(self.cards)

                # Reset tile ownership for new game
                # Tier 1 not necessary, but is included for structure of data
                for i in range(len(master_list)):
                    for j in range(len(master_list[i])):    # Tier 2, straights
                        # Tier 3, tiles
                        for k in range(len(master_list[i][j])):
                            master_list[i][j][k][1] = 0

            print(
                f'Length of lists AFTER removal: {len(self.players)}, {len(self.client_ips)}, {len(self.client_sockets)}')

            # Update the server UI
            history_listbox.insert(
                0, f'Admin (broadcast): {player_name} has left the game...')

        else:
            # Catch for errors...
            history_listbox.insert(0, 'Error processing message...')


# Create a Connection object and run the root window's mainloop()
if __name__ == '__main__':
    server = Server()
    root.mainloop()
