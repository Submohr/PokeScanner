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
    MOVE_LIMIT = os.environ.get('MOVE_LIMIT') or 30

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
    TESSDATA_DIR_CONFIG = f'--tessdata-dir "{TESSDATA_DIR}"'
    TESSDATA_CUSTOM_DICT = True if os.environ.get('TESSDATA_CUSTOM_DICT') else False

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

    INSERT_INTO_DB = True if os.environ.get("INSERT_INTO_DB") else False
    INSERT_INTO_TXT = True if os.environ.get("INSERT_INTO_TXT") else False
    DATA_SOURCE = os.environ.get("SOURCE") or "DB"

    try:
        handler = RotatingFileHandler("/".join([LOG_FOLDER,LOG_NAME]), maxBytes=102400, backupCount=10)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        LOGGER.addHandler(handler)
        LOGGER.info("Logger initialized.")
    except:
        LOGGER.addHandler(logging.NullHandler())
