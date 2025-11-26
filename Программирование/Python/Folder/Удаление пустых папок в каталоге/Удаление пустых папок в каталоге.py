import os

def remove_empty_folders(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for dirname in dirnames:
            folder_path = os.path.join(dirpath, dirname)
            if not os.listdir(folder_path):
                try:
                    os.rmdir(folder_path)
                    print("Удалил пустую папку:", folder_path)
                except OSError:
                    print("Не удалось удалить пустую папку:", folder_path)
        if not os.listdir(dirpath):
            try:
                os.rmdir(dirpath)
                print("Удалил начало каталога:", dirpath)
            except OSError:
                print("Не удалось удалить начало каталога:", dirpath)

root_directory = 'C:/Users/.../Documents/Папка'
remove_empty_folders(root_directory)



