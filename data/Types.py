import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Types(SqlAlchemyBase):
    __tablename__ = 'Types'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
