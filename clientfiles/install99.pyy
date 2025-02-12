# IMPORTANT --- this file must be copied to the \clientfiles folder for staging
# IMPORTANT --- this file must be RENAMED to install.cmd in the \clientfiles folder

import shutil
import os
import sys
import wget
import ctypes

client_files = [
    'game99.py',
    'client99.py',
    'game99.cmd',
    'updater.py',
    'Game Of 99.lnk',
    'refresh99.cmd'
]

def update_client_files(server_ip):
    
    if sys.platform == 'win32':

        answer = ctypes.windll.user32.MessageBoxW(0, "Create folders and download client files?", "Game Of 99 installer", 1)
        print(f'answer: {answer}')
        if answer != 1:
            print('Declined')
            sys.exit()

        else:
            
            base_url = 'http://'+server_ip+':9999/'
            home_path = os.getenv(key='HOMEPATH')
            source_folder = home_path+'\Games\Source\GameOf99'
            game_folder = home_path+'\Games\GameOf99'
            backup_folder = home_path+'\Games\Backup\GameOf99.bak'
            os.makedirs(source_folder, exist_ok=True)
            os.makedirs(game_folder, exist_ok=True)
            os.makedirs(backup_folder, exist_ok=True)
            for name in client_files:
                # print(name)
                file_url = base_url+name
                fetched = wget.download(file_url, out=source_folder)
                fetched = wget.download(file_url, out=game_folder)
                print(fetched)

    else:
        print('Unknown system')
        sys.exit()


if __name__ == "__main__":
    os.system('cls')
    server_address = input("Please provide the server's IP address: ")
    update_client_files(server_address)
    # refresh_all()