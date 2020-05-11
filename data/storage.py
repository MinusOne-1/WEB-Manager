import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Storage(SqlAlchemyBase):
    __tablename__ = 'Storage'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    id_parts = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Parts.id"), nullable=True)
    part = orm.relation('Parts')

    serial_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)