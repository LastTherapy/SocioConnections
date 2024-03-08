import os
import shutil

source_directory = 'media/'  # Укажите путь к исходной директории
target_directory = 'media_new/'   # Укажите путь к целевой директории



if not os.path.exists(target_directory):
    os.makedirs(target_directory)

for folder_name in os.listdir(source_directory):
    folder_path = os.path.join(source_directory, folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            target_file_path = os.path.join(target_directory, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                if os.path.exists(target_file_path):
                    os.remove(file_path)  # Удаление файла, если он уже существует в целевой директории
                else:
                    shutil.move(file_path, target_directory)
        # Удаление пустой папки
        os.rmdir(folder_path)