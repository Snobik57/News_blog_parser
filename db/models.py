import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

"""
Модуль в котором описаны модели для базы даных парсера новостных сайтов.
Отношение между таблицами: один-ко-многим
"""

Base = declarative_base()


class Resource(Base):
    """Дочерний класс от declarative_base. Хранит сведения о новостных ресурсах"""
    __tablename__ = 'resource'

    RESOURCE_ID = sq.Column(sq.Integer(), primary_key=True, autoincrement=True)
    RESOURCE_NAME = sq.Column(sq.VARCHAR(255), nullable=True, default=None)
    RESOURCE_URL = sq.Column(sq.VARCHAR(255), nullable=True, default=None)
    top_tag = sq.Column(sq.VARCHAR(255), nullable=False)
    bottom_tag = sq.Column(sq.VARCHAR(255), nullable=False)
    title_cut = sq.Column(sq.VARCHAR(255), nullable=False)
    date_cut = sq.Column(sq.VARCHAR(255), nullable=False)


class Items(Base):
    """Дочерний класс от declarative_base. Хранит сведения о статьях"""
    __tablename__ = 'items'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    res_id = sq.Column(sq.Integer, sq.ForeignKey(Resource.RESOURCE_ID), nullable=False)
    link = sq.Column(sq.VARCHAR(255), nullable=False)
    title = sq.Column(sq.TEXT(), nullable=False)
    content = sq.Column(sq.TEXT(), nullable=False)
    nd_date = sq.Column(sq.BIGINT, nullable=False)
    s_date = sq.Column(sq.BIGINT, default=datetime.now().timestamp())
    not_date = sq.Column(sq.VARCHAR(25), nullable=False)

    res = relationship('Resource', backref='items')


def create_tables(engine):
    """Функция для создания моделей в БД"""
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    pass