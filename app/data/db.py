from . import Session
from app.data.models import Pokemon as db_poke
from app.data.models import Pokemon_Extreme
from app.pokemon.Pokemon import Pokemon as logical_poke
from datetime import datetime, timedelta
from config import Config
from sqlalchemy import func, Column, and_
from sqlalchemy.sql.expression import desc


def insert_pokemon(poke: logical_poke, source_type: str = None, source_id: str = None,
                   created_timestamp: datetime = None,
                   confidence_data: str = None, extended_attributes: str = None,
                   session = None, commit = True):
    if session:
        s = session
    else:
        s = Session()
    try:
        dbpk = convert_logical_to_db_poke(poke, source_type=source_type, source_id=source_id,
                                          created_timestamp=created_timestamp, confidence_data=confidence_data,
                                          extended_attributes=extended_attributes)
        s.add(dbpk)
        if commit:
            s.commit()
    except Exception as e:
        Config.LOGGER.exception("")
        raise e
    finally:
        if commit:
            s.close()


def convert_logical_to_db_poke(poke: logical_poke, source_type=None, source_id=None, created_timestamp=None,
                               confidence_data=None, extended_attributes=None) -> db_poke:
    ret = db_poke(name=poke.name, weight=poke.weight, height=poke.height, source_type=source_type, source_id=source_id,
                  created_timestamp=created_timestamp, confidence_data=confidence_data,
                  extended_attributes=extended_attributes)
    return ret


def update_extreme(name, extreme_col, minmax, timestamp, value, session=None, commit = True):
    if session:
        s = session
    else:
        s = Session()
    try:
        ext = s.query(Pokemon_Extreme).filter_by(name=name, extreme_type=minmax, extreme_column=extreme_col).first()
        if not ext:
            ext = Pokemon_Extreme(name=name, extreme_type=minmax, extreme_column=extreme_col,
                                  updated_timestamp=timestamp,
                                  extreme_value=value)
            s.add(ext)
        else:
            ext.extreme_value = value
            ext.updated_timestamp = timestamp
        if commit:
            s.commit()
    except Exception as e:
        Config.LOGGER.exception("")
    finally:
        if commit:
            s.close()


def convert_db_to_logical_poke(poke: db_poke) -> logical_poke:
    ret = logical_poke(name=poke.name, weight=poke.weight, height=poke.height)
    return ret


def get_max_weight_by_name(name: str) -> int:
    # returns max weight for given pokemon; returns None if not found
    ext = get_extreme_from_extreme_by_name(name, "WEIGHT", "MAX", full=True)
    if ext:
        ts = ext.updated_timestamp
        ext_weight = ext.extreme_value
    else:
        ts = datetime.min
        ext_weight = -1
    stat = get_extreme_from_stats_by_name(name, db_poke.weight, func.max, ts=ts)
    if stat is not None and stat >= ext_weight:
        update_extreme(name, "WEIGHT", "MAX", (datetime.utcnow() - timedelta(days=1)), stat)
        ext_weight = stat
    return ext_weight
    # get_extreme_by_name(name, db_poke.weight, func.max)


def get_min_weight_by_name(name: str) -> int:
    ext = get_extreme_from_extreme_by_name(name, "WEIGHT", "MIN", full=True)
    if ext:
        ts = ext.updated_timestamp
        ext_weight = ext.extreme_value
    else:
        ts = datetime.min
        ext_weight = 1000000000
    stat = get_extreme_from_stats_by_name(name, db_poke.weight, func.min, ts=ts)
    if stat is not None and stat <= ext_weight:
        update_extreme(name, "WEIGHT", "MIN", (datetime.utcnow() - timedelta(days=1)), stat)
        ext_weight = stat
    return ext_weight


def get_max_height_by_name(name: str) -> int:
    ext = get_extreme_from_extreme_by_name(name, "HEIGHT", "MAX", full=True)
    if ext:
        ts = ext.updated_timestamp
        ext_height = ext.extreme_value
    else:
        ts = datetime.min
        ext_height = -1
    stat = get_extreme_from_stats_by_name(name, db_poke.height, func.max, ts=ts)
    if stat is not None and stat >= ext_height:
        update_extreme(name, "HEIGHT", "MAX", (datetime.utcnow() - timedelta(days=1)), stat)
        ext_height = stat
    return ext_height
    # return get_extreme_by_name(name, db_poke.height, func.max)


def get_min_height_by_name(name: str) -> int:
    ext = get_extreme_from_extreme_by_name(name, "HEIGHT", "MIN", full=True)
    if ext:
        ts = ext.updated_timestamp
        ext_height = ext.extreme_value
    else:
        ts = datetime.min
        ext_height = 1000000000
    stat = get_extreme_from_stats_by_name(name, db_poke.height, func.min, ts=ts)
    if stat is not None and stat <= ext_height:
        update_extreme(name, "HEIGHT", "MIN", (datetime.utcnow() - timedelta(days=1)), stat)
        ext_height = stat
    return ext_height
    # return get_extreme_by_name(name, db_poke.height, func.min)


def get_extreme_from_extreme_by_name(name: str, col: str, minmax: str, full=False) -> int:
    try:
        s = Session()
        if full:
            query = s.query(Pokemon_Extreme).filter_by(name=name, extreme_type=minmax, extreme_column=col)
        else:
            query = s.query(Pokemon_Extreme.extreme_value).filter_by(name=name, extreme_type=minmax, extreme_column=col)
    except Exception as e:
        Config.LOGGER.exception("")
    finally:
        s.close()
    return query.first()


def get_extreme_from_stats_by_name(name: str, col, func, ts=datetime.min) -> int:
    try:
        s = Session()
        query = s.query(func(col)).filter(db_poke.inserted_timestamp > ts).filter_by(name=name)
    except Exception as e:
        Config.LOGGER.exception("")
    finally:
        s.close()
    return query.first()[0]


def get_extreme_last_updated_ts(name:str) -> str:
    try:
        s = Session()
        query = s.query(Pokemon_Extreme).filter_by(name=name).order_by(desc('updated_timestamp'))
    except Exception as e:
        Config.LOGGER.exception("")
    finally:
        s.close()
    return query.first().updated_timestamp