import urllib2
import re
response = urllib2.urlopen("http://www.dice.com/job/results/20001?b=7&caller=searchagain&n=50&q=technology+manager&src=19&x=all&p=z")
html = response.read()
response.close()
p = re.compile('summary')
print p.match(html)
