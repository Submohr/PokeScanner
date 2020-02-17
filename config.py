import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir,'.env'))


class Config(object):
    SOURCE_FOLDER = os.environ.get('SOURCE_FOLDER')

    PUSHOVER_TOKEN = os.environ.get('PUSHOVER_TOKEN')
    PUSHOVER_USER = os.environ.get('PUSHOVER_USER')

    MOVE_SOURCE_FOLDER = os.environ.get('MOVE_SOURCE_FOLDER')
    MOVE_DEST_FOLDER = os.environ.get('SCAN_FOLDER')
    MOVE_LIMIT = int(os.environ.get('MOVE_LIMIT') or 30)

    SCAN_SOURCE_FOLDER = os.environ.get('SCAN_FOLDER')
    SCAN_ERROR_FOLDER = os.environ.get('SCAN_ERROR_FOLDER')
    try:
        if not os.path.isdir(SCAN_ERROR_FOLDER):
            os.mkdir(SCAN_ERROR_FOLDER)
    except:
        pass
    SCAN_PROCESSED_FOLDER = os.environ.get('SCAN_PROCESSED_FOLDER')
    try:
        if not os.path.isdir(SCAN_PROCESSED_FOLDER):
            os.mkdir(SCAN_PROCESSED_FOLDER)
    except:
        pass

    TESSDATA_DIR = os.environ.get('TESSDATA_DIR')
    TESSDATA_CONFIG_NAME = f'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:-2♀♂ -psm 7 --tessdata-dir "{TESSDATA_DIR}"'
    TESSDATA_CONFIG_NUMBERS = f'-c tessedit_char_whitelist=mkg.0123456789 -psm 7 --tessdata-dir "{TESSDATA_DIR}"'
    TESSDATA_CONFIG_DEFAULT = f'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:-.0123456789♀♂ -psm 7 --tessdata-dir "{TESSDATA_DIR}"'

    TESSDATA_CUSTOM_DICT = os.environ.get('TESSDATA_CUSTOM_DICT') == "True"

    LOG_LEVEL = os.environ.get('LOG_LEVEL') or "DEBUG"
    LOG_FOLDER = os.environ.get('LOG_FOLDER')
    LOG_NAME = os.environ.get('LOG_NAME')

    LOGGER = logging.getLogger("Rotating Log")
    LOGGER.setLevel(LOG_LEVEL)

    SQL_DB_LOCATION = os.environ.get('SQL_DB_LOCATION')
    FLAT_FILE_DIR = os.environ.get('FLAT_FILE_DIR')

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + \
                              os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    INSERT_INTO_DB = os.environ.get("INSERT_INTO_DB") == "True"
    INSERT_INTO_TXT = os.environ.get("INSERT_INTO_TXT") == "True"
    DATA_SOURCE = os.environ.get("SOURCE") or "DB"

    DISCORD_DEBUG_MODE = os.environ.get("DISCORD_DEBUG_MODE") == "True"
    DISCORD_DEBUG_CHANNEL = int(os.environ.get("DISCORD_DEBUG_CHANNEL") or 0)
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
    DISCORD_SIZE_CHANNEL = os.environ.get("DISCORD_SIZE_CHANNEL")
    DISCORD_MAX_MESSAGE_LENGTH = int(os.environ.get("DISCORD_MAX_MESSAGE_LENGTH") or 1800)

    try:
        handler = RotatingFileHandler("/".join([LOG_FOLDER,LOG_NAME]), maxBytes=102400, backupCount=10)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        LOGGER.addHandler(handler)
        LOGGER.info("Logger initialized.")
    except:
        LOGGER.addHandler(logging.NullHandler())
