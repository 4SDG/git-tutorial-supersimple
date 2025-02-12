import socket
import os
import sys

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_os():
    host_os = sys.platform
    # host_os = os.name
    return host_os


if __name__ == "__main__":
    print(get_ip())
    print(get_os())