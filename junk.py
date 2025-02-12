import shutil
import os
import sys

def update_client_files(server_ip):    

    base_url = 'http://'+server_ip+':9999/'
    home_path = os.getenv(key='HOMEPATH')
    source_folder = home_path+'\Games\Source\GameOf99'
    game_folder = home_path+'\Games\GameOf99'
    backup_folder = home_path+'\Games\Backup\GameOf99.bak'
    os.makedirs(source_folder, exist_ok=True)
    os.makedirs(game_folder, exist_ok=True)
    os.makedirs(backup_folder, exist_ok=True)

    print(f'Updating client files')
    shutil.rmtree(backup_folder)
    shutil.move(game_folder, backup_folder)
    shutil.copytree(source_folder, game_folder)
    print(f'Copy client files function finished')
    return('Client files updated.')


if __name__ == "__main__":
    os.system('cls')
    if update_client_files('192.168.2.129') == 'Stop':
        exit()