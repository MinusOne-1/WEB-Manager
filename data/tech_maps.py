import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class TechMaps(SqlAlchemyBase):
    __tablename__ = 'TechMaps'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_drons = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Drons.id"), nullable=True)
    dron = orm.relation('Drons')

    id_parts = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Parts.id"), nullable=True)
    part = orm.relation('Parts')

    quantity = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
