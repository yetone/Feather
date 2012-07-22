# coding: utf-8
import re
from feather.databases import User, Topic, Reply

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
		if tonumber != 0:
			nurl = '<a id=lou onclick="toReply(%s);" href="#%d" style="color: #376B43;">#<span id=nu>%s</span>楼 </a>' % (url, tonumber, url)
		else:
			nurl = '<a id=lou onclick="toReply(1);" href="#topicend" style="color: #376B43;">#<span id=nu>1</span>楼 </a>'
		text = text.replace(number, nurl)
	content = text.replace('\n','')
	usernames = list(set(mentions(content)))
	for username in usernames:
		url = '<a class=at_user href="/member/%s" target="_blank">%s</a>' % (username, username)
		text = text.replace(username, url)
	return text
