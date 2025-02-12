import json
import threading
import socket
import tkinter as tk


class Packet(dict):
    '''The Packet object is a dictionary'''
    '''This class stores the data to be sent to the server'''

    def assemble_json(self, flag, player_name, message, tile_no="", player_id="", card_played=""):
        '''Return a message packet to be sent to the server'''
        message_packet = {
            "flag": flag,
            "player_name": player_name,
            "message": message,
            "tile_no": tile_no,
            "player_id": player_id,
            "card_played": card_played}

        message_json = json.dumps(message_packet)
        return message_json


class Client():
    '''The Client object is a connection to a server'''
    '''This class stores a client socket, other pertinent data and methods'''

    def __init__(self):
        self.server_port = 6812
        self.server_ip = "173.89.93.83"
        self.encoder = "utf-8"
        self.buffer = 1024  # Total size in bytes of message received, might need to increase this
        self.header = 32    # Length of message in bytes, this is sent first
        self.connected = False

    def join(self, game):
        '''Connects the client to the server'''
        # Create the socket
        self.server_addr = (self.server_ip, self.server_port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.connect(self.server_addr)
        self.connected = True

        # Create a thread to coninousuly receive messages from the server
        receive_thread = threading.Thread(
            target=self.receive_message, args=(game, self.my_socket, self.server_addr))
        receive_thread.start()

        packet = Packet()
        message_json = packet.assemble_json(
            "JOIN", game.name, f"{self.name} joins game.")
        self.send(message_json)

    def leave(self, game):
        '''Disconnect the client from the server'''
        # Create a message packet to be sent

        packet = Packet()
        message_json = packet.assemble_json(
            "LEAVE", game.name, f"{game.name} has left the game")
        self.send(message_json)
        if game.name == 'Admin':
            print('Goodbye all.')
            self.connected = False
            return

        game.disconnect_button.configure(state=tk.DISABLED)
        game.connect_button.configure(state=tk.NORMAL)
        game.my_info.set(f'Disconnected from Game Server on {self.server_ip}')
        game.player_turn.configure(background='light grey', foreground='black')
        game.my_turn_info.set('Please CONNECT to game for turn status')
        self.connected = False

    def send(self, message_json):
        '''Send a message to the server'''
        message = message_json.encode(self.encoder)

        msg_length = len(message)
        send_length = str(msg_length).encode(self.encoder)
        # adds spaces (in binary) to pad the message to header length
        send_length += b" " * (self.header - len(send_length))
        self.my_socket.send(send_length)
        self.my_socket.send(message)

    def receive_message(self, game, my_socket, server_addr):
        '''Receive a message from the server'''
        while self.connected:
            print("Begin receive_message while loop, waiting for recv")
            # Receive an incoming message packet from the server
            try:
                # tells us how long the msg is that's coming - the header
                msg_length = my_socket.recv(
                    self.header).decode(self.encoder)
            except:
                # Cannot receive message, close the connection and break
                game.my_info.set(f'Connection has been closed...Goodbye.')
                self.connected = False
                break

            if msg_length:
                msg_length = int(msg_length)
                message_json = my_socket.recv(msg_length).decode(self.encoder)
                self.process_message(game, message_json,
                                     self.my_socket, self.server_addr)

        if self.connected:
            game.show_turn()

    def process_message(self, game, message_json, my_socket, server_addr):
        packet = json.loads(message_json)
        flag = packet["flag"]  # required
        player_name = packet["player_name"]  # required
        message = packet["message"]  # required
        print(f'player_name: {player_name}  message: {message}')

        if player_name == 'Admin':
            print(f'Admin detected  {flag}')
            return

        if player_name == 'Server':
            game.my_info.set(f'{player_name}:  {message}')
            return

        if flag == "ASSIGN":
            game.player_id = int(packet["player_id"])
            game.current_player = int(packet["next_player"])

            if game.player_id == 1:
                game.player1_name = game.current_player
                game.player_frame.config(bg='red')
                game.opp1_label.config(fg='blue')
                game.opponent1_id = 2
                game.opp2_label.config(fg='green')
                game.opponent2_id = 3

            if game.player_id == 2:
                game.player2_name = game.current_player
                game.player_frame.config(bg='blue')
                game.opp1_label.config(fg='green')
                game.opponent1_id = 3
                game.opp2_label.config(fg='red')
                game.opp2_label.config(text=game.player1)
                game.opponent2_id = 1

            if game.player_id == 3:
                game.player3_name = game.current_player
                game.player_frame.config(bg='green')
                game.opp1_label.config(fg='red')
                game.opp1_label.config(text=game.player1)
                game.opponent1_id = 1
                game.opp2_label.config(fg='blue')
                game.opp2_label.config(text=game.player2)
                game.opponent2_id = 2

            game.my_info.set(
                f'game.player_id: {game.player_id}  Turn given to: {game.current_player}')
            game.show_turn()

        elif flag == "UPDATE":
            player_id = int(packet["player_id"])
            game.player1 = packet['player1']
            game.player2 = packet['player2']
            game.player3 = packet['player3']
            if game.player_id == 1:
                game.player1 = player_name
                game.opp1_label.config(text=game.player2)
                game.opp2_label.config(text=game.player3)
            elif game.player_id == 2:
                game.player2 = player_name
                game.opp1_label.config(text=game.player3)
                game.opp2_label.config(text=game.player1)
            elif game.player_id == 3:
                game.player3 = player_name
                game.opp1_label.config(text=game.player1)
                game.opp2_label.config(text=game.player2)
            print(
                f'player_id: {player_id}, game.player1: {game.player1}, game.player2: {game.player2}, game.player3: {game.player3}')

        elif flag == "LEAVE":
            game.my_info.set(f'Leaving server')
            self.my_socket.close()
            return

        elif flag == "NEW":

            game.cards_held = {
                "position_1": "",
                "position_2": "",
                "position_3": "",
                "position_4": "",
                "position_5": ""
            }
            game.deck.cardBtn.configure(state=tk.NORMAL)
            game.opp_right_discard.cardBtn.configure(text="")
            game.opp_left_discard.cardBtn.configure(text="")

            game.current_player = int(packet["next_player"])
            game.my_info.set(
                f'{player_name}:  {message}')
            # game.my_turn_info.set(f'New game started')
            game.show_turn()
            return

        elif flag == "WIN":
            # game.player_id = int(packet["player_id"])
            game.current_player = packet["next_player"]
            game.my_info.set(f'{message}')
            game.my_turn_info.set(f'WINNER is {player_name}')
            game.deck.cardBtn.configure(state=tk.DISABLED)
            game.card1.cardBtn.configure(state=tk.DISABLED)
            game.card2.cardBtn.configure(state=tk.DISABLED)
            game.card3.cardBtn.configure(state=tk.DISABLED)
            game.card4.cardBtn.configure(state=tk.DISABLED)
            game.card5.cardBtn.configure(state=tk.DISABLED)
            # return

        elif flag == "MESSAGE":
            game.current_player = packet["next_player"]
            game.my_info.set(
                f'{message}, player_id: {game.player_id}  Turn given to: {game.current_player}')
            game.show_turn()
            return

        elif flag == "DRAWN":
            new_card = packet["new_card"]
            if game.cards_held["position_1"] == "":
                game.cards_held["position_1"] = new_card
                game.card1.cardTop.configure(text=f'{new_card} to 99')
                game.card1.cardBtn.configure(text=new_card, state=tk.NORMAL)
                game.card1.cardBot.configure(text=f'{new_card} to 99')
            elif game.cards_held["position_2"] == "":
                game.cards_held["position_2"] = new_card
                game.card2.cardTop.configure(text=f'{new_card} to 99')
                game.card2.cardBtn.configure(text=new_card, state=tk.NORMAL)
                game.card2.cardBot.configure(text=f'{new_card} to 99')
            elif game.cards_held["position_3"] == "":
                game.cards_held["position_3"] = new_card
                game.card3.cardTop.configure(text=f'{new_card} to 99')
                game.card3.cardBtn.configure(text=new_card, state=tk.NORMAL)
                game.card3.cardBot.configure(text=f'{new_card} to 99')
            elif game.cards_held["position_4"] == "":
                game.cards_held["position_4"] = new_card
                game.card4.cardTop.configure(text=f'{new_card} to 99')
                game.card4.cardBtn.configure(text=new_card, state=tk.NORMAL)
                game.card4.cardBot.configure(text=f'{new_card} to 99')
            elif game.cards_held["position_5"] == "":
                game.cards_held["position_5"] = new_card
                game.card5.cardTop.configure(text=f'{new_card} to 99')
                game.card5.cardBtn.configure(text=new_card, state=tk.NORMAL)
                game.card5.cardBot.configure(text=f'{new_card} to 99')

            return

        elif flag == "DRAW":
            game.current_player_id = int(packet["next_player"])
            game.my_info.set(f'{player_name}:  {message}')
            game.show_turn()

        elif flag == "DUMP":
            player_id = packet['player_id']
            card_played = packet['card_played']
            if player_id != game.player_id:
                if game.opponent1_id == player_id:
                    game.opp_right_discard.cardBtn.configure(text=card_played)
                else:
                    game.opp_left_discard.cardBtn.configure(text=card_played)
            game.my_info.set(f'{message}')

        elif flag == "TAG":
            player_id = packet['player_id']
            tile_no = int(packet['tile_no'])
            card_played = packet['card_played']
            game.current_player_id = int(packet["next_player"])
            # print(f'game.current_player_id: {game.current_player_id}')

            if player_id == 1:
                tile_color = "red"
            elif player_id == 2:
                tile_color = "blue"
            elif player_id == 3:
                tile_color = "green"
            else:
                tile_color = "brown"

            game.squares[tile_no-1].square_btn.configure(
                background=tile_color, foreground='white')

            game.squares[tile_no-1].owner_id = player_id

            if player_id != game.player_id:
                if game.opponent1_id == player_id:
                    game.opp_right_discard.cardBtn.configure(text=card_played)
                else:
                    game.opp_left_discard.cardBtn.configure(text=card_played)

            # game.current_player_id = int(packet["next_player"])
            game.show_turn()


def main():
    print("Client starting.")
    pass


if __name__ == "__main__":
    main()
