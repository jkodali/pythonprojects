from django.shortcuts import render
from django.http import HttpResponse
from models import JobList
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from forms import GetJobListForm
import datetime

# Create your views here.
def index(request):
	message = ""
	citylist = ['dc','chicago']
	searchstringlist = ['technology+manager']
	jobsitelist = ['dice']
	for jobsite in jobsitelist:
		for city in citylist:
			for searchstring in searchstringlist:
				message = message + "<a href='./%s/%s/%s?page=1'>%s - %s - %s</a><br />" % (jobsite, city, searchstring, jobsite, city, searchstring)
	return HttpResponse(message) 

def joblist(request, jobsite, city, searchstring):
	test = ""
	if request.method == "POST":
		form = GetJobListForm(request.POST)
		if form.is_valid():
			cursor = connection.cursor()
			if form.data['idToUnSave'] != 0:
				cursor.execute("update job_list set Saved = 0 where Id = %s" % form.data['idToUnSave'])
			if form.data['idToSave'] != 0:
				cursor.execute("update job_list set Saved = 1 where Id = %s" % form.data['idToSave'])

	fulljoblist = JobList.objects.filter(JobSite=jobsite, SearchString=searchstring, CityToSearch=city)
	paginator = Paginator(fulljoblist, 50)

	pageNumber = request.GET.get('page')
	try:
		joblist = paginator.page(pageNumber)
	except PageNotAnInteger:
		joblist = paginator.page(1)
	except EmptyPage:
		joblist = paginator.page(1)
	context = {'joblist': joblist }
	return render(request, 'getjoblist/index.html', context)
