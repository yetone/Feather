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
	content = text.replace('\n','')
	usernames = list(set(mentions(content)))
	for username in usernames:
		url = '<a class=at_user href="/member/%s" target="_blank">%s</a>' % (username, username)
		text = text.replace(username, url)
	return text
