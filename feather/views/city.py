# coding: utf-8
from flask import Module, render_template
from feather.extensions import db
from feather.databases import City, User

city = Module(__name__)

@city.route('/city/<citysite>')
def city_view(citysite):
	city = City.query.filter_by(site=citysite).first()
	users = city.users.order_by(User.id.asc()).all()
	return render_template('city_view.html',city=city,users=users)

