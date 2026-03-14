from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class IOAccess(Base):
    __tablename__ = 'io_access'

    id = Column(Integer, primary_key=True, autoincrement=True)
    access_name = Column(String, nullable=False)
    application = Column(String)
    topic = Column(String)
    advise_active = Column(String)
    dde_protocol = Column(String)
    sec_application = Column(String)
    sec_topic = Column(String)
    sec_advise_active = Column(String)
    sec_dde_protocol = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class IODisc(Base):
    __tablename__ = 'io_disc'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String)
    comment = Column(String)
    access_name = Column(String)
    item_name = Column(String)


class IOInt(Base):
    __tablename__ = 'io_int'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String)
    comment = Column(String)
    eng_units = Column(String)
    min_value = Column(Float)
    max_value = Column(Float)
    lolo_alarm_state = Column(Integer)
    lolo_alarm_value = Column(Float)
    lolo_alarm_pri = Column(Integer)
    lo_alarm_state = Column(Integer)
    lo_alarm_value = Column(Float)
    lo_alarm_pri = Column(Integer)
    hi_alarm_state = Column(Integer)
    hi_alarm_value = Column(Float)
    hi_alarm_pri = Column(Integer)
    hihi_alarm_state = Column(Integer)
    hihi_alarm_value = Column(Float)
    hihi_alarm_pri = Column(Integer)
    access_name = Column(String)
    item_name = Column(String)


class IOReal(Base):
    __tablename__ = 'io_real'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String)
    comment = Column(String)
    eng_units = Column(String)
    min_eu = Column(Float)
    max_eu = Column(Float)
    lolo_alarm_state = Column(Integer)
    lolo_alarm_value = Column(Float)
    lolo_alarm_pri = Column(Integer)
    lo_alarm_state = Column(Integer)
    lo_alarm_value = Column(Float)
    lo_alarm_pri = Column(Integer)
    hi_alarm_state = Column(Integer)
    hi_alarm_value = Column(Float)
    hi_alarm_pri = Column(Integer)
    hihi_alarm_state = Column(Integer)
    hihi_alarm_value = Column(Float)
    hihi_alarm_pri = Column(Integer)
    access_name = Column(String)
    item_name = Column(String)


def init_engine(db_path: str):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()