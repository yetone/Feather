# coding: utf-8
# all the imports
import os
import time
import re
from hashlib import md5
from flask import Flask, request, session, g, redirect, url_for, \
		abort, render_template, flash
from flaskext.markdown import Markdown
from feather.views import account, node, topic, reply, timesystem, city
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
_emoji_list = [
    "-1", "0", "1", "109", "2", "3", "4", "5", "6", "7", "8", "8ball", "9",
    "a", "ab", "airplane", "alien", "ambulance", "angel", "anger", "angry",
    "apple", "aquarius", "aries", "arrow_backward", "arrow_down",
    "arrow_forward", "arrow_left", "arrow_lower_left", "arrow_lower_right",
    "arrow_right", "arrow_up", "arrow_upper_left", "arrow_upper_right",
    "art", "astonished", "atm", "b", "baby", "baby_chick", "baby_symbol",
    "balloon", "bamboo", "bank", "barber", "baseball", "basketball", "bath",
    "bear", "beer", "beers", "beginner", "bell", "bento", "bike", "bikini",
    "bird", "birthday", "black_square", "blue_car", "blue_heart", "blush",
    "boar", "boat", "bomb", "book", "boot", "bouquet", "bow", "bowtie",
    "boy", "bread", "briefcase", "broken_heart", "bug", "bulb",
    "bullettrain_front", "bullettrain_side", "bus", "busstop", "cactus",
    "cake", "calling", "camel", "camera", "cancer", "capricorn", "car",
    "cat", "cd", "chart", "checkered_flag", "cherry_blossom", "chicken",
    "christmas_tree", "church", "cinema", "city_sunrise", "city_sunset",
    "clap", "clapper", "clock1", "clock10", "clock11", "clock12", "clock2",
    "clock3", "clock4", "clock5", "clock6", "clock7", "clock8", "clock9",
    "closed_umbrella", "cloud", "clubs", "cn", "cocktail", "coffee",
    "cold_sweat", "computer", "confounded", "congratulations",
    "construction", "construction_worker", "convenience_store", "cool",
    "cop", "copyright", "couple", "couple_with_heart", "couplekiss", "cow",
    "crossed_flags", "crown", "cry", "cupid", "currency_exchange", "curry",
    "cyclone", "dancer", "dancers", "dango", "dart", "dash", "de",
    "department_store", "diamonds", "disappointed", "dog", "dolls",
    "dolphin", "dress", "dvd", "ear", "ear_of_rice", "egg", "eggplant",
    "egplant", "eight_pointed_black_star", "eight_spoked_asterisk",
    "elephant", "email", "es", "european_castle", "exclamation", "eyes",
    "factory", "fallen_leaf", "fast_forward", "fax", "fearful", "feelsgood",
    "feet", "ferris_wheel", "finnadie", "fire", "fire_engine", "fireworks",
    "fish", "fist", "flags", "flushed", "football", "fork_and_knife",
    "fountain", "four_leaf_clover", "fr", "fries", "frog", "fuelpump", "gb",
    "gem", "gemini", "ghost", "gift", "gift_heart", "girl", "goberserk",
    "godmode", "golf", "green_heart", "grey_exclamation", "grey_question",
    "grin", "guardsman", "guitar", "gun", "haircut", "hamburger", "hammer",
    "hamster", "hand", "handbag", "hankey", "hash", "headphones", "heart",
    "heart_decoration", "heart_eyes", "heartbeat", "heartpulse", "hearts",
    "hibiscus", "high_heel", "horse", "hospital", "hotel", "hotsprings",
    "house", "hurtrealbad", "icecream", "id", "ideograph_advantage", "imp",
    "information_desk_person", "iphone", "it", "jack_o_lantern",
    "japanese_castle", "joy", "jp", "key", "kimono", "kiss", "kissing_face",
    "kissing_heart", "koala", "koko", "kr", "leaves", "leo", "libra", "lips",
    "lipstick", "lock", "loop", "loudspeaker", "love_hotel", "mag",
    "mahjong", "mailbox", "man", "man_with_gua_pi_mao", "man_with_turban",
    "maple_leaf", "mask", "massage", "mega", "memo", "mens", "metal",
    "metro", "microphone", "minidisc", "mobile_phone_off", "moneybag",
    "monkey", "monkey_face", "moon", "mortar_board", "mount_fuji", "mouse",
    "movie_camera", "muscle", "musical_note", "nail_care", "necktie", "new",
    "no_good", "no_smoking", "nose", "notes", "o", "o2", "ocean", "octocat",
    "octopus", "oden", "office", "ok", "ok_hand", "ok_woman", "older_man",
    "older_woman", "open_hands", "ophiuchus", "palm_tree", "parking",
    "part_alternation_mark", "pencil", "penguin", "pensive", "persevere",
    "person_with_blond_hair", "phone", "pig", "pill", "pisces", "plus1",
    "point_down", "point_left", "point_right", "point_up", "point_up_2",
    "police_car", "poop", "post_office", "postbox", "pray", "princess",
    "punch", "purple_heart", "question", "rabbit", "racehorse", "radio",
    "rage", "rage1", "rage2", "rage3", "rage4", "rainbow", "raised_hands",
    "ramen", "red_car", "red_circle", "registered", "relaxed", "relieved",
    "restroom", "rewind", "ribbon", "rice", "rice_ball", "rice_cracker",
    "rice_scene", "ring", "rocket", "roller_coaster", "rose", "ru", "runner",
    "sa", "sagittarius", "sailboat", "sake", "sandal", "santa", "satellite",
    "satisfied", "saxophone", "school", "school_satchel", "scissors",
    "scorpius", "scream", "seat", "secret", "shaved_ice", "sheep", "shell",
    "ship", "shipit", "shirt", "shit", "shoe", "signal_strength",
    "six_pointed_star", "ski", "skull", "sleepy", "slot_machine", "smile",
    "smiley", "smirk", "smoking", "snake", "snowman", "sob", "soccer",
    "space_invader", "spades", "spaghetti", "sparkler", "sparkles",
    "speaker", "speedboat", "squirrel", "star", "star2", "stars", "station",
    "statue_of_liberty", "stew", "strawberry", "sunflower", "sunny",
    "sunrise", "sunrise_over_mountains", "surfer", "sushi", "suspect",
    "sweat", "sweat_drops", "swimmer", "syringe", "tada", "tangerine",
    "taurus", "taxi", "tea", "telephone", "tennis", "tent", "thumbsdown",
    "thumbsup", "ticket", "tiger", "tm", "toilet", "tokyo_tower", "tomato",
    "tongue", "top", "tophat", "traffic_light", "train", "trident",
    "trollface", "trophy", "tropical_fish", "truck", "trumpet", "tshirt",
    "tulip", "tv", "u5272", "u55b6", "u6307", "u6708", "u6709", "u6e80",
    "u7121", "u7533", "u7a7a", "umbrella", "unamused", "underage", "unlock",
    "up", "us", "v", "vhs", "vibration_mode", "virgo", "vs", "walking",
    "warning", "watermelon", "wave", "wc", "wedding", "whale", "wheelchair",
    "white_square", "wind_chime", "wink", "wink2", "wolf", "woman",
    "womans_hat", "womens", "x", "yellow_heart", "zap", "zzz", "+1"
]


def _emoji(text):
    pattern = re.compile(':([a-z0-9\+\-_]+):')

    def make_emoji(m):
        name = m.group(1)
        if name not in _emoji_list:
            return ':%s:' % name
        tpl = ('<img class="emoji" title="%(name)s" alt="%(name)s" height="20"'
				' width="20" src="http://l.ruby-china.org/assets/emojis/%(name)s.png" align="top">')
        return tpl % {'name': name}

    text = pattern.sub(make_emoji, text)
    return text

@app.template_filter('formattext')
def format_text(text):
	text = re.sub(ur'<a.+?href="(.+?)".*?>(.+?)<\/a>',ur'<a href="\1" target="_blank">\2</a>',text)
	text = re.sub(ur'<(http(s|):\/\/[\w.]+\/?\S*)>',ur'<a href="\1" target="_blank">\1</a>',text)
	topic_url = ur'http:\/\/(www\.|)feather\.im\/topic\/?(\S*)'
	for match in re.finditer(topic_url, text):
		url = match.group(0)
		topic_id = match.group(2)
		topic = Topic.query.get(topic_id)
		if topic is None:
			continue
		else:
			topic_title = topic.title
		aurl = '<a href="%s" target="_blank">/%s</a>' % (url, topic_title)
		text = text.replace(url, aurl)
	text = re.sub(ur'http:\/\/(www\.|)feather\.im\/(node\/?\S*)',ur'<a href="\2" target="_blank">\2</a>',text)
	regex_url = r'(^|\s)http(s|):\/\/([\w.]+\/?)\S*'
	for match in re.finditer(regex_url, text):
		url = match.group(0)
		aurl = '<a href="%s" target="_blank">%s</a>' % (url, url)
		text = text.replace(url, aurl)
	number = ur'#(\d+)楼\s'
	for match in re.finditer(number, text):
		url = match.group(1)
		number = match.group(0)
		tonumber = int(url) - 1
		nurl = '<a id=lou onclick="toReply(%s);" href="#;" style="color: #376B43;">#<span id=nu>%s</span>楼 </a>' % (url, url)
		text = text.replace(number, nurl)
	text = _emoji(text)
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
			str = '昨天' + rtime
		else:
			str = '前天' + rtime
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
	return 'http://ruby-china.org/avatar/%s?d=identicon&s=%d' % \
			(md5(email.strip().lower().encode('utf-8')).hexdigest(), 128)

@app.template_filter('gravatar')
def gravatar_url(email, size=48):
	return 'http://ruby-china.org/avatar/%s?d=identicon&s=%d' % \
			(md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

@app.template_filter('gravatarmini')
def gravatarmini_url(email):
	return 'http://ruby-china.org/avatar/%s?d=identicon&s=%d' % \
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

