import requests
import argparse
import difflib
import operator
from colored import fg, bg, attr

ap = argparse.ArgumentParser()
ap.add_argument('-u', '--user', required = True, help = 'username or Email')
ap.add_argument('-w', '--warning', default = 0.7, required = False, help = 'level of warning, between 0 and 1')
ap.add_argument('-e', '--exactly', default = False, action = 'store_true', help = 'show only data for exactly user')
ap.add_argument('-nc', '--no-color', default = False, action = 'store_true', help = 'don\'t show color')
ap.add_argument('-s', '--services', default = False, action = 'store_true', help = 'show service hacked')
args = vars(ap.parse_args())

payload = {
	'param':args['user']
	}

url = 'https://ghostproject.fr/search.php'

data = []

def search(user):
	for i in data:
		if user == i['usr']:
			return True
	return False


def enumerate(user):
	cont = 0
	for i in data:
		if user == i['usr']:
			return cont
		cont += 1
	return 0


def ratio(user, comp):
	if not '@' in user:
		comp = comp.split('@')[0]
	return difflib.SequenceMatcher(lambda x: x == ' \t', user, comp).ratio()


def show_color(usr, pw, level):
	if not args['no_color']:
		print ('%s%s%s' % (fg(level), usr, attr(0)))
		for i in pw:
			print ('\t\t%s%s%s' % (fg(level), i, attr(0)))
	else:
		print ('%s' % (usr))
		for i in pw:
			print ('\t\t%s' % (i))

def show(d):
	d.reverse()
	for i in d:
		if i['rt'] == 1:
			show_color(i['usr'], i['pw'], 'green')
		elif i['rt'] > args['warning']:
			if not args['exactly']:
				show_color(i['usr'], i['pw'], 'yellow')
		else:
			if not args['exactly']:
				show_color(i['usr'], i['pw'], 'red')

def get_serv_hacked(user):
	url = "https://haveibeenpwned.com/api/v2/breachedaccount/"+user
	useragent = {'User-Agent':'PwnedMee'}
	r = requests.get(url, headers=useragent)
	print r.text
	if r.status_code == 200:
		return r.json()
	else:
		return False

def main():
	r = requests.post(url, data=payload)
	for text in r.text.split("\\n"):
		if not 'Search'  in text and ':' in text:
			rsp = text.split(':')
			src_usr = args['user'].lower()
			rsp_usr = rsp[0].lower()
			rsp_pw = rsp[1]
			srvs = []
			if not search(rsp_usr):
				rt = ratio(src_usr, rsp_usr)
				if args['services'] and rt == 1:
					srvs = get_serv_hacked(rsp_usr)
					print srvs
				data.append({'usr':rsp_usr, 'pw':[rsp_pw], 'rt': rt, 'srvs': srvs})
			else:
				pos = enumerate(rsp_usr)
				data[pos]['pw'].append(rsp_pw)
	ord_data = sorted(data, key=lambda x: x['rt'])
	show(ord_data)	

main()
