# coding: utf-8
import re
from feather.databases import User, Topic, Reply
import markdown
import functools

markdown = functools.partial(markdown.markdown,
                             safe_mode=False,
                             output_format="html")


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

def textformat(text):
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

def mention(text):
	usernames = []
	if text.find('@') == -1:
		begin = -1
		usernames = usernames
	elif text.find(' ') != -1:
		begin = text.find('@') + 1
		if text.find('\n') != -1:
			end = text.find(' ') < text.find('\n') and text.find(' ') or text.find('\n')
		else:
			end = len(text)
	elif text.find('\n') != -1:
		begin = text.find('@') + 1
		end = text.find('\n')
	else:
		begin = text.find('@') +1
		end = len(text)
	if begin != -1:
		value = text[begin:end]
		n = len(value)
		for i in range(0,n):
			rv = User.query.filter_by(name=value).first()
			if not rv:
				value = list(value)
				value.pop()
				value = ''.join(value)
				if value == '' and '@' in text[text.find('@') + 1:]:
					usernames = 'error'
			else:
				text = text[text.find('@') + len(value):]
				usernames = usernames + [value]
				break
	return usernames

def mentions(text):
	usernames = []
	if text.find('@') == -1:
		begin = -1
		usernames = usernames
	elif text.find(' ') != -1:
		begin = text.find('@') + 1
		if text.find('\n') != -1:
			end = text.find(' ') < text.find('\n') and text.find(' ') or text.find('\n')
		else:
			end = len(text)
	elif text.find('\n') != -1:
		begin = text.find('@') + 1
		end = text.find('\n')
	else:
		begin = text.find('@') +1
		end = len(text)
	if begin != -1:
		value = text[begin:end]
		n = len(value)
		for i in range(0,n):
			rv = User.query.filter_by(name=value).first()
			if not rv:
				value = list(value)
				value.pop()
				value = ''.join(value)
				if value == '' and '@' in text[text.find('@') + 1:]:
					text = text[text.find('@') + 1:]
					while True:
						a = mention(text)
						if a == []:
							break
						i = 0
						while a == 'error':
							text = text[text.find('@') + 1:]
							a = mention(text)
							i += 1
							if i == 6:
								break
						if a == 'error':
							a = []
						usernames = usernames + a
						text = text[text.find('@') + 1:]
			else:
				text = text[text.find('@') + len(value):]
				usernames = usernames + [value]
				while True:
					a = mention(text)
					if a == []:
						break
					i = 0
					while a == 'error':
						text = text[text.find('@') + 1:]
						a = mention(text)
						i += 1
						if i == 6:
							break
					if a == 'error':
						a = []
					usernames = usernames + a
					text = text[text.find('@') + 1:]
				break
	return usernames



def mentionfilter(text):
	content = text.replace('\n','')
	usernames = list(set(mentions(content)))
	for username in usernames:
		url = '<a class=at_user href="/member/%s" target="_blank">%s</a>' % (username, username)
		text = text.replace(username, url)
	return text
