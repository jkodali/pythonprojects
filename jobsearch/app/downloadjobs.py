import urllib2
import os
import re
import xml.etree.ElementTree as ET
import mysql.connector
import string
import datetime
import ConfigParser
import sys, getopt

class ConfigSettings:
	config = ConfigParser.RawConfigParser()
	executing_dir = os.path.dirname(__file__)
	config_filename = os.path.join(executing_dir, './configlocal.cfg')
	config.read(config_filename)

	DB_HOST = config.get("mysqld", "DB_HOST")
	DB_DATABASE = config.get("mysqld", "DB_DATABASE")
	DB_USERNAME = config.get("mysqld", "DB_USERNAME")
	DB_PASSWORD = config.get("mysqld", "DB_PASSWORD")		

def processDiceDataFromScraping(jobsite, searchstring, citytosearch, ziptosearch):

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
				date = trTree[3].text.strip()
				
				joblistfile.write(jobname + '\t' + joblink + '\t' + companyname + '\t' + companylink + '\t' + city + '\t' + date + '\n')

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
		print linecount
		lineparts = line.split('\t')
		postedDate = datetime.datetime.strptime(lineparts[5].strip(), '%b-%d-%Y').strftime('%Y-%m-%d')
		#queryData.append((lineparts[0], lineparts[1], lineparts[2], lineparts[4], postedDate, postedDate, now, postedDate, now))
		query = "INSERT INTO job_list (JobSite, SearchString, CityToSearch, Title, JobLink, CompanyName, City, OriginalDatePosted, LastDatePosted, LastUpdate) values ('%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s') ON DUPLICATE KEY UPDATE LastDatePosted='%s', LastUpdate='%s'" % (jobsite, searchstring, citytosearch, lineparts[0].replace("'", "\\'"), lineparts[1].replace("'", "\\'"), lineparts[2].replace("'", "\\'"), lineparts[4].replace("'", "\\'"), postedDate, postedDate, now, postedDate, now)
		print query
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

def downloadJobData(jobsite, searchstring, citytosearch, ziptosearch):
	if (jobsite == "dice"):
		processDiceDataFromScraping(jobsite, searchstring, citytosearch, ziptosearch)

def main(argv):

	jobsite = "dice"
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
		elif opt == '-s':
			searchstring = arg
		elif opt == '-c':
			citytosearch = arg
			if citytosearch == 'dc':
				ziptosearch = '20001'
			elif citytosearch == 'chicago':
				ziptosearch = '60606'
			else:
				print 'invalid city to search %s' % citytosearch
				sys.exit(1)

	downloadJobData(jobsite, searchstring, citytosearch, ziptosearch)
	loadDataIntoDBFromFile(jobsite, searchstring, citytosearch, ziptosearch)

if __name__ == "__main__":
	main(sys.argv[1:])