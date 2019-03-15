from flask import Flask
from config import Config

from models import User, Event

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

coffee = Flask(__name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
session = sessionmaker(bind=engine)()

# create engine
m = User.__table__.metadata
m.bind = engine
m.create_all()

from coffee import routes, models
