from django.shortcuts import render
from django.http import HttpResponse
from models import JobList, LastSearchTime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from forms import GetJobListForm
import datetime

# Create your views here.
def index(request):
	searchlist = LastSearchTime.objects.all()

	city = ''
	jobsite = ''
	treeList = {}
	for search in searchlist:
		if city != search.City:
			city = search.City
			treeList[city] = {}
			jobsite = search.JobSite
			treeList[city][jobsite] = {}
			treeList[city][jobsite][search.SearchString] = ''
		elif jobsite != search.JobSite:
			jobsite = search.JobSite
			treeList[search.City][jobsite] = {}
			treeList[search.City][jobsite][search.SearchString] = ''
		else:
			treeList[search.City][search.JobSite][search.SearchString] = ''

	message = "<ul>"
	for city in treeList:
		message = message + "<li><font face='Sans-Serif'>%s</font>" % city
		message = message + "<ul>"
		for jobsite in treeList[city]:
			message = message + "<li><font face='Sans-Serif'>%s</font>" % jobsite
			message = message + "<ul>"
			for searchstring in treeList[city][jobsite]:
				message = message + "<li><a href='./%s/%s/%s?page=1'><font face='Sans-Serif'>%s</font></a></li>" % (jobsite, city, searchstring, searchstring)
			message = message + "</ul></li>"
		message = message + "</ul></li>"
	message = message + "</ul>"


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
