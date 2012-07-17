# coding: utf-8

from flask_sqlalchemy import SQLAlchemy
from flaskext.cache import Cache

db = SQLAlchemy()
cache = Cache()
