# coding: utf-8
import time
from flask import Module, request, session, g, redirect, url_for, \
		abort, render_template, flash
from flask_sqlalchemy import Pagination
from feather import config
from feather.extensions import db, cache
from feather.databases import Bill, Bank, User, Nodeclass, Node, \
		Topic, Reply


topic = Module(__name__)

@cache.cached(60 * 60, key_prefix='liketopics/%d')
def get_liketopics(topicid):
	topic = Topic.query.get(topicid)
	liketopics = []
	i = 0
	for n in Topic.query.all():
		if i == 6:
			break
		if liketopic(topic.title,n.title) == 0:
			liketopics += [n]
			i += 1
			continue
		elif liketopic(topic.title,n.title) == 1:
			liketopics += [n]
			i += 1
			continue
		elif liketopic(topic.title,n.title) == 2:
			liketopics += [n]
			i += 1
			continue
		rv = liketopics
	return rv

@cache.cached(600, key_prefix='sitestatus')
def get_sitestatus():
	usercount = 0
	topiccount = 0
	replycount = 0
	if User.query.all():
		usercount = len(User.query.all())
	if Topic.query.all():
		topiccount = len(Topic.query.all())
	if Reply.query.all():
		replycount = len(Reply.query.all())
	rv = (usercount, topiccount, replycount)
	return rv

@cache.cached(1200, key_prefix='hottopics')
def get_hottopics():
	nowtime = int(time.time())
	agotime = nowtime - 24*60*60
	rv = Topic.query.filter(Topic.date <= nowtime).filter(Topic.date >= agotime).order_by(Topic.reply_count.desc()).limit(10).all()
	return rv

@cache.cached(600, key_prefix='view/%s')
def get_nodeclass(tabname):
	return Nodeclass.query.filter_by(name=tabname).first()


def liketopic(a,b):
	import difflib
	return len(filter(lambda i: i.startswith('+'), difflib.ndiff(a,b)))

class Getdate:
	def __init__(self, time):
		self.time = time
	def year(self):
		return int(time.strftime('%Y', time.localtime(self.time)))
	def month(self):
		return int(time.strftime('%m', time.localtime(self.time)))
	def day(self):
		return int(time.strftime('%d', time.localtime(self.time)))


@topic.route('/<tabname>', defaults={'page': 1})
@topic.route('/index', defaults={'page': 1, 'tabname': 'All'})
@topic.route('/page/<int:page>', defaults={'tabname': 'All'})
@topic.route('/<tabname>/page/<int:page>')
@cache.cached(timeout=60 * 5, unless= lambda: g.user is not None)
def index(page, tabname):
	(usercount, topiccount, replycount) = get_sitestatus()
	hottopics = get_hottopics()
	nodeclasses = Nodeclass.query.all()
	nodeclass = get_nodeclass(tabname)
	if tabname == 'All':
		page_obj = Topic.query.filter_by(report=0).order_by(Topic.last_reply_date.desc()).paginate(page, per_page=config.PER_PAGE)
		page_url = lambda page: url_for("topic.index", page=page, tabname='All')
	elif nodeclass is None:
		tabname = 'Geek'
		nodeclass = get_nodeclass(tabname)
		page_obj = Topic.query.filter_by(report=0).filter_by(nodeclass=nodeclass).order_by(Topic.last_reply_date.desc()).paginate(page, per_page=config.PER_PAGE)
		page_url = lambda page: url_for("topic.index", page=page, tabname='Geek')
	else:
		page_obj = Topic.query.filter_by(report=0).filter_by(nodeclass=nodeclass).order_by(Topic.last_reply_date.desc()).paginate(page, per_page=config.PER_PAGE)
		page_url = lambda page: url_for("topic.index", page=page, tabname=nodeclass.name)
	return render_template('index.html', page_obj=page_obj, page_url=page_url, nodeclasses=nodeclasses, nodeclass=nodeclass, usercount=usercount, topiccount=topiccount, replycount=replycount, hottopics=hottopics, tabname=tabname)

@topic.route('/', defaults={'tabname': 'index'})
@topic.route('/tab/<tabname>')
def tab_view(tabname):
	if not session.get('user_id'):
		if tabname == 'index':
			return redirect(url_for('topic.index', tabname='Geek'))
		else:
			return redirect(url_for('topic.index', tabname=tabname))
	if tabname == 'index' and session.get('user_id'):
		if g.user.tab_id == 0:
			return redirect(url_for('topic.index', tabname='All'))
		elif g.user.tab_id != -1:
			nodeclass = Nodeclass.query.get(g.user.tab_id)
			return redirect(url_for('topic.index', tabname=nodeclass.name))
		else:
			return redirect(url_for('topic.index', tabname='Geek'))
	else:
		nodeclass = Nodeclass.query.filter_by(name=tabname).first()
		if nodeclass is not None and session.get('user_id'):
			g.user.tab_id = nodeclass.id
			db.session.commit()
			return redirect(url_for('topic.index', tabname=tabname))
		elif tabname == 'all' or tabname == 'All':
			g.user.tab_id = 0
			db.session.commit()
			return redirect(url_for('topic.index', tabname='All'))

@topic.route('/add/<nodesite>', methods=['GET', 'POST'])
def topic_add(nodesite):
	if not session.get('user_id'):
		return redirect(url_for('account.login'))
	node = Node.query.filter_by(site=nodesite).first()
	if request.method == 'POST':
		if g.user.time < 20:
			flash(u'时间不足20分钟！')
			return redirect(url_for('topic.index'))
		node = Node.query.filter_by(site=nodesite).first()
		if request.form['title'] == '':
			g.error = u'请输入主题标题！'
			render_template('topic_add.html', node=node)
		elif request.form['text'] == '':
			g.error = u'请输入主题内容！'
			render_template('topic_add.html', node=node)
		else:
			topic = Topic(author=g.user, title=request.form['title'], text=request.form['text'], node=node, reply_count=0)
			bank = Bank.query.get(1)
			g.user.time -= 20
			bank.time +=20
			db.session.add(topic)
			db.session.commit()
			topic = Topic.query.filter_by(title=unicode(request.form['title'])).first()
			bill = Bill(author=g.user,time=20,type=2,date=int(time.time()),topic=topic,balance=g.user.time)
			db.session.add(bill)
			db.session.commit()
			flash(u'发布成功！')
			return redirect(url_for('topic.topic_view', topic_id=topic.id))
	return render_template('topic_add.html', node=node)


@topic.route('/del/<int:topic_id>')
def del_topic(topic_id):
	topic = Topic.query.get(topic_id)
	replys = topic.replys.all()
	if replys:
		for reply in replys:
			db.session.delete(reply)
	db.session.delete(topic)
	db.session.commit()
	flash(u'成功删除一条记录！')
	return redirect(url_for('topic.index'))


@topic.route('/topic/<int:topic_id>/edit', methods=['GET', 'POST'])
def topic_edit(topic_id):
	topic = Topic.query.get(topic_id)
	if session.get('user_id') == topic.author.id or session.get('user_id') == 1:
		if request.method == 'POST':
			if not session.get('user_id'):
				abort(401)
			if request.form['title'] == '':
				g.error = u'请输入主题标题！'
				render_template('topic_edit.html', topic=topic)
			elif request.form['text'] == '':
				g.error = u'请输入主题内容！'
				render_template('topic_edit.html', topic=topic)
			else:
				topic = Topic.query.get(topic_id)
				topic.title = request.form['title']
				topic.text = request.form['text']
				topic.date = int(time.time())
				db.session.commit()
				flash(u'修改成功！')
				return redirect(url_for('topic.topic_view',topic_id=topic_id))
		return render_template('topic_edit.html', topic=topic)
	else:
		abort(401)


@topic.route('/topic/<int:topic_id>', defaults={'page': 1})
@topic.route('/topic/<int:topic_id>/page/<int:page>')
def topic_view(topic_id, page):
	topic = Topic.query.get(topic_id)
	liketopics = get_liketopics(topic.id)
	page_obj = topic.replys.order_by(Reply.date.asc()).paginate(page, per_page=config.RE_PER_PAGE)
	page_url = lambda page: url_for("topic.topic_view", topic_id=topic_id, page=page)
	if g.user:
		if topic not in g.user.reads:
			g.user.reads += [topic]
			db.session.commit()
	return render_template('topic_view.html', topic=topic, liketopics=liketopics, page_obj=page_obj, page_url=page_url, page=page)



@topic.route('/topic/<int:topic_id>/fav')
def fav(topic_id):
	if not session.get('user_id'):
		abort(401)
	topic = Topic.query.get(topic_id)
	user = g.user
	if topic in user.favorites:
		return redirect(url_for('topic.topic_view', topic_id=topic.id) + "#fav")
	else:
		user.favorites += [topic]
		db.session.commit()
		return redirect(url_for('topic.topic_view', topic_id=topic.id) + "#topic")

@topic.route('/topic/<int:topic_id>/vote')
def vote(topic_id):
	if not session.get('user_id'):
		abort(401)
	topic = Topic.query.get(topic_id)
	user = g.user
	if topic in user.votes:
		return redirect(url_for('topic.topic_view', topic_id=topic.id) + "#;")
	else:
		user.votes += [topic]
		topic.vote += 1
		if topic.vote >= 10:
			topic.report = 1
		db.session.commit()
		flash(u'已举报，谢谢参与社区建设。')
		return redirect(url_for('topic.topic_view', topic_id=topic.id) + "#;")


@topic.route('/trash', defaults={'page': 1})
@topic.route('/trash/page/<int:page>')
def trash(page):
	page_obj = Topic.query.filter_by(report=1).order_by(Topic.last_reply_date.desc()).paginate(page, per_page=config.PER_PAGE)
	page_url = lambda page: url_for("topic.trash", page=page)
	return render_template('trash.html', page_obj=page_obj, page_url=page_url)

