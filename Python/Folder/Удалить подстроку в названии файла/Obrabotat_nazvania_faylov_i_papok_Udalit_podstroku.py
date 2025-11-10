import os

def rename_files_and_folders(directory, lst_str_to_remove):
    # Обработка файлов
    for root, _, files in os.walk(directory, topdown=False):
        for file_name in files:
            new_file_name = file_name
            for string_to_remove in lst_str_to_remove:
                new_file_name = new_file_name.replace(string_to_remove, '')
            old_file_path = os.path.join(root, file_name)
            new_file_path = os.path.join(root, new_file_name)
            os.rename(old_file_path, new_file_path)
    # Обработка папок
    for root, dirs, _ in os.walk(directory, topdown=False):
        for dir_name in dirs:
            new_dir_name = dir_name
            for string_to_remove in lst_str_to_remove:
                new_dir_name = new_dir_name.replace(string_to_remove, '')
            old_dir_path = os.path.join(root, dir_name)
            new_dir_path = os.path.join(root, new_dir_name)
            os.rename(old_dir_path, new_dir_path)

directory_path = "F:/000"
lst_str_to_remove = ["[eground.org] ",                     "[s1.eground.org] ",
                     "[SuperSliv.biz] ",                   "[SLIV.ONE] ",
                     "[SW.BAND] ",                         "[Boominfo.ORG] ",
                     "SuperSliv.BiZ - ",                   "[M1.Boominfo.ORG] ",
                     "[Яндекс.Практикум] ",                "[WWW.SW.BAND] ",
                     "[S1.SLIV.ONE] ",                     "[Boominfo.CC] "]

rename_files_and_folders(directory_path, lst_str_to_remove)




