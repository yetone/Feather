# coding: utf-8
# all the imports
import os
import time
import re
from hashlib import md5
from flask import Flask, session, g
from flaskext.markdown import Markdown
from feather.views import account, node, topic, reply, timesystem, city, love, blog
from feather.extensions import db, cache
from feather.helpers import mentions
from feather import config
from feather.databases import Bill, Bank, City, User, Nodeclass, Node, \
		Topic, Reply, Notify
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)
#app.config.from_object('feather.config.DevConfig') # SQLite
app.config.from_object('feather.config.ProConfig') # MySQL
app.config.from_envvar('FEATHER_SETTINGS', silent=True)

Markdown(app)

app.register_module(blog)
app.register_module(love)
app.register_module(topic)
app.register_module(account)
app.register_module(reply)
app.register_module(node)
app.register_module(city)
app.register_module(timesystem)

db.init_app(app)
cache.init_app(app)

@app.before_request
def before_request():
	g.un = 1
	g.user = None
	g.notify = 0
	if 'user_id' in session:
		g.user = User.query.get(session['user_id'])
		g.notify_read = []
		g.notify_unread = []
		if Notify.query.filter_by(author=g.user).all():
			g.notify_read = Notify.query.filter_by(author=g.user).filter_by(status=0).order_by(Notify.date.desc())
			g.notify_unread = Notify.query.filter_by(author=g.user).filter_by(status=1).order_by(Notify.date.desc()).all()
			if g.notify_unread == []:
				g.un = 0
			g.notify = len(g.notify_unread)


# filters
@app.template_filter('getday')
def get_day(timestamp):
	FORY = '%d'
	os.environ["TZ"] = config.DEFAULT_TIMEZONE
	time.tzset()
	str = time.strftime(FORY, time.localtime(timestamp))
	return str

@app.template_filter('getmonth')
def get_month(timestamp):
	FORY = '%m'
	os.environ["TZ"] = config.DEFAULT_TIMEZONE
	time.tzset()
	str = time.strftime(FORY, time.localtime(timestamp))
	return str

@app.template_filter('getsome')
def get_some(text):
	return text

@app.template_filter('datetimeformat')
def format_datetime(timestamp):
	FORY = '%Y-%m-%d @ %H:%M'
	FORM = '%m-%d @ %H:%M'
	FORH = '%H:%M'
	os.environ["TZ"] = config.DEFAULT_TIMEZONE
	time.tzset()
	rtime = time.strftime(FORM, time.localtime(timestamp))
	htime = time.strftime(FORH, time.localtime(timestamp))
	now = int(time.time())
	t = now - timestamp
	if t < 60:
		str = '刚刚'
	elif t < 60 * 60:
		min = t / 60
		str = '%d 分钟前' % min
	elif t < 60 * 60 * 24:
		h = t / (60 * 60)
		str = '%d 小时前 %s' % (h,htime)
	elif t < 60 * 60 * 24 * 3:
		d = t / (60 * 60 * 24)
		if d == 1:
			str = '昨天 ' + rtime
		else:
			str = '前天 ' + rtime
	else:
		str = time.strftime(FORY, time.localtime(timestamp))
	return str

@app.template_filter('datetimeformat2')
def format_datetime2(timestamp):
	FORY = '%Y-%m-%d @ %H:%M'
	os.environ["TZ"] = config.DEFAULT_TIMEZONE
	time.tzset()
	str = time.strftime(FORY, time.localtime(timestamp))
	return str

@app.template_filter('gravatarbig')
def gravatar_url(email):
	return 'http://gravatar.com/avatar/%s?d=identicon&s=%d&d=http://feather.im/static/img/gravatar.png' % \
			(md5(email.strip().lower().encode('utf-8')).hexdigest(), 128)

@app.template_filter('gravatar')
def gravatar_url(email, size=48):
	return 'http://gravatar.com/avatar/%s?d=identicon&s=%d&d=http://feather.im/static/img/gravatar.png' % \
			(md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

@app.template_filter('gravatarmini')
def gravatarmini_url(email):
	return 'http://gravatar.com/avatar/%s?d=identicon&s=%d&d=http://feather.im/static/img/gravatar.png' % \
			(md5(email.strip().lower().encode('utf-8')).hexdigest(), 24)


@app.template_filter('emailtobase64')
def email_to_base64(email):
	import base64
	return base64.encodestring(email)

@app.template_filter('gettopnumber')
def get_top_number(user_id):
	users = User.query.filter_by(topswitch=1).order_by(User.time.desc()).limit(26)
	i = 0
	while True:
		if user_id == users.all()[i].id:
			break
		i = i + 1
	return i+1

@app.template_filter('getbanktime')
def get_bank_time(time):
	hours = time/60
	minute = time%60
	day = hours/24
	hour = hours%24
	return '%d天%02d时%02d分' % (day,hour,minute)

@app.template_filter('getuserid')
def get_user_id(username):
	rv = User.query.filter_by(name=username).first()
	return rv.id if rv else None

@app.template_filter('getuserdescription')
def get_user_descriptin(user_id):
	rv = User.query.get(user_id)
	return rv.description if rv.description else ''

@app.template_filter('getuseridfromemail')
def get_user_id_from_email(email):
	rv = User.query.filter_by(email=email).first()
	return rv.id if rv else None

@app.template_filter('getuseremail')
def get_user_email(user_id):
	rv = User.query.get(user_id)
	return rv.email if rv else None

@app.template_filter('getusername')
def get_user_name(user_id):
	if user_id:
		rv = User.query.get(user_id)
		return rv.name if rv else None
	else:
		return 'yetone'

@app.template_filter('getusertimeswitch')
def get_user_switch(user_id):
	rv = User.query.get(user_id)
	switch = rv.timeswitch
	return switch

@app.template_filter('getuserhour')
def get_user_hour(user_id):
	rv = User.query.get(user_id)
	hour = rv.time/60
	return '%02d' % hour

@app.template_filter('getuserminute')
def get_user_minute(user_id):
	rv = User.query.get(user_id)
	minute = rv.time%60
	return '%02d' % minute

@app.template_filter('getbalancehour')
def get_balance_hour(balance):
	hour = balance/60
	return '%02d' % hour

@app.template_filter('getbalanceminute')
def get_balance_minute(balance):
	minute = balance%60
	return '%02d' % minute

@app.template_filter('gettopiclastreply')
def get_topic_last_reply(topic_id):
	rv = Topic.query.get(topic_id).replys.order_by(Reply.date.asc())
	return rv[-1] if rv.first() else None

@app.template_filter('gettopiclastreplyid')
def get_topic_last_reply_id(topic_id):
	rv = Topic.query.get(topic_id).replys.order_by(Reply.date.asc())
	last_reply = rv[-1]
	return last_reply.id

@app.template_filter('gettopicauthorname')
def get_topic_author_name(topic_id):
	return Topic.query.get(topic_id).author.name

@app.template_filter('gettopicauthoremail')
def get_topic_author_email(topic_id):
	return Topic.query.get(topic_id).author.email

@app.template_filter('gettopicreplycount')
def get_topic_reply_count(topic_id):
	count = 0
	rv = Topic.query.get(topic_id).replys.all()
	if rv:
		count = len(rv)
	return count


@app.template_filter('getreplyauthorid')
def get_reply_author_id(reply_id):
	rv = Reply.query.get(reply_id)
	return rv.author_id


@app.template_filter('getreplydate')
def get_reply_date(reply_id):
	rv = Reply.query.get(reply_id)
	return rv.date


@app.template_filter('getreplytext')
def get_reply_text(reply_id):
	rv = Reply.query.get(reply_id)
	return rv.text
'''
def re_tuple(tuple):
	return list(tuple)[0]
'''
@app.template_filter('getreplythankerscount')
def get_reply_thankers_count(reply_id):
	rv = Reply.query.get(reply_id)
	return len(rv.thankers.all())

