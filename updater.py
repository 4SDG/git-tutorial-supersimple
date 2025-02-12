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

        answer = ctypes.windll.user32.MessageBoxW(0, "Update client files? Requires restart of game.", "Game Of 99 updater", 1)
        print(f'answer: {answer}')
        if answer != 1:
            return 'Decline'

        else:
            
            base_url = 'http://'+server_ip+':9999/'
            home_path = os.getenv(key='HOMEPATH')
            source_folder = home_path+'\Games\Source\GameOf99'
            game_folder = home_path+'\Games\GameOf99'
            backup_folder = home_path+'\Games\Backup\GameOf99.bak'
            shutil.rmtree(source_folder)
            os.makedirs(source_folder, exist_ok=True)
            os.makedirs(game_folder, exist_ok=True)
            os.makedirs(backup_folder, exist_ok=True)
            for name in client_files:
                # print(name)
                file_url = base_url+name
                fetched = wget.download(file_url, out=source_folder)
                print(fetched)

            source_path = source_folder+'\\refresh99.cmd'
            destination_path = home_path+'\\Games'
            shutil.copy2(source_path, destination_path)
            return 'Update'
    else:
        return 'Unknown'

# def refresh_all():

#     print(f'Updating client files')
#     home_path = os.getenv(key='HOMEPATH')
#     source_folder = home_path+'\Games\Source\GameOf99'
#     game_folder = home_path+'\Games\GameOf99'
#     backup_folder = home_path+'\Games\Backup\GameOf99.bak'
#     shutil.rmtree(backup_folder)
#     shutil.move(game_folder, backup_folder)
#     shutil.copytree(source_folder, game_folder)
#     print(f'Copy client files function finished')
#     return('Client files updated.')



if __name__ == "__main__":
    os.system('cls')
    if update_client_files('192.168.2.129') == 'Stop':
        exit()
    # refresh_all()