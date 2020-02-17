from config import Config
import os
from PIL import Image
from app.move import move
import app.scan as scan
from app.scan import Screenshot
from app.pokemon import helpers, Pokemon, constants
from app.push import push
from app.data import data
import traceback
from datetime import datetime
import math


def scan_all_photos(folder=Config.SCAN_SOURCE_FOLDER, delete=True):
    success = 0
    total = 0
    messages = []
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            total += 1
            filepath = subdir + os.sep + file
            dat = {'success': False, 'pokemon_name': None, 'message': "UNKNOWN"}
            try:
                dat = scan_photo(filepath)
            except Exception as e:
                Config.LOGGER.exception("Error when scanning photo.")
                move_file(filepath, file, status="ERROR")
                continue
            try:
                succeed = dat['success']
            except:
                succeed = False
            try:
                message = dat['message']
            except:
                message = "UNKNOWN"
            if succeed is True:
                success += 1
                name = "none"
                if message not in [None, "UNKNOWN",""]:
                    messages.append(message)
            try:
                name = str(dat['pokemon_name']).lower()
            except KeyError:
                pass
            if succeed is True:
                move_file(filepath, file, status="PROCESSED", name=name, delete=delete)
            else:
                move_file(filepath, file, status=str(message))

    return {'success': success, 'total': total, 'messages': messages}


def scan_photo(filepath):
    dat = {'success': False, 'pokemon_name': None, "message": "UNKNOWN"}
    try:
        screen = Screenshot(filepath)
        poke = helpers.pokemon_from_screenshot(screen)
        if poke.name is None:
            dat['message'] = "BADNAME"
            dat['success'] = "FALSE"
            return dat
        dat['pokemon_name'] = poke.name
        extremes = data.get_all_extremes(poke.name)
        try:
            source_name = screen.image_path[screen.image_path.rfind(os.sep) + 1:]
        except:
            source_name = ""
        try:
            confidence_data = "weight{" + str(screen.weight_data['conf']) + \
                              "}, height{" + str(screen.height_data['conf']) + \
                              "}, name{" + str(screen.name_data['conf']) + \
                              "}, type{" + str(screen.type_data['conf']) + "}"
        except:
            confidence_data = ""
        try:
            ts = datetime.strptime(screen.created_ts, "%Y:%m:%d %H:%M:%S")
        except:
            ts = datetime.utcnow()
        insert = data.insert_pokemon(poke, source_type="screenshot",
                                     source_name=source_name,
                                     created_timestamp=ts,
                                     confidence_data=confidence_data)
        if not insert["success"]:
            dat['message'] = "DBERROR"
        else:
            dat['success'] = True
            message = build_message(poke, extremes)
            if message is not None:
                dat['message'] = message
    except:
        Config.LOGGER.exception()
        pass
    return dat


def build_message(poke, extremes):
    w = poke.weight
    h = poke.height
    title = ""
    s = extremes["self"]
    if s is not None:
        if s[0] is None or s[0] < w:
            title = title + "Heavy"
        if s[1] is None or s[1] < h:
            title = title + "Tall"
        if s[2] is None or s[2] > w:
            title = title + "Light"
        if s[3] is None or s[3] > h:
            title = title + "Small"
    if len(title) > 0:
        return f"{poke.name} is now <b>{title}</b>."
    e = extremes["evos"]
    f = None
    if e is not None:
        e_heavy = [99999999]
        e_tall = [99999999]
        e_light = [-1]
        e_small = [-1]
        for p in e.values():
            if(p[0]>0):
                e_heavy.append(p[0])
            if(p[1]>0):
                e_tall.append(p[1])
            if(p[2]<5999999):
                e_light.append(p[2])
            if(p[3]<5999999):
                e_small.append(p[3])

        f = [min(e_heavy), min(e_tall), max(e_light), max(e_small)]
    if f is not None:
        if f[0] is None or f[0] < w:
            title = title + "Heavy2"
        if f[1] is None or f[1] < h:
            title = title + "Tall2"
        if f[2] is None or f[2] > w:
            title = title + "Light2"
        if f[3] is None or f[3] > h:
            title = title + "Small2"
    if len(title) > 0:
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
        return
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
            msg = f"Successfully processed <b>{success}</b> of <b>{total}</b> messages, and found no upgrades."
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
        results = scan_all_photos(delete=False)
    except Exception as e:
        Config.LOGGER.exception("Exception occurred while scanning.  See log.")
    try:
        send_push(results['success'], results['total'], results['messages'])
    except Exception as e:
        Config.LOGGER.exception("Exception occurred while pushing.  See log.")
