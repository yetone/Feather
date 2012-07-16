# coding: utf-8
from flask import Module, abort, render_template, url_for
from feather import config
from feather.extensions import db
from feather.databases import Bill, Bank
from sqlalchemy import or_

timesystem = Module(__name__)

@timesystem.route('/bank', defaults={'page': 1})
@timesystem.route('/bank/page/<int:page>')
def bank(page):
	bank = Bank.query.get(1)
	if not bank:
		abort(401)
	page_obj = Bill.query.filter(or_(Bill.type == 1, Bill.type == 2, Bill.type == 7, Bill.type == 8)).order_by(Bill.date.desc()).paginate(page, per_page=config.RE_PER_PAGE)
	page_url = lambda page: url_for("timesystem.bank", page=page)
	return render_template('bank.html', bank=bank, page_obj=page_obj, page_url=page_url)

