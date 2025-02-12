import scapy.all as scapy
# import scapy
import socket
import os
import json

PORT = 6812  # unused port
FORMAT = 'utf-8'
BUFFER = 1024
DISCONNECT_MESSAGE = '!DISCONNECT'

targets = []  # list for all hosts on LAN
answer = "NOT FOUND"  # game server answer variable for main while loop
game_host = ""  # ip address of hosting system

# get local ip address
local_ip = socket.gethostbyname(socket.gethostname())
print(f"local_ip: {local_ip}")

# calculate local lan gateway and segment via split and join methods
local_list = local_ip.split(".", 3)[:-1]
local_gw = ".".join(local_list) + ".1"
print(f"local_gw: {local_gw}")
local_lan = local_gw + "/24"
print(f"local_lan: {local_lan}")

# create ARP request packet
request = scapy.ARP()

# prepare ARP request to send as broadcast to local lan segment
request.pdst = local_lan
broadcast = scapy.Ether()
broadcast.dst = 'ff:ff:ff:ff:ff:ff'
request_broadcast = broadcast / request

# build list of hosts by sending and receiving at layer 2
hosts = scapy.srp(request_broadcast, timeout=16, verbose=1)[0]


# define function to query all hosts at specified port
# to find the game server
def query_host(msg, target_server):
    # SERVER = target_server
    ADDR = (target_server, PORT)
    portal = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)

    message_json = msg
    # message_json = json.dumps(msg)

    try:
        portal.connect(ADDR)
    except ConnectionRefusedError:
        return ("Connection refused.")
    except TimeoutError:
        return ("Timed out.")

    else:
        message_json = str(msg).encode(FORMAT)
        # print(f"Message to be sent (1): {message}")
        msg_length = len(message_json)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b" " * (BUFFER - len(send_length))
        # print(f"Message to be sent (2): {message}")
        portal.settimeout(2)
        portal.send(send_length)
        # print(f"Message to be sent (*): {message}")
        portal.send(message_json)
        answer = portal.recv(1024).decode(FORMAT)
        return answer


def find_game():
    global answer, game_host
    # build targets list of host ip addresses
    for element in hosts:
        # print(element[1].psrc)
        targets.append(element[1].psrc)

    # remove local_gw (gateway) from targets list
    # print(f"Removing local_gw: {local_gw}")
    targets.remove(local_gw)
    print(targets)

    # while answer != "FOUND":
    for host in targets:
        print(f"Looking for Game on {host}")
        msg = "SEEK"
        answer = query_host(msg, host)
        # query_host(DISCONNECT_MESSAGE, host)
        if answer == "FOUND":
            game_host = host
            print(f"Game {answer} on {host}")
            # output = os.system(
            #     f"xcopy \\\\{host}\\Games\\Source c:\\Data\\Games /H /I /K /E /R /Y")
            # exit()
    if answer != "FOUND":
        game_host = "0.0.0.0"
    return game_host


def main():
    print("findgame starting.")
    game_host = find_game()
    print(f"Game server: {game_host}")


if __name__ == "__main__":
    main()
