from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from app.data import helpers

Base = declarative_base()


class Pokemon(Base):
    __tablename__ = 'pokemon_stats'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    weight = Column(Integer)
    height = Column(Integer)
    source_type = Column(String, nullable=False)
    source_id = Column(String)
    inserted_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_timestamp = Column(DateTime)
    confidence_data = Column(String)
    extended_attributes = Column(String)

    def __repr__(self):
        return f"<Pokemon(name='{self.name}', weight='{helpers.weight_int_to_str(self.weight)}', " \
               f"height='{helpers.height_int_to_str(self.height)}', " \
               f"id='{self.id}')>"


class Pokemon_Extreme(Base):
    __tablename__ = 'pokemon_extreme'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    extreme_type = Column(String, nullable=False)
    extreme_column = Column(String, nullable=False)
    extreme_value = Column(Integer, nullable=False)
    updated_timestamp = Column(DateTime, default=datetime.utcnow)

    @validates('extreme_type')
    def validate_type(self, key, ext):
        assert ext in ['MIN','MAX']
        return ext

    @validates('extreme_column')
    def validate_column(self, key, col):
        assert col in ['WEIGHT','HEIGHT']
        return col

    def __repr__(self):
        return f"<Pokemon_Extreme(name='{self.name}', {self.extreme_type}='{self.extreme_value}', " \
               f"updated_timestamp='{self.updated_timestamp}')>"
