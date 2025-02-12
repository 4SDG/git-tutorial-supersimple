import tkinter as tk
from tkinter import DISABLED, VERTICAL, END, NORMAL, simpledialog
# from winsound import Beep
import sys
# import findgame
import client99
# from updater import update_client_files
# import ctypes

# ctypes.windll.shcore.SetProcessDpiAwareness(3)


# board layout
bd = [(5, 5), (6, 5), (6, 6), (5, 6),  # 4
      (5, 7), (6, 7), (7, 7), (7, 6), (7, 5), (7, 4),  # 10
      (6, 4), (5, 4), (4, 4), (4, 5), (4, 6), (4, 7),  # 16
      (3, 7), (3, 6), (3, 5), (3, 4), (3, 3),  # 21
      (4, 3), (5, 3), (6, 3), (7, 3), (8, 3),  # 26
      (8, 4), (8, 5), (8, 6), (8, 7), (8, 8),  # 31
      (7, 8), (6, 8), (5, 8), (4, 8), (3, 8),  # 36
      (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9),  # 43
      (9, 8), (9, 7), (9, 6), (9, 5), (9, 4), (9, 3), (9, 2),  # 50
      (8, 2), (7, 2), (6, 2), (5, 2), (4, 2), (3, 2), (2, 2),  # 57
      (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
      (2, 8), (2, 9),  # 64
      (1, 9), (1, 8), (1, 7), (1, 6), (1, 5), (1, 4), (1, 3), (1, 2), (1, 1),
      (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1),
      (10, 2), (10, 3), (10, 4), (10, 5), (10,
                                           6), (10, 7), (10, 8), (10, 9), (10, 10),
      (9, 10), (8, 10), (7, 10), (6, 10), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10)]


class Square(tk.Frame):

    # defines a Square object to have the following parameters: game, id, owner_id
    def __init__(self, id=0, owner_id=0):
        super().__init__()
        self.id = id
        self.owner_id = owner_id
        self.square_btn = tk.Button(self, height=1, width=3, foreground='gold', background='#876445',
                                    command=lambda: game.tag(self),
                                    font=('Arial Narrow', 18), text=self.id,
                                    borderwidth=0, default=tk.NORMAL, relief=tk.FLAT)
        self.square_btn.pack(expand=True, fill='both', side='bottom')


class Card(tk.LabelFrame):
    def __init__(self):
        super().__init__()
        self.configure(width=8, height=8, padx=1, highlightthickness=0)

        self.cardTop = tk.Label(self, width=8, height=1,
                                bg='gold', fg='#876445', text='', justify=tk.LEFT)

        self.cardBtn = tk.Button(self, text='', width=2, height=1, font=(
            'Arial Narrow', 22), bg='gold', fg='#876445', highlightthickness=0,
            activebackground='gold', relief=tk.FLAT, command='pass', state=tk.DISABLED)

        self.cardBot = tk.Label(self, width=8, height=1,
                                bg='gold', fg='#876445', text='', justify=tk.RIGHT)

        self.cardTop.pack(expand=True, fill='both',
                          side='top', padx=0, pady=0, anchor=tk.W)
        self.cardBot.pack(expand=True, fill='both',
                          side='bottom', padx=0, pady=0, anchor=tk.E)
        self.cardBtn.pack(expand=True, fill='both',
                          side='bottom', padx=0, pady=0)


class Game(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Game of 99')
        # self.geometry('900x800')
        self.geometry('800x700')
        self.tk.call('tk', 'scaling', 1.0)
        # self.resizable(0, 0)

        # windows only (remove the minimize/maximize button)
        # self.attributes('-toolwindow', True)

        self.server_address = "173.89.93.83"
        print(f'Server:  {self.server_address}')
        self.update_flag = True
        self.player_id = 0     # This value is assigned by the server
        self.player = 'Player'
        self.current_player_id = 1
        self.opponent1_id = 0
        self.opponent2_id = 0
        self.player1 = ''
        self.player2 = ''
        self.player3 = ''
        self.info_string = 'Enter your name & server IP, and press CONNECT to begin'
        self.turn_info_string = 'Please CONNECT to game for turn status'

        self.my_name = tk.StringVar(self, self.player)
        self.my_server = tk.StringVar(self, self.server_address)
        self.my_info = tk.StringVar(self, self.info_string)
        self.my_turn_info = tk.StringVar(self, self.turn_info_string)

        self.card_playable = False
        self.playing_card = ''
        self.discards = []    # list to track cards as they are played
        self.squares = []    # list to track squares as they are created

        self.cards_held = {
            "position_1": "",
            "position_2": "",
            "position_3": "",
            "position_4": "",
            "position_5": ""
        }

        # Merge client code into Game object

        self.client = client99.Client()

        # Create frames

        self.upper_frame = tk.Frame(
            width=940, height=120, borderwidth=3, pady=3)

        self.left_frame = tk.Frame(width=20, height=25, borderwidth=3)

        self.center_frame = tk.Frame(width=575, height=525, borderwidth=15,
                                     relief=tk.RAISED, background='gold')

        self.right_frame = tk.Frame(width=20, height=25, borderwidth=3)

        self.lower_frame = tk.Frame(width=800, height=130, borderwidth=0)

        self.player_frame = tk.Frame(width=560, height=60, borderwidth=6,
                                     background='tan')

        # Create widgets and add them to frames

        self.name_label = tk.Label(self, text="Your Name", height=1, width=11,
                                   font=('Arial', 10), justify=tk.RIGHT)
        self.name_entry = tk.Entry(self, width=16, font=(
            'Arial', 10), justify=tk.LEFT, insertofftime=0, textvariable=self.my_name)
        self.server_label = tk.Label(self, text="Server IP", height=1, width=11,
                                     font=('Arial', 10), justify=tk.RIGHT)
        self.server_entry = tk.Entry(self, width=16, font=(
            'Arial', 10), justify=tk.LEFT, insertofftime=0, textvariable=self.my_server)
        self.connect_button = tk.Button(
            self.upper_frame, height=1, width=10, text='CONNECT', font=('Arial', 10), command=self.connect_to_server)
        self.disconnect_button = tk.Button(self, height=1, width=20, text='DISCONNECT/LEAVE', font=(
            'Arial', 10), command=self.disconnect_from_server, state=tk.DISABLED)
        self.new_game_button = tk.Button(self, height=1, width=10, text='NEW GAME', font=(
            'Arial', 10), command=self.new_game, state=tk.DISABLED)
        self.update_client_button = tk.Button(self, height=1, width=10, text='UPDATE', font=(
            'Arial', 10), command=self.upd_client, state=tk.NORMAL)
        self.info_label = tk.Label(self, textvariable=self.my_info, height=1, width=50,
                                   font=('Arial Italic', 13), justify=tk.CENTER)

        self.name_label.grid(row=0, column=0, in_=self.upper_frame)
        self.name_entry.grid(row=0, column=1, in_=self.upper_frame)
        self.server_label.grid(row=0, column=2, in_=self.upper_frame)
        self.server_entry.grid(row=0, column=3, in_=self.upper_frame)
        self.connect_button.grid(
            row=0, column=4, in_=self.upper_frame, padx=10)
        self.disconnect_button.grid(row=0, column=5, in_=self.upper_frame)
        self.new_game_button.grid(
            row=0, column=6, in_=self.upper_frame, padx=10)
        # Comment out lines for update button while using .exe file
        # self.update_client_button.grid(
        #     row=0, column=7, in_=self.upper_frame, padx=10)
        self.info_label.grid(row=1, column=0, columnspan=7, pady=8,
                             in_=self.upper_frame)

        self.opp1_label = tk.Label(self, text="Opponent", height=4, width=16,
                                   font=('Arial', 13), justify=tk.CENTER)
        self.opp1_label.grid(row=0, column=0, in_=self.right_frame)

        self.opp2_label = tk.Label(self, text="Opponent", height=4, width=16,
                                   font=('Arial', 13), justify=tk.CENTER)
        self.opp2_label.grid(row=0, column=0, in_=self.left_frame)

        # Create squares in center_frame, create cards in lower_frame
        self.set_board()

        self.player_turn = tk.Label(self, textvariable=self.my_turn_info, height=2, width=50, background='light grey',
                                    font=('Caladea', 13), justify=tk.CENTER)
        self.player_turn.grid(row=0, column=0, in_=self.player_frame)

        # Add frames to main window
        self.upper_frame.grid(row=0, column=0, columnspan=3)
        self.left_frame.grid(row=1, column=0)
        self.center_frame.grid(row=1, column=1, padx=3, pady=3)
        self.right_frame.grid(row=1, column=2)
        self.lower_frame.grid(row=2, column=0, columnspan=3, padx=15, pady=8)
        self.player_frame.grid(row=3, column=1)

    def connect_to_server(self):
        self.name = self.my_name.get()
        self.client.name = self.my_name.get()
        self.client.server_ip = self.my_server.get()
        # if findgame.query_host('SEEK', self.client.server_ip) != 'FOUND':
        #     self.server_address = findgame.find_game()
        self.client.join(self)
        self.connect_button.configure(state=tk.DISABLED)
        self.disconnect_button.configure(state=tk.NORMAL)
        self.new_game_button.configure(state=tk.NORMAL)
        self.update_client_button.configure(state=tk.DISABLED)
        self.deck.cardBtn.configure(state=tk.NORMAL)
        self.my_info.set(f'Connected to Game Server on {self.server_address}')

    def disconnect_from_server(self):
        self.name_entry.configure(state=tk.NORMAL)
        self.server_entry.configure(state=tk.NORMAL)
        self.connect_button.configure(state=tk.NORMAL)
        self.disconnect_button.configure(state=tk.DISABLED)
        self.new_game_button.configure(state=tk.DISABLED)
        self.update_client_button.configure(state=tk.NORMAL)
        self.reset_squares()
        self.reset_cards()

        self.client.leave(self)
        sys.exit()

    def upd_client(self):
        result = update_client_files(self.server_address)
        # print(f'Result of copy:  {result}')
        # if result == 'Update':
        # self.update_flag = True
        # self.my_info.set(f'You must exit the game now and restart.')
        # self.disconnect_from_server()
        sys.exit()

    def set_board(self):

        # Create all squares from Square class with the following parameters: id, owner_id
        for i in range(0, 99):
            self.squares.append(Square(i+1, 0))
            tile = self.squares[i]
            tile.id = str(i+1)
            tile.grid(row=bd[i][0], column=bd[i][1],
                      in_=self.center_frame, padx=2, pady=2)

        # Create cards from Card class: Opponents (right and left) and Self  (bottom-center)
        self.opp_right_discard = Card()
        self.opp_right_discard.cardBot.configure(
            state=tk.DISABLED, text='DISCARD')
        self.opp_right_discard.grid(
            row=1, column=0, in_=self.right_frame, pady=10)

        self.opp_left_discard = Card()
        self.opp_left_discard.cardBot.configure(
            state=tk.DISABLED, text='DISCARD')
        self.opp_left_discard.grid(
            row=1, column=0, in_=self.left_frame, pady=10)

        self.discard = Card()
        self.discard.cardBot.configure(state=tk.DISABLED, text='DISCARD')
        self.discard.grid(row=1, column=0, in_=self.lower_frame, padx=80)

        self.card1 = Card()
        self.card1.cardBtn.configure(
            text='', command=lambda: self.play(self.card1, "position_1"))
        self.card1.grid(row=1, column=1, in_=self.lower_frame, padx=8)

        self.card2 = Card()
        self.card2.cardBtn.configure(
            text='', command=lambda: self.play(self.card2, "position_2"))
        self.card2.grid(row=1, column=2, in_=self.lower_frame, padx=8)

        self.card3 = Card()
        self.card3.cardBtn.configure(
            text='', command=lambda: self.play(self.card3, "position_3"))
        self.card3.grid(row=1, column=3, in_=self.lower_frame, padx=8)

        self.card4 = Card()
        self.card4.cardBtn.configure(
            text='', command=lambda: self.play(self.card4, "position_4"))
        self.card4.grid(row=1, column=4, in_=self.lower_frame, padx=8)

        self.card5 = Card()
        self.card5.cardBtn.configure(
            text='', command=lambda: self.play(self.card5, "position_5"))
        self.card5.grid(row=1, column=5, in_=self.lower_frame, padx=8)

        self.deck = Card()
        self.deck.cardBtn.configure(
            state=tk.DISABLED, command=lambda: self.draw())
        self.deck.cardBot.configure(text='DRAW')
        self.deck.grid(row=1, column=6, in_=self.lower_frame, padx=80)

    def new_game(self):
        packet = client99.Packet()
        message_json = packet.assemble_json(
            "NEW", f"{self.name}", f"{self.name} requesting a new game", player_id=self.player_id)
        self.client.send(message_json)
        self.reset_squares()
        self.reset_cards()

    def reset_squares(self):
        # Reset square colors
        for square in self.squares:
            square.square_btn.configure(
                background='#876445', foreground='gold')
            square.owner_id = 0

    def reset_cards(self):
        # Reset cards
        self.card1.cardTop.configure(text='')
        self.card1.cardBtn.configure(text='')
        self.card1.cardBot.configure(text='')
        self.card2.cardTop.configure(text='')
        self.card2.cardBtn.configure(text='')
        self.card2.cardBot.configure(text='')
        self.card3.cardTop.configure(text='')
        self.card3.cardBtn.configure(text='')
        self.card3.cardBot.configure(text='')
        self.card4.cardTop.configure(text='')
        self.card4.cardBtn.configure(text='')
        self.card4.cardBot.configure(text='')
        self.card5.cardTop.configure(text='')
        self.card5.cardBtn.configure(text='')
        self.card5.cardBot.configure(text='')
        self.discard.cardTop.configure(text='')
        self.discard.cardBtn.configure(text='')
        self.discard.cardBot.configure(text='DISCARD')
        self.deck.cardBot.configure(text='DRAW')
        self.discards.clear()
        self.cards_held = {
            "position_1": "",
            "position_2": "",
            "position_3": "",
            "position_4": "",
            "position_5": ""
        }
        self.opp_right_discard.cardBtn.configure(text="")
        self.opp_left_discard.cardBtn.configure(text="")
        self.show_turn()

    def draw(self):
        '''Requests a card from the server'''
        if self.player_id != self.current_player_id:
            self.my_info.set(
                f'It is not your turn.  player_id: {self.player_id} current_player_id: {self.current_player_id}')
            return

        if "" in self.cards_held.values():
            packet = client99.Packet()
            message_json = packet.assemble_json(
                "DRAW", self.name, f"{self.name} is drawing a card.", player_id=self.player_id)
            self.client.send(message_json)
        else:
            self.my_info.set(f'You may not draw a card now.  Hand is full.')
            return

        self.show_turn()

    def play(self, card_selected, position_selected):
        '''Plays a card which the client has'''
        if self.player_id != self.current_player_id:
            self.my_info.set(
                f'It is not your turn.  player_id: {self.player_id} current_player_id: {self.current_player_id}')
            return
        # Beep(440, 500)
        self.card_in_play = card_selected
        self.position_in_play = position_selected
        self.card_in_play.cardTop.configure(background='tan')
        self.card_in_play.cardBtn.configure(background='tan')
        self.card_in_play.cardBot.configure(background='tan')
        self.playing_card = self.cards_held[position_selected]
        packet = client99.Packet()

        spam = int(self.playing_card)

        while spam < 100:
            # print(spam)
            if self.squares[spam-1].owner_id == 0:
                print('Card playable')
                break
            spam = spam + 1
        if spam == 100:
            print('Card not playable')
            # Discard unplayable card
            self.discard.cardTop.configure(text=f'{self.playing_card} to 99')
            self.discard.cardBtn.configure(text=self.playing_card)
            self.discard.cardBot.configure(text='DISCARDED')
            self.card_in_play.cardTop.configure(background='gold', text='')
            self.card_in_play.cardBtn.configure(
                background='gold', text='', state=tk.DISABLED)
            self.card_in_play.cardBot.configure(background='gold', text='')

            packet = client99.Packet()
            message_json = packet.assemble_json(
                "DUMP", f"{self.name}", f"{self.name} discards {self.playing_card} to 99 as unplayable",
                player_id=self.player_id, card_played=self.playing_card)
            self.client.send(message_json)

            self.my_info.set(
                f'Card {self.playing_card} to 99 discarded as unplayable.')

            self.cards_held[self.position_in_play] = ""
            self.playing_card = ''

            self.show_turn()
            return

        message_json = packet.assemble_json(
            "PLAY", self.name, f"{self.name} is playing card {self.playing_card} to 99")
        self.client.send(message_json)
        self.my_info.set(
            f'Select a square from {self.playing_card} to 99 to complete your turn.')

    def tag(self, selected_tile):
        '''Tags a tile which no one owns'''

        if self.playing_card == '':
            self.my_info.set("Square clicked with no card in play.")
            return

        if self.player_id != self.current_player_id:
            self.my_info.set(
                f'It is not your turn.  player_id: {self.player_id} current_player_id: {self.current_player_id}')
            return

        if selected_tile.owner_id != 0:
            self.my_info.set(
                f'Tile not available.  It is owned by player {selected_tile.owner_id}: select another tile.')
            return

        if int(selected_tile.id) < int(self.playing_card):
            self.my_info.set(
                f'Card played {self.playing_card} not valid for tile{selected_tile.id}: select another tile.')
            return

        self.my_info.set(
            f'Playing card {self.playing_card}, tile {selected_tile.id} selected by {self.name} {self.player_id}')

        selected_tile.owner_id = self.player_id

        if self.player_id == 1:
            tile_color = "red"
        elif self.player_id == 2:
            tile_color = "blue"
        elif self.player_id == 3:
            tile_color = "green"
        else:
            tile_color = "brown"

        selected_tile.square_btn.configure(
            background=tile_color, foreground='white')

        # Discard card_in_playshow_turn
        self.discard.cardTop.configure(text=f'{self.playing_card} to 99')
        self.discard.cardBtn.configure(text=self.playing_card)
        self.discard.cardBot.configure(text='DISCARDED')

        self.card_in_play.cardTop.configure(background='gold', text='')
        self.card_in_play.cardBtn.configure(
            background='gold', text='', state=tk.DISABLED)
        self.card_in_play.cardBot.configure(background='gold', text='')

        packet = client99.Packet()
        message_json = packet.assemble_json(
            "TAG", f"{self.name}", f"{self.name} selects tile {selected_tile.id} with card {self.playing_card} to 99", tile_no=selected_tile.id,
            player_id=self.player_id, card_played=self.playing_card)
        self.client.send(message_json)

        self.cards_held[self.position_in_play] = ""
        self.playing_card = ''

        self.show_turn()

    def show_turn(self):
        if self.current_player_id == self.player_id:
            self.player_turn.configure(
                background='#227C70', foreground='white')
            self.my_turn_info.set('IT IS YOUR TURN !')
        else:
            self.player_turn.configure(background='#131', foreground='#febd69')
            self.my_turn_info.set(
                f'Waiting for player {self.current_player_id} to take a turn')


if __name__ == "__main__":
    game = Game()
    game.mainloop()
