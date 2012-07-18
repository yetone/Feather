# coding: utf-8
import time
from flask import Module, request, session, g, redirect, url_for, \
		abort, render_template, flash
from werkzeug import check_password_hash, generate_password_hash
from feather.extensions import db, cache
from feather import config
from feather.databases import Bill, Bank, City, User, Topic, Notify

account = Module(__name__)

def get_user_id(username):
	rv = User.query.filter_by(name=username).first()
	return rv.id if rv else None

def get_user_id_from_email(email):
	rv = User.query.filter_by(email=email).first()
	return rv.id if rv else None

@account.route('/users')
@cache.cached(60 * 5)
def users():
	users = User.query.order_by(User.id.asc()).all()
	return render_template('users.html',users=users)


@account.route('/member/<username>', defaults={'page': 1})
@account.route('/member/<username>/page/<int:page>')
def usercenter(username,page):
	user = User.query.filter_by(name=username).first()
	page_obj = user.topics.order_by(Topic.last_reply_date.desc()).paginate(page, per_page=config.PER_PAGE)
	page_url = lambda page: url_for("account.usercenter", username=username, page=page)
	return render_template('usercenter.html', user=user, page_obj=page_obj, page_url=page_url)


@account.route('/setting/account', methods=['GET', 'POST'])
def setting():
	if not g.user:
		return redirect(url_for('topic.tab_view'))
	user = g.user
	if request.method == 'POST':
		if check_password_hash(g.user.password,request.form['user[current_password]']):
			user.name = request.form['user[name]']
			user.email = request.form['user[email]']
			user.website = request.form['user[website]']
			user.description = request.form['user[description]']
			user.timeswitch = request.form['user[timeswitch]']
			user.topswitch = request.form['user[topswitch]']
			user.emailswitch = request.form['user[emailswitch]']
			city = City.query.filter_by(name=request.form['user[city]']).first()
			if not city:
				city = City(name=request.form['user[city]'])
				db.session.add(city)
				db.session.commit()
			city = City.query.filter_by(name=request.form['user[city]']).first()
			user.city = city
			db.session.commit()
			flash(u'修改成功！')
			return redirect(url_for('account.setting'))
		else:
			flash(u'密码错误！')
			return redirect(url_for('account.setting'))
	return render_template('setting.html',user=g.user)


@account.route('/notification', defaults={'page': 1})
@account.route('/notification/page/<int:page>')
def notify(page):
	g.notify = 0
	if g.notify_read:
		page_obj = g.notify_read.paginate(page, per_page=config.RE_PER_PAGE)
	else:
		page_obj = []
	page_url = lambda page: url_for("account.notify", page=page)
	notifications = Notify.query.filter_by(author=g.user).all()
	for notification in notifications:
		notification.status = 0
		db.session.commit()
	return render_template('notifications.html', page_obj=page_obj, page_url=page_url, unreads=g.notify_unread, un=g.un)



@account.route('/top')
@cache.cached(60 * 60)
def top():
	users = User.query.filter_by(topswitch=1).order_by(User.time.desc()).limit(26)
	return render_template('top.html',users=users.all())



@account.route('/favorites', defaults={'page': 1})
@account.route('/favorites/page/<int:page>')
def favorites(page):
	if not session.get('user_id'):
		abort(401)
	topics = User.query.get(session['user_id']).favorites[::-1]
	n = len(topics)
	PER_PAGE = config.PER_PAGE
	if n < PER_PAGE:
		pages = 1
	else:
		pages = n / PER_PAGE
		if n % PER_PAGE != 0:
			pages += 1
	return render_template('favorites.html',topics=topics[(page-1)*PER_PAGE:(page-1)*PER_PAGE+PER_PAGE],pages=pages,page=page)

@account.route('/times', defaults={'page': 1})
@account.route('/times/page/<int:page>')
def times(page):
	if not session.get('user_id'):
		abort(401)
	page_obj = Bill.query.filter_by(author=g.user).order_by(Bill.date.desc()).paginate(page, per_page=config.RE_PER_PAGE)
	page_url = lambda page: url_for("account.times", page=page)
	return render_template('times.html', page_obj=page_obj, page_url=page_url)



@account.route('/login', methods=['GET', 'POST'])
def login():
	if session.get('user_id'):
		return redirect(url_for('topic.tab_view'))
	error = None
	if request.method == 'POST':
		if '@' in request.form['username']:
			user = User.query.filter_by(email=request.form['username']).first()
			if user is None:
				error = u'用户名错误！'
			elif not check_password_hash(user.password,request.form['password']):
				error = u'密码错误！'
			else:
				flash(u'登录成功！')
				session['user_id'] = user.id
				return redirect(url_for('topic.tab_view'))
		else:
			user = User.query.filter_by(name=request.form['username']).first()
			if user is None:
				error = u'用户名错误！'
			elif not check_password_hash(user.password,request.form['password']):
				error = u'密码错误！'
			else:
				flash(u'登录成功！')
				session['user_id'] = user.id
				session.permanent = True
				return redirect(url_for('topic.tab_view'))
	return render_template('login.html', error=error)


@account.route('/register', defaults={'invitername': u''}, methods=['GET', 'POST'])
@account.route('/register/~<invitername>', methods=['GET', 'POST'])
def register(invitername):
	if g.user:
		return redirect(url_for('topic.tab_view'))
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = u'你需要输入一个用户名哦！'
		elif not request.form['email'] or \
				'@' not in request.form['email']:
			error = u'你需要输入一个有效的邮箱地址！'
		elif not request.form['password']:
			error = u'你需要输入一个密码哦！'
		elif request.form['password'] != request.form['password2']:
			error = u'你输入的两次密码不一样哦！'
		elif get_user_id(request.form['username']) is not None:
			error = u'此用户名已存在哦！'
		elif get_user_id_from_email(request.form['email']) is not None:
			error = u'此邮箱已存在哦！'
		else:
			if invitername:
				user = User(name=request.form['username'], email=request.form['email'], password=generate_password_hash(request.form['password']), time=2160)
			else:
				user = User(name=request.form['username'], email=request.form['email'], password=generate_password_hash(request.form['password']), time=2100, date=int(time.time()))
			db.session.add(user)
			db.session.commit()
			if Bank.query.all() == []:
				b = Bank(time=2100000)
				db.session.add(b)
				db.session.commit()
			bank = Bank.query.get(1)
			user = User.query.filter_by(name=request.form['username']).first()
			if invitername:
				giver = User.query.filter_by(name=invitername).first()
				bank.time -= 2220
				giver.time += 60
				bill = Bill(author=user,time=2160,type=7,balance=user.time,date=int(time.time()),user_id=giver.id)
				bill2 = Bill(author=giver,time=60,type=8,balance=giver.time,date=int(time.time()),user_id=user.id)
				db.session.add(bill2)
			else:
				bank.time -= 2100
				bill = Bill(author=user,time=2100,type=1,balance=user.time,date=int(time.time()))
			db.session.add(bill)
			db.session.commit()
			flash(u'你已经成功注册！现在马上登录吧！')
			return redirect(url_for('account.login'))
	return render_template('register.html', error=error, invitername=invitername)




@account.route('/logout', methods=['GET', 'POST'])
def logout():
	if g.user is not None:
		session.pop('user_id', None)
		session.permanent = False
		flash(u'你已经成功登出！')
	return redirect(url_for('topic.tab_view'))



