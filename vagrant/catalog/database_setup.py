import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Table to hold user info
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)    
    picture = Column(String(250))


# Table that will separate the items into different categories
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Return the category in a serializable format
        return {
            'id' : self.id,
            'name' : self.name
        }

# Table for items
class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    description = Column(String(250))
    picture = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref = "items")

    @property
    def serialize(self):
        # Return the item in a serializable format
        return {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,
            'picture' : self.picture,
            'category' : self.category.name
        }


engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.create_all(engine)
