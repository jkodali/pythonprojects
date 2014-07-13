from django.shortcuts import render
from django.http import HttpResponse
from models import JobList

# Create your views here.
def index(request):
	message = ""
	citylist = ['dc','chicago']
	searchstringlist = ['technology+manager']
	jobsitelist = ['dice']
	for jobsite in jobsitelist:
		for city in citylist:
			for searchstring in searchstringlist:
				message = message + "<a href='./%s/%s/%s'>%s - %s - %s</a><br />" % (jobsite, city, searchstring, jobsite, city, searchstring)
	return HttpResponse(message) 

def joblist(request, jobsite, city, searchstring, pageNumber):
	if pageNumber is None:
		pageNumber = 1
	else:
		pageNumber = int(pageNumber)
	fulljoblist = JobList.objects.filter(JobSite=jobsite, SearchString=searchstring, CityToSearch=city)
	joblist = fulljoblist[((pageNumber-1)*50+1):((pageNumber)*50)]
	#return HttpResponse(joblist[0].City)
	context = {'joblist': joblist, 'nextPageNumber': pageNumber+1, 'prevPageNumber': pageNumber-1, 'total': len(fulljoblist), 'start': (((pageNumber-1)*50+1)), 'end': (((pageNumber)*50)) }
	return render(request, 'getjoblist/index.html', context)
