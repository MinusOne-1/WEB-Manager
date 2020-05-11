import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Parts(SqlAlchemyBase):
    __tablename__ = 'Parts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
    type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Types.id"), nullable=True)
    type_name = orm.relation('Types')
