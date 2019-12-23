from config import Config
from app.move import move


if __name__ == "__main__":
    move.move_files(Config.MOVE_SOURCE_FOLDER, Config.MOVE_DEST_FOLDER, int(Config.MOVE_LIMIT))
