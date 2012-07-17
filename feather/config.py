# coding: utf-8

import os

_CURRENT_PATH = os.path.dirname(__file__)
_DB_SQLITE_PATH = os.path.join(_CURRENT_PATH, 'feather.sqlite')

_DBUSER = "yetone" # 数据库用户名
_DBPASS = "123" # 数据库密码
_DBHOST = "localhost" # 数据库服务器
_DBNAME = "feather" # 数据库名称

PER_PAGE = 15 # 每页显示主题数目
RE_PER_PAGE = 25 # 每页显示主题回复数目
DEFAULT_TIMEZONE = "Asia/Shanghai" # 默认时区

#_COMM_NAME = "Feather" # 社区名称

class Config(object):
	SECRET_KEY = 'your secret key'
	DEBUG = False
	TESTING = False
	SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % _DB_SQLITE_PATH
	CACHE_TYPE = 'memcached'


class ProConfig(Config):
	SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (_DBUSER, _DBPASS, _DBHOST, _DBNAME)

class DevConfig(Config):
	DEBUG = True

class TestConfig(Config):
	TESTING = True
