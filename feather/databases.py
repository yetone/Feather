# coding: utf-8
import time
from feather.extensions import db

# databases
favorites = db.Table('favorites',
		db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
		db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'))
		)

votes = db.Table('votes',
		db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
		db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'))
		)

thanks = db.Table('thanks',
		db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
		db.Column('reply_id', db.Integer, db.ForeignKey('reply.id'))
		)

reads = db.Table('reads',
		db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
		db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'))
)

class Bill(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
	reply_id = db.Column(db.Integer, db.ForeignKey('reply.id'))
	user_id = db.Column(db.Integer)
	time = db.Column(db.Integer)
	balance = db.Column(db.Integer)
	type = db.Column(db.Integer)
	date = db.Column(db.Integer)

	def __init__(self, author, time, balance, type, date, topic=None, reply=None, user_id=None):
		self.author = author
		self.topic = topic
		self.reply = reply
		self.user_id = user_id
		self.time = time
		self.balance = balance
		self.type = type
		self.date = date

	def __repr__(self):
		return '<Bill %r>' % (self.id)

class Bank(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.Integer)

	def __init__(self,time):
		self.time = time

	def __repr__(self):
		return '<Bank %r>' % (self.time)

class City(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=True)
	site = db.Column(db.String(50), unique=True)
	description = db.Column(db.Text)
	users = db.relationship('User', backref='city', lazy='dynamic')

	def __init__(self, name):
		self.name = name
		self.site = name
		self.description = u''

	def __repr__(self):
		return '<City %r>' % (self.name)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=True)
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120))
	time = db.Column(db.Integer)
	timeswitch = db.Column(db.Integer)
	topswitch = db.Column(db.Integer)
	emailswitch = db.Column(db.Integer)
	timetop = db.Column(db.Integer)
	usercenter = db.Column(db.String(50), unique=True)
	status = db.Column(db.Integer)
	steam_id = db.Column(db.Integer)
	description = db.Column(db.Text)
	website = db.Column(db.Text)
	date = db.Column(db.Integer)
	tab_id = db.Column(db.Integer)
	topics = db.relationship('Topic', backref='author', lazy='dynamic')
	replys = db.relationship('Reply', backref='author', lazy='dynamic')
	bills = db.relationship('Bill', backref='author', lazy='dynamic')
	notifications = db.relationship('Notify', backref='author', lazy='dynamic')
	favorites = db.relationship('Topic', secondary=favorites,
			backref=db.backref('followers', lazy='dynamic'))
	votes = db.relationship('Topic', secondary=votes,
			backref=db.backref('voters', lazy='dynamic'))
	thanks = db.relationship('Reply', secondary=thanks,
			backref=db.backref('thankers', lazy='dynamic'))
	city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
	reads = db.relationship('Topic', secondary=reads,
			backref=db.backref('readers', lazy='dynamic'))

	def __init__(self, name, email, password, time, date):
		self.name = name
		self.email = email
		self.password = password
		self.time = time
		self.timeswitch = 1
		self.timetop = 1
		self.topswitch = 1
		self.emailswitch = 1
		self.usercenter = name
		self.status = 1
		self.steam_id = 1
		self.description = u''
		self.website = u''
		self.date = date
		self.tab_id = -1
	

	def get_gravatar_url(self, size=80):
		return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
				(md5(self.email.strip().lower().encode('utf-8')).hexdigest(), size)


	def __repr__(self):
		return '<User %r>' % (self.name)


class Nodeclass(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=True)
	description = db.Column(db.Text)
	nodes = db.relationship('Node', backref='nodeclass', lazy='dynamic')
	topics = db.relationship('Topic', backref='nodeclass', lazy='dynamic')
	status = db.Column(db.Integer)

	def __init__(self, name):
		self.name = name
		self.description = u''
		self.status = 1

	def __repr__(self):
		return '<Nodeclass %r>' % self.name


class Node(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=True)
	site = db.Column(db.String(50), unique=True)
	description = db.Column(db.Text)
	header = db.Column(db.Text)
	description_origin = db.Column(db.Text)
	header_origin = db.Column(db.Text)
	nodeclass_id = db.Column(db.Integer, db.ForeignKey('nodeclass.id'))
	topics = db.relationship('Topic', backref='node', lazy='dynamic')
	status = db.Column(db.Integer)
	date = db.Column(db.Integer)
	style = db.Column(db.Text)

	def __init__(self, name, site, description, description_origin, nodeclass, style=None):
		self.name = name
		self.site = site
		self.description = description
		self.description_origin = description_origin
		self.header = u''
		self.header_origin = u''
		self.status = 1
		self.date = int(time.time())
		self.nodeclass = nodeclass

	def __repr__(self):
		return '<Node %r>' % self.name


class Topic(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	notify = db.relationship('Notify', backref='topic', lazy='dynamic', uselist=False)
	title = db.Column(db.String(80))
	text = db.Column(db.Text)
	text_origin = db.Column(db.Text)
	replys = db.relationship('Reply', backref='topic', lazy='dynamic')
	bills = db.relationship('Bill', backref='topic', uselist=False, lazy='dynamic')
	node_id = db.Column(db.Integer, db.ForeignKey('node.id'))
	nodeclass_id = db.Column(db.Integer, db.ForeignKey('nodeclass.id'))
	vote = db.Column(db.Integer)
	report = db.Column(db.Integer)
	date = db.Column(db.Integer)
	last_reply_date = db.Column(db.Integer)
	reply_count = db.Column(db.Integer)

	def __init__(self, author, title, text, text_origin, node, reply_count, report=0):
		self.author = author
		self.title = title
		self.text = text
		self.text_origin = text_origin
		self.node = node
		self.nodeclass = node.nodeclass
		self.vote = 0
		self.report = report
		self.date = int(time.time())
		self.last_reply_date = int(time.time())
		self.reply_count = reply_count

	def get_reply_count(self):
		return len(self.replys.all()) if self.replys else 0

	def __repr__(self):
		return '<Topic %r>' % self.title


class Reply(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	notify = db.relationship('Notify', backref='reply', lazy='dynamic')
	text = db.Column(db.Text)
	text_origin = db.Column(db.Text)
	bills = db.relationship('Bill', backref='reply', uselist=False, lazy='dynamic')
	date = db.Column(db.Integer)
	number = db.Column(db.Integer)
	type = db.Column(db.Integer)

	def __init__(self, topic, author, text, text_origin, number=1, type=0):
		self.topic = topic
		self.author = author
		self.text = text
		self.text_origin = text_origin
		self.date = int(time.time())
		self.number = number
		self.type = type

	def __repr__(self):
		return '<Reply %r>' % self.text

class Notify(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	status = db.Column(db.Integer)
	topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
	reply_id = db.Column(db.Integer, db.ForeignKey('reply.id'))
	type = db.Column(db.Integer)
	date = db.Column(db.Integer)

	def __init__(self, author, topic, reply, type):
		self.author = author
		self.status = 1
		self.topic = topic
		self.reply = reply
		self.type = type
		self.date = int(time.time())

	def __repr__(self):
		return '<Notify %r>' % self.id

