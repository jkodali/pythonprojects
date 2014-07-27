import urllib2
import os
import re
import xml.etree.ElementTree as ET
import mysql.connector
import string
import datetime
import ConfigParser
import sys, getopt
import time
from linkedin import linkedin

class ConfigSettings:
	config = ConfigParser.RawConfigParser()
	executing_dir = os.path.dirname(__file__)
	config_filename = os.path.join(executing_dir, './configlocal.cfg')
	config.read(config_filename)

	DB_HOST = config.get("mysqld", "DB_HOST")
	DB_DATABASE = config.get("mysqld", "DB_DATABASE")
	DB_USERNAME = config.get("mysqld", "DB_USERNAME")
	DB_PASSWORD = config.get("mysqld", "DB_PASSWORD")		

def processLinkedInData(jobsite, searchstring, citytosearch, ziptosearch, lastDownloadedTime):
	authentication = linkedin.LinkedInDeveloperAuthentication('75ph7mwmqazlp9', 'wauOWNOXgZqBKBWo', '4468dda6-1a33-4007-a175-0e03dc72282b', 'a9aee8ab-984b-4a3d-b8e9-a4e459c7d10f', 
		'http:\\jeevansgadgets.com\getjoblist', linkedin.PERMISSIONS.enums.values())
	application = linkedin.LinkedInApplication(authentication)

	loopcount = 20
	totalcount = 0

	filename = '%sjoblist.txt' % jobsite
	joblistfile = open(filename, 'w')

	while loopcount == 20:
		print 'downloading %s-%s' % (totalcount, totalcount+20)
		loopcount = 0
		data = application.search_job(selectors=[{'jobs': ['id', 'customer-job-code', 'posting-date', 'active', 'company', 'position', 'site-job-url', 'location-description']}], 
			params={'keywords': searchstring, 'count': 20, 'start': totalcount, 'postal-code': ziptosearch, 'country-code': 'US', 'distance': 50, 'sort': 'DD'})

		#print data
		for job in data["jobs"]["values"]:
			loopcount = loopcount + 1
			totalcount = totalcount + 1
			date = datetime.datetime.strptime(str(job["postingDate"]["month"]) + '-' + str(job["postingDate"]["day"]) + '-' + str(job["postingDate"]["year"]), '%m-%d-%Y')
			if date >= lastDownloadedTime:
				joblistfile.write(job["position"]["title"].encode('ascii', 'ignore').strip() + '\t' + job["siteJobUrl"].strip() + '\t' + job["company"]["name"].encode('ascii', 'ignore').strip() + '\t' + '' + '\t' + job["locationDescription"].strip() + '\t' + date.strftime('%Y-%m-%d') + '\n')


def processDiceDataFromScraping(jobsite, searchstring, citytosearch, ziptosearch, lastDownloadedTime):

	loopcount = 50
	totalcount = 0

	filename = '%sjoblist.txt' % jobsite
	joblistfile = open(filename, 'w')

	while loopcount == 50:
		loopcount = 0
		url = "http://www.dice.com/job/results/%s?b=7&o=%s&caller=searchagain&n=50&q=%s&src=19&x=all&p=z" % (ziptosearch, totalcount, searchstring)
		print url
		response = urllib2.urlopen(url)
		fullhtmlString = response.read()
		response.close()

		# assumptions:
		#1. there is only one table element with class=summary (<table class="summary")
		#2. In this, all job rows are under tbody section
		#3. Each row is information about one job and below is the example of the job row
		#4. <tr class="STDsrRes"><td><div><a href="/job/result/10106525/17297032000007842?src=19&q=technology manager">SAP Basis/Netweaver - Senior Consultant</a></div></td><td><a href="/jobsearch/company/DiceId_10106525/10106525" title="Find more jobs at Find more jobs at Deloitte">Deloitte</a></td><td>McLean, VA</td><td align="center">Jun-04-2014</td></tr>
		#5. Actual job link is part of a div node in first column
		#6. 2nd column is company
		#7. 3rd column in City
		#8. 4th column is Date

		# extract the actual table script from this html
		tablestart = re.compile('<table class="summary" cellspacing="0">')
		tablestartmatch = tablestart.search(fullhtmlString)
		fromtableString = fullhtmlString[tablestartmatch.start():]
		tableend = re.compile("</table>")
		tableendmatch = tableend.search(fromtableString)

		maintableHTML = fromtableString[:tableendmatch.end()]
		maintableHTML = string.replace(maintableHTML, '&', '&amp;')

		tableTree = ET.fromstring(maintableHTML)
		tbodyTree = tableTree.find('tbody')

		companylink = ""

		# print maintableHTML

		for trTree in tbodyTree.findall('tr'):
			if len(list(trTree)) == 4:
				loopcount = loopcount + 1
				totalcount = totalcount + 1
				jobname = trTree[0][0][0].text.strip().lower()
				joblink = trTree[0][0][0].attrib.get('href').strip()

				if len(list(trTree[1])) == 1:
					companyname = trTree[1][0].text.strip().lower()
					companylink = trTree[1][0].attrib.get('href').strip()
				else:
					companyname = trTree[1].text.strip().lower()

				if len(list(trTree[2])) == 1:
					city = trTree[2][0].text.strip().lower()
				else:
					city = trTree[2].text.strip().lower()
				date = datetime.datetime.strptime(trTree[3].text.strip(), '%b-%d-%Y')

				if date >= lastDownloadedTime:
					joblistfile.write(jobname + '\t' + joblink + '\t' + companyname + '\t' + companylink + '\t' + city + '\t' + date.strftime('%Y-%m-%d') + '\n')

def loadDataIntoDBFromFile(jobsite, searchstring, citytosearch, ziptosearch):

	queryData=[]
	filename = '%sjoblist.txt' % jobsite
	joblistfile = open(filename, 'r')
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	connection = mysql.connector.connect(user=ConfigSettings.DB_USERNAME, password=ConfigSettings.DB_PASSWORD, host=ConfigSettings.DB_HOST, database=ConfigSettings.DB_DATABASE)
	cursor = connection.cursor()

	linecount = 0;
	for line in joblistfile:
		linecount = linecount + 1
		lineparts = line.split('\t')
		postedDate = lineparts[5].strip()
		#print linecount
		#postedDate = datetime.datetime.strptime(lineparts[5].strip(), '%m-%d-%Y').strftime('%Y-%m-%d')
		#queryData.append((lineparts[0], lineparts[1], lineparts[2], lineparts[4], postedDate, postedDate, now, postedDate, now))
		query = "INSERT INTO job_list (JobSite, SearchString, CityToSearch, Title, JobLink, CompanyName, City, OriginalDatePosted, LastDatePosted, LastUpdate) values ('%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s') ON DUPLICATE KEY UPDATE LastDatePosted='%s', LastUpdate='%s'" % (jobsite, searchstring, citytosearch, lineparts[0][:128].replace("'", "\\'"), lineparts[1].replace("'", "\\'"), lineparts[2][:64].replace("'", "\\'"), lineparts[4][:128].replace("'", "\\'"), postedDate, postedDate, now, postedDate, now)
		#print query
		cursor.execute(query)

	#queryString = "INSERT INTO dice_job_list (Title, JobLink, CompanyName, City, OriginalDatePosted, LastDatePosted, LastUpdate) values (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE LastDatePosted=%s, LastUpdate=%s"

	#loadfileStr = "LOAD DATA LOCAL INFILE './dicejoblist.txt' INTO TABLE jobdata.dice_job_list FIELDS TERMINATED BY '\t' LINES TERMINATED BY '\n'"

	#while len(queryData) != 0:
	#    cursor.executemany(queryString, queryData[:999])
	#    del queryData[:999]
	
	connection.commit()
	cursor.close()
	connection.disconnect()
	connection.close()
	print 'Total Lines: %s' % linecount

def downloadJobData(jobsite, searchstring, citytosearch, ziptosearch, lastDownloadedTime):
	if (jobsite == "dice"):
		processDiceDataFromScraping(jobsite, searchstring, citytosearch, ziptosearch, lastDownloadedTime)
	elif jobsite == "linkedin":
		processLinkedInData(jobsite, searchstring, citytosearch, ziptosearch, lastDownloadedTime)

def updateLastSearchTime(jobsite, searchstring, citytosearch):
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	connection = mysql.connector.connect(user=ConfigSettings.DB_USERNAME, password=ConfigSettings.DB_PASSWORD, host=ConfigSettings.DB_HOST, database=ConfigSettings.DB_DATABASE)
	cursor = connection.cursor()
	query = "INSERT INTO last_search_time (JobSite, SearchString, City, LastUpdate) values ('%s', '%s','%s','%s') ON DUPLICATE KEY UPDATE LastUpdate='%s'" % (jobsite, searchstring, citytosearch, now, now)
	#print query
	cursor.execute(query)
	cursor.close()
	connection.disconnect()
	connection.close()

def getLastDownloadedTime(jobsite, searchstring, citytosearch):
	query = "select LastUpdate from last_search_time where JobSite = '%s' and SearchString = '%s' and City = '%s'" % (jobsite, searchstring, citytosearch)
	#print query
	connection = mysql.connector.connect(user=ConfigSettings.DB_USERNAME, password=ConfigSettings.DB_PASSWORD, host=ConfigSettings.DB_HOST, database=ConfigSettings.DB_DATABASE)
	cursor = connection.cursor()
	cursor.execute(query)

	lastUpdate = None
	for LastUpdate in cursor:
		lastUpdate = LastUpdate[0]
	cursor.close()
	connection.disconnect()
	connection.close()
	if lastUpdate is None:
		lastUpdate = datetime.datetime.strptime('1900-01-01', '%Y-%m-%d')
	return lastUpdate

def main(argv):

	jobsite = "linkedin"
	searchstring = "technology+manager"
	citytosearch = 'dc'
	ziptosearch = '20001'

	opts = None
	try:
		opts, args = getopt.getopt(argv, "j:s:c:")
	except getopt.GetoptError:
		print 'invalid arguments'
		sys.exit(1)

	for opt, arg in opts:
		if opt == '-j':
			jobsite = arg
		if opt == '-s':
			searchstring = arg
		if opt == '-c':
			citytosearch = arg
			if citytosearch == 'dc':
				ziptosearch = '20001'
			elif citytosearch == 'chicago':
				ziptosearch = '60606'
			else:
				print 'invalid city to search %s' % citytosearch
				sys.exit(1)

	print 'doing: %s %s %s' % (jobsite, searchstring, citytosearch)
	lastDownloadedTime = getLastDownloadedTime(jobsite, searchstring, citytosearch)
	print 'LastDownloaded on: %s' % lastDownloadedTime
	downloadJobData(jobsite, searchstring, citytosearch, ziptosearch, lastDownloadedTime)
	loadDataIntoDBFromFile(jobsite, searchstring, citytosearch, ziptosearch)
	updateLastSearchTime(jobsite, searchstring, citytosearch)

if __name__ == "__main__":
	main(sys.argv[1:])