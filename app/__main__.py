from config import Config
import os
from PIL import Image
from app.move import move
import app.scan as scan
from app.scan import Screenshot
from app.pokemon import helpers, Pokemon
from app.push import push
from app.data import data

def scan_all_photos(folder=Config.SCAN_SOURCE_FOLDER, delete=True):
    success = 0
    total = 0
    messages = []
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            total += 1
            filepath = subdir + os.sep + file
            try:
                data = scan_photo(filepath)
            except Exception as e:
                Config.LOGGER.error("Error when scanning photo.")
                move_file(filepath, file, status="ERROR")
            succeed = data['success']
            if succeed:
                success += 1
                name = "none"
            try:
                messages.append(data['message'])
                name = data['pokemon']['name'].lower()
            except KeyError:
                pass

            if succeed:
                move_file(filepath, file, status="SUCCESS", name=name, delete=delete)
            else:
                move_file(filepath, file, status=data['message'])

    return {'success': 0, 'total': 0, 'messages': ["message"]}


def scan_photo(filepath):
    data = {'success': False}
    try:
        screen = Screenshot(filepath)
        poke = helpers.pokemon_from_screenshot(screen)
        extremes = data.get_extremes_loose(poke.name)
        message = build_message(poke,extremes)
        if message is not None:
            data['message'] = message
    except:
        pass


def build_message(poke, extremes):
    w = poke.weight
    h = poke.weight
    title = ""
    if extremes[0] is None or extremes[0] < w:
        title = title + "Heavy"
    if extremes[1] is None or extremes[1] < h:
        title = title + "Tall"
    if extremes[2] is None or extremes[2] > w:
        title = title + "Light"
    if extremes[3] is None or extremes[3] > h:
        title = title + "Small"
    if len(title)>0:
        return f"{poke.name} is now <b>{title}</b>."
    return None



def move_file(filepath, file, status="PROCESSED", name="none", delete=False):
    if status == "PROCESSED":
        _move(filepath, file, Config.SCAN_PROCESSED_FOLDER + os.sep + name, delete=delete)
    else:
        _move(filepath, file, Config.SCAN_ERROR_FOLDER + os.sep + status, delete=delete)


def _move(filepath, file, destination, delete=False):
    if delete:
        os.remove(filepath)
    if not os.path.isdir(destination):
        os.mkdir(destination)
    newfilepath = destination + os.sep + file
    count = 2
    while os.path.isfile(newfilepath):
        index = file.rfind('.')
        newfilepath = destination + os.sep + file[:index] + "_" + str(count) + file[index:]
        count += 1
    os.rename(filepath, newfilepath)


def send_push(success, total, messages):
    if total > 0:
        if success == 0:
            msg = f"Failed to process <b>{total}</b> messages."
        elif len(messages) > 0:
            msg = f"Successfully processed <b>{success}</b> of <b>{total}</b> messages, and found <b>{len(messages)}" \
                  f"</b> upgrades:"
        else:
            f"Successfully processed <b>{success}</b> of <b>{total}</b> messages, and found no upgrades."
        send = "\n".join([msg, *messages])
        push.send_message(send)
        return 0
    return 1


if __name__ == "__main__":
    try:
        move.move_files(Config.MOVE_SOURCE_FOLDER, Config.MOVE_DEST_FOLDER, int(Config.MOVE_LIMIT))
    except Exception as e:
        Config.LOGGER.exception("Exception occurred during move script.  See log.")
    try:
        success, total, messages = scan_all_photos()
    except Exception as e:
        Config.LOGGER.exception("Exception occurred while scanning.  See log.")
    try:
        send_push(success, total, messages)
    except Exception as e:
        Config.LOGGER.exception("Exception occurred while pushing.  See log.")
