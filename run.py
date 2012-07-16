# coding: utf-8
from flaskext.script import Manager, Server, prompt_bool
from feather import app, db

manager = Manager(app)
server = Server(host='0.0.0.0', port=8888)
manager.add_command("runserver", server)

@manager.command
def createall():
	db.create_all()

@manager.command
def dropall():
	if prompt_bool(u"警告：你将要删除全部的数据！你确定否？"):
		db.drop_all()

if __name__ == "__main__":
	manager.run()
