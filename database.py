import os
import sys
from flask_sqlalchemy import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class SuperMart(Base):
    __tablename__ = 'supermart'
    id = Column(Integer, primary_key=True)
    category = Column(String(60), nullable=False)


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(300), nullable=True)
    price = Column(String(10))
    offer = Column(String(100), nullable=True)
    supermart_category_id = Column(Integer, ForeignKey('supermart.id'))
    supermart = relationship(SuperMart)


engine = create_engine('sqlite:///supermart.db')
Base.metadata.create_all(engine)
