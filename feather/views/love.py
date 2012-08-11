# coding: utf-8
import time
from flask import Module, request, session, g, redirect, url_for, \
		abort, render_template, flash, jsonify
from flask_sqlalchemy import Pagination
from feather import config
from feather.extensions import db, cache
from feather.helpers import mentions, mentionfilter
from feather.databases import Bill, Bank, User, Nodeclass, Node, \
		Topic, Reply, Notify


love = Module(__name__)

@love.route('/love', defaults={'page': 1})
@love.route('/love/page/<int:page>')
def index(page):
	if not session.get('user_id'):
		return redirect(url_for('account.login'))
	if session.get('user_id') != 1 and session.get('user_id') != 2:
		return redirect(url_for('topic.index'))
	page_obj = Topic.query.filter_by(report=2).order_by(Topic.date.desc()).paginate(page, per_page=config.PER_PAGE)
	page_url = lambda page: url_for("love.index", page=page)
	return render_template('love.html', page_obj=page_obj, page_url=page_url)

@love.route('/love/add', methods=['GET', 'POST'])
def love_add():
	node = Node.query.filter_by(name=u'爱情').first()
	if not session.get('user_id'):
		return redirect(url_for('account.login'))
	if session.get('user_id') != 1 and session.get('user_id') != 2:
		return redirect(url_for('topic.index'))
	if request.method == 'POST':
		topic = Topic(author=g.user, title=request.form['title'], text=request.form['text'], reply_count=0, node=node, report=2)
		db.session.add(topic)
		db.session.commit()
		return redirect(url_for('love.love_view', topic_id=topic.id))
	return render_template('love_add.html', node=node)

@love.route('/love/<int:topic_id>')
def love_view(topic_id):
	topic = Topic.query.get(topic_id)
	return render_template('love_view.html', topic=topic)

@love.route('/love/<int:topic_id>/reply', methods=['POST'])
def love_reply(topic_id):
	topic = Topic.query.get(topic_id)
	reply = Reply(topic=topic, author=g.user, text=request.form['reply[content]'], type=1)
	db.session.add(reply)
	db.session.commit()
	return redirect(url_for('love.love_view', topic_id=topic_id))
