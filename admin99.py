from tkinter import simpledialog
import tkinter as tk
from tkinter import DISABLED, NORMAL, simpledialog
from winsound import Beep
import sys
import client99


class Control(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Admin Features for Game of 99')
        self.geometry('690x100')
        self.resizable(0, 0)
        self.server_address = '173.89.93.83'
        print(f'Server:  {self.server_address}')
        self.code = 'ou812'
        self.player_id = 9
        self.player = 'Admin'
        self.current_player_id = 9
        self.info_string = 'ADMIN: Press CONNECT to begin'

        self.my_name = tk.StringVar(self, self.player)
        self.my_server = tk.StringVar(self, self.server_address)
        self.my_info = tk.StringVar(self, self.info_string)

        # Merge client code into control object
        self.client = client99.Client()

        # Create frame
        self.upper_frame = tk.Frame(width=680, height=90, borderwidth=3, pady=3)

        # Create widgets
        self.server_label = tk.Label(self, text="Server IP", height=1, width=11,
                                     font=('Arial', 10), justify=tk.RIGHT)
        self.server_entry = tk.Entry(self, width=16, font=(
            'Arial', 10), justify=tk.LEFT, insertofftime=0, textvariable=self.my_server)
        self.connect_button = tk.Button(
            self.upper_frame, height=1, width=10, text='CONNECT', font=('Arial', 10), command=self.connect_to_server)
        self.disconnect_button = tk.Button(self, height=1, width=20, text='DISCONNECT', font=(
            'Arial', 10), command=self.disconnect_from_server, state=tk.DISABLED)
        self.clear_all_players_button = tk.Button(self, height=1, width=10, text='CLEAR ALL', font=(
            'Arial', 10), command=self.clear_all_players, state=tk.DISABLED)
        self.info_label = tk.Label(self, textvariable=self.my_info, height=1, width=50,
                                   font=('Arial Italic', 13), justify=tk.CENTER)

        self.server_label.grid(row=0, column=2, in_=self.upper_frame)
        self.server_entry.grid(row=0, column=3, in_=self.upper_frame)
        self.connect_button.grid(
            row=0, column=4, in_=self.upper_frame, padx=10)
        self.disconnect_button.grid(row=0, column=5, in_=self.upper_frame)
        self.clear_all_players_button.grid(
            row=0, column=6, in_=self.upper_frame, padx=10)
        self.info_label.grid(row=1, column=0, columnspan=7, pady=8,
                             in_=self.upper_frame)

        # Add frames to main window
        self.upper_frame.grid(row=0, column=0, columnspan=3)

    def connect_to_server(self):
        self.name = 'Admin'
        self.client.name = self.name
        self.client.server_ip = self.my_server.get()
        message = self.client.join(self)
        self.connect_button.configure(state=tk.DISABLED)
        self.disconnect_button.configure(state=tk.NORMAL)
        self.clear_all_players_button.configure(state=tk.NORMAL)
        self.my_info.set(f'Connected to {self.server_address} {message}')

    def disconnect_from_server(self):
        self.server_entry.configure(state=tk.NORMAL)
        self.connect_button.configure(state=tk.NORMAL)
        self.disconnect_button.configure(state=tk.DISABLED)
        self.clear_all_players_button.configure(state=tk.DISABLED)

        self.client.leave(self)
        self.client.connected = False
        sys.exit()


    def clear_all_players(self):
        submitted = simpledialog.askstring("Input", "What is the password?")
        if submitted is None:
            print("Nothing submitted")
            return

        if submitted == self.code:
            print(
                f"from clear_all_players, correct password given.")
            packet = client99.Packet()
            message_json = packet.assemble_json(
                "CLEARALLPLAYERS", f"{self.name}", f"You have been disconnected.")
            self.client.send(message_json)
            self.server_entry.configure(state=tk.NORMAL)
            self.connect_button.configure(state=tk.NORMAL)
            self.disconnect_button.configure(state=tk.DISABLED)
            self.clear_all_players_button.configure(state=tk.DISABLED)
            self.client.connected = False
        else:
            print(f"submitted: {submitted} (INCORRECT)")
            


if __name__ == "__main__":
    admin = Control()
    admin.mainloop()