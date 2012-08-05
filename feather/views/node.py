# coding: utf-8
from flask import Module, request, session, g, redirect, url_for, \
		abort, render_template, flash
from feather import config
from feather.extensions import db
from feather.databases import Nodeclass, Node, Topic

node = Module(__name__)


def get_node(nodesite):
	rv = Node.query.filter_by(site=nodesite).first()
	return rv

def get_topicscount(node):
	return node.topics.count()

@node.route('/add/node', methods=['GET', 'POST'])
def node_add():
	if session['user_id'] != 1:
		abort(401)
	if request.method == 'POST':
		if session['user_id'] != 1:
			abort(401)
		nodeclass = Nodeclass.query.filter_by(name=request.form['nodeclass']).first()
		if not nodeclass:
			nodeclass = Nodeclass(request.form['nodeclass'])
			db.session.add(nodeclass)
			db.session.commit()
		nodeclass = Nodeclass.query.filter_by(name=request.form['nodeclass']).first()
		if request.form['nodename'] == '' or request.form['nodesite'] == '' or request.form['nodeclass'] == '':
			error = u'请填写完整信息！'
			return render_template('node_add.html', error=error)
		elif Node.query.filter_by(name=request.form['nodename']).first() is not None:
			error = u'节点名称已存在！'
			return render_template('node_add.html', error=error)
		elif Node.query.filter_by(site=request.form['nodesite']).first() is not None:
			error = u'节点地址已存在！'
			return render_template('node_add.html', error=error)
		else:
			node = Node(request.form['nodename'], request.form['nodesite'], request.form['description'], nodeclass)
			db.session.add(node)
			db.session.commit()
			flash(u'添加成功！')
			return redirect(url_for('topic.tab_view'))
	return render_template('node_add.html')

@node.route('/node/<nodesite>/edit', methods=['GET', 'POST'])
def node_edit(nodesite):
	if session['user_id'] != 1:
		abort(401)
	node = Node.query.filter_by(site=nodesite).first()
	if request.method == 'POST':
		if request.form['nodename'] == '' or request.form['nodesite'] == '' or request.form['nodeclass'] == '':
			error = u'请填写完整信息！'
			return render_template('node_edit.html', node=node, error=error)
		elif request.form['nodename'] != node.name and Node.query.filter_by(name=request.form['nodename']).first() is not None:
			error = u'节点名称已存在！'
			return render_template('node_edit.html', node=node, error=error)
		elif request.form['nodesite'] != node.site and Node.query.filter_by(site=request.form['nodesite']).first() is not None:
			error = u'节点地址已存在！'
			return render_template('node_edit.html', node=node, error=error)
		else:
			nodeclass = Nodeclass.query.filter_by(name=request.form['nodeclass']).first()
			if not nodeclass:
				nodeclass = Nodeclass(request.form['nodeclass'])
				db.session.add(nodeclass)
				db.session.commit()
			nodeclass = Nodeclass.query.filter_by(name=request.form['nodeclass']).first()
			node.name = request.form['nodename']
			node.site = request.form['nodesite']
			node.description = request.form['description']
			node.header = request.form['header']
			node.style = request.form['style']
			node.nodeclass = nodeclass
			db.session.commit()
			flash(u'节点修改成功！')
			return redirect(url_for('node.index', nodesite=nodesite))
	return render_template('node_edit.html',node=node)

@node.route('/node/<nodesite>', defaults={'page': 1})
@node.route('/node/<nodesite>/page/<int:page>')
def index(nodesite,page):
	node = get_node(nodesite)
	topicscount = get_topicscount(node)
	page_obj = Topic.query.filter_by(node=node).filter_by(report=0).order_by(Topic.last_reply_date.desc()).paginate(page, per_page=config.PER_PAGE)
	page_url = lambda page: url_for("node.index", nodesite=nodesite, page=page)
	return render_template('node_index.html', page_obj=page_obj, page_url=page_url, node=node, topicscount=topicscount)


