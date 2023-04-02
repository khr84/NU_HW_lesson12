from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Table, schema, Float
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///sqlite_orm.db', echo=True)
Base = declarative_base()


class DBRegion(Base):
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True)
    reg_id = Column(Integer, unique=True)
    reg_name = Column(String)

    def __init__(self, id, name):
        self.reg_id = id
        self.reg_name = name


class DBSkill(Base):
    __tablename__ = 'skill'
    skill_id = Column(Integer, primary_key=True)
    skill_name = Column(String, unique=True)

    def __init__(self, name):
        self.skill_name = name


class DBVacancy(Base):
    __tablename__ = 'search_vac'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    count_vac = Column(Integer)
    search_date = Column(String)
    region_id = Column(Integer, ForeignKey('region.id'))
    strict_search = Column(Integer)
    __table_args__ = (schema.UniqueConstraint('name', 'region_id', 'strict_search', name='uc_vac'),)

    def __init__(self, name, count, dt, region_id, strict):
        self.name = name
        self.count_vac = count
        self.search_date = dt
        self.region_id = region_id
        self.strict_search = strict


class DBSalary(Base):
    __tablename__ = 'salary'
    id = Column(Integer, primary_key=True)
    vac_id = Column(Integer, ForeignKey(DBVacancy.id))
    low = Column(Float)
    high = Column(Float)
    count = Column(Integer)

    def __init__(self, id, low, high, cnt):
        self.vac_id = id
        self.low = low
        self.high = high
        self.count = cnt


vac_to_skill = Table('vac_to_skill', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('vac_id', Integer, ForeignKey('search_vac.id')),
    Column('skill_id', Integer, ForeignKey('skill.skill_id')),
    Column('percent', Float)
)

# Создание таблицы
Base.metadata.create_all(engine)
