from bs4 import BeautifulSoup
import requests
from random import choice
import os

# Libraries required to limit the time taken by a request
import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
	def signal_handler(signum, frame):
		raise TimeoutException
	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(seconds)
	try:
		yield
	finally:
		signal.alarm(0)

BaseURL	= "https://en.wikipedia.org"
startURL= "https://en.wikipedia.org/wiki/Category:Lists_of_hospitals_in_the_United_States"
outDir	= "../output/"
outFile	= "ListOfHospitals.txt"

def ckdir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)
	return

def getRequest(aurl):

	# user_agents 							= ['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36','Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11','Opera/9.25 (Windows NT 5.1; U; en)','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)','Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)','Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19','Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0','Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:8.0.1) Gecko/20100101 Firefox/8.0.1']
	# user_agent 							= choice(user_agents)
	user_agent 								= 'Mozzila/5.0'
	hdr 									= {'User-Agent':user_agent}

	print("Requesting website : "+aurl)
	while  True:
		try:
			try:
				with time_limit(20):
					req 	= requests.get(aurl,headers=hdr)
				break
			except TimeoutException:
				print('Request times out. Trying again...')
				continue
		except Exception:
			print('Error in request.')
			continue
	
	return req

def getSoup(aurl):
	req 		= getRequest(aurl)
	content 	= req.content

	soup 		= BeautifulSoup(content,'html.parser')
	return soup


def processResultTable(table,state,outfile):
	headers			= table.find_all('th')

	cityIndex		= None
	hospitalIndex	=	None

	for i in range(0,len(headers)):
		if "Name" in headers[i].get_text() or "Hospital" in headers[i].get_text():
			hospitalIndex	= i
			break
	else:
		print("No name found : "+state)
	
	for i in range(0,len(headers)):
		if "city" in headers[i].get_text() or "City" in headers[i].get_text() or "Location" in headers[i].get_text():
			cityIndex	= i
			break
	else:
		print("No city found : "+state)


	records		= table.find_all('tr')

	for record in records[1:]:
		fields	= record.find_all('td')

		Name	= fields[hospitalIndex].get_text()
		if cityIndex:	City	= fields[cityIndex].get_text()
		else:	City	= ''

		outfile.write(Name+"|"+City+"|"+state+"|USA\n")
	return


def processComplicatedWithArea(soup,state,outfile):
	for child in soup.children:
		if child.name == None:
			continue
		if child.name.startswith('h'):
			nextHeader	= child.find('span',{'class':'mw-headline'})['id']
			if nextHeader in ["External_links","See_also","References","Notes"]:
				return
			else:
				continue
		if child.name == "ul":
			for record in child.children:
				if record.name == "li":
					City	= ''
					City	= record.contents[0].string.strip()
					for content in record.contents[1:]:
						if content.name == "ul":
							for hospital in content.find_all('li'):
								Name	= hospital.get_text().strip()
								outfile.write(Name+"|"+City+"|"+state+"|USA\n")

	return


def processDelaware(soup,state,outfile):
	City = ''
	for child in soup.children:
		if child.name == None:
			continue
		if child.name == "h2":
			nextHeader	= child.find('span',{'class':'mw-headline'})['id']
			if nextHeader in ["External_links","See_also","References","Notes","Historic_hospitals"]:
				return
			else:
				continue

		if child.name == "h3":
			City	= child.find('span',{'class':'mw-headline'})['id']
		if child.name == "ul":
			for record in child.children:
				if record.name == "li":
					for content in record.contents[1:]:
						if content.name == "ul":
							for hospital in content.find_all('li'):
								Name	= hospital.get_text().strip()
								outfile.write(Name+"|"+City+"|"+state+"|USA\n")
	return


def processNYC(soup,state,outfile):
	City = ''
	for child in soup.children:
		if child.name == None:
			continue
		if child.name == "h2":
			nextHeader	= child.find('span',{'class':'mw-headline'})['id']
			if nextHeader in ["External_links","See_also","References","Notes"]:
				return
			else:
				continue

		if child.name == "h3":
			City	= child.find('span',{'class':'mw-headline'})['id']
		if child.name == "ul":
			for record in child.children:
				if record.name == "li":
					if record.contents[0].name == 'a':
						Name	= record.find('a').get_text()
						outfile.write(Name+"|"+City+"|"+state+"|USA\n")
	return


def processNebraska(soup,state,outfile):
	City = ''
	for child in soup.children:
		if child.name == None:
			continue
		if child.name == "h2":
			nextHeader	= child.find('span',{'class':'mw-headline'})['id']
			if nextHeader in ["External_links","See_also","References","Notes"]:
				return
			else:
				continue

		if child.name == "h3":
			City	= child.find('span',{'class':'mw-headline'})['id']
		if child.name == "ul":
			for record in child.children:
				if record.name == "li":
					Name	= record.string
					outfile.write(Name+"|"+City+"|"+state+"|USA\n")
	return

def processComplicatedList(soup,state,outfile):
	if state in ["Maine","Minnesota","Wisconsin"]:
		processComplicatedWithArea(soup,state,outfile)
	elif state == "Delaware":	
		processDelaware(soup,state,outfile)
	elif state == "New York City":
		processNYC(soup,state,outfile)
	elif state == "Nebraska":
		processNebraska(soup,state,outfile)
	else:
		print("Unkown :"+state)

	return

def processResultList(soup,state,outfile):
	headers		= soup.find_all('h2')
	lists		= soup.find_all('ul')

	for i in range(0,len(lists)):
		records	= lists[i].find_all('li')

		if records[0].find('li'):
			# print("Complicated : "+state)
			return processComplicatedList(soup,state,outfile)

		link	= records[0].find('a')
		if link:
			if not link['href'].startswith('#'):
				for record in records:
					text	= record.get_text().strip()
					parts 	= text.split('–',1)
					Name 	= parts[0].strip()
					if len(parts)>1:
						City= parts[1]
					else:
						City= ''

					outfile.write(Name+"|"+City+"|"+state+"|USA\n")
		else:	
			for record in records:
				text	= record.get_text()
				parts 	= text.split('–',1)
				Name 	= parts[0].strip()
				if len(parts)>1:
					City= parts[1]
				else:
					City= ''

				outfile.write(Name+"|"+City+"|"+state+"|USA\n")


		try:
			nextHeader	= headers[i].find('span',{'class':'mw-headline'})['id']
		except IndexError:
			return
		except TypeError:
			return
		if nextHeader == "External_links" or nextHeader == "See_also" or nextHeader == "References":
			return
	return


def processStatePage(url,state,outfile):
	soup		= getSoup(url)
	results		= soup.find('div',{'class':'mw-parser-output'})

	table		= results.find('table',{'class':'wikitable sortable'})

	if table:	processResultTable(table,state,outfile)
	else:	processResultList(results,state,outfile)

	return

def begin():
	ckdir(outDir)

	outfile		= open(outDir+outFile,'w')
	outfile.write("Hospital Name|CITY|State|Country\n")

	soup		= getSoup(startURL)
	Categories	= soup.find_all('div',{'class':'mw-category-group'})

	for category in Categories[1:]:
		states	= category.find_all('a')

		for state in states:
			text	= state.get_text()
			link	= BaseURL + state['href']
			state	= text.split('in ')[1]
			processStatePage(link,state,outfile)
	# processStatePage("https://en.wikipedia.org/wiki/List_of_hospitals_in_New_York_City","New York City",outfile)
	return

if __name__ == "__main__":
	begin()
	print("done")