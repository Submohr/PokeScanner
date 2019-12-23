import os
import shutil
from config import Config
from datetime import datetime


def move_files(source_folder, dest_folder, max_count, delete_extra=True, file_types=["PNG"], timestamp=True):
    move_count = 0
    del_count = 0
    for subdir, dirs, files in os.walk(source_folder):
        for file in files:
            try:
                try:
                    index=file.rfind('.')
                    file_type =file[index+1:].upper()
                except:
                    continue
                if file_type in file_types:
                    old_file_path = subdir + os.sep + file
                    if timestamp:
                        new_file_path = dest_folder + os.sep + file[:file.rfind('.')] + datetime.utcnow().strftime('%y%m%d%H%M%S%f') + file[file.rfind('.'):]
                    else:
                        new_file_path = dest_folder + os.sep + file
                    count = 0
                    while os.path.isfile(new_file_path):
                        new_file_path = dest_folder + os.sep + file[:index] + "_" + str(count) + file[index:]
                        count += 1
                    shutil.move(old_file_path,new_file_path)
                    Config.LOGGER.debug(f"Moved file from {old_file_path} to {new_file_path}.")
                    move_count += 1
                elif delete_extra:
                    old_file_path = subdir + os.sep + file
                    os.remove(old_file_path)
                    del_count += 1
                    Config.LOGGER.debug(f"Deleted file from {old_file_path}")
                if move_count >= max_count:
                    Config.LOGGER.debug(f"Moved {move_count} files and deleted {del_count} files.")
                    return move_count, del_count
            except Exception as e:
                Config.LOGGER.exception("Encountered exception in function move_files")

    Config.LOGGER.debug(f"Moved {move_count} files and deleted {del_count} files.")
    return move_count, del_count

