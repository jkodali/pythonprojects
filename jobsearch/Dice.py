import urllib2
import re



def processDiceData():
	response = urllib2.urlopen("http://www.dice.com/job/results/20001?b=7&caller=searchagain&n=50&q=technology+manager&src=19&x=all&p=z")
	fullhtmlString = response.read()
	response.close()
	tablestart = re.compile('<table class="summary" cellspacing="0">')
	tablestartmatch = tablestart.search(fullhtmlString)

	fromtableString = fullhtmlString[tablestartmatch.start():]
	tableend = re.compile("</table>")
	tableendmatch = tableend.search(fromtableString)
	maintableHTML = fromtableString[:tableendmatch.end()]

	print maintableHTML

def main():
	processDiceData()

if __name__ == "__main__":
	main()