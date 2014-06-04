import urllib2
import re
import xml.etree.ElementTree as ET
import string


def processDiceDataFromScraping():

	loopcount = 50
	totalcount = 0

	joblistfile = open('dicejoblist.txt', 'w')

	while loopcount == 50:
		loopcount = 0
		response = urllib2.urlopen("http://www.dice.com/job/results/20001?b=7&o=%s&caller=searchagain&n=50&q=technology+manager&src=19&x=all&p=z" % totalcount)
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
				jobname = trTree[0][0][0].text.strip()
				joblink = trTree[0][0][0].attrib.get('href').strip()

				if len(list(trTree[1])) == 1:
					companyname = trTree[1][0].text.strip()
					companylink = trTree[1][0].attrib.get('href').strip()
				else:
					companyname = trTree[1].text.strip()

				if len(list(trTree[2])) == 1:
					city = trTree[2][0].text.strip()
				else:
					city = trTree[2].text.strip()
				date = trTree[3].text.strip()
				

				joblistfile.write(jobname + '\t' + joblink + '\t' + companyname + '\t' + companylink + '\t' + city + '\t' + date + '\n')

def main():
	processDiceDataFromScraping()

if __name__ == "__main__":
	main()