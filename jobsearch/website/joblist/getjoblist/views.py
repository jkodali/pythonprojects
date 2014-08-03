from django.shortcuts import render,get_object_or_404
from rest_framework.response import Response
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
import datetime
from rest_framework import generics

from models import JobList, LastSearchTime
from forms import GetJobListForm
from serializers import JobListSerializer, LastSearchTimeSerializer


class LastSearchTimeList(generics.ListCreateAPIView):
	queryset = LastSearchTime.objects.all()
	serializer_class = LastSearchTimeSerializer

class JobListAPI(generics.ListCreateAPIView):
	serializer_class = JobListSerializer

	def get_queryset(self):
		jobsite = self.kwargs['jobsite']
		searchstring = self.kwargs['searchstring']
		city = self.kwargs['city']
		return JobList.objects.filter(JobSite=jobsite, SearchString=searchstring, CityToSearch=city)

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
			treeList[city][jobsite][search.SearchString] = search.LastUpdate
		elif jobsite != search.JobSite:
			jobsite = search.JobSite
			treeList[search.City][jobsite] = {}
			treeList[search.City][jobsite][search.SearchString] = search.LastUpdate
		else:
			treeList[search.City][search.JobSite][search.SearchString] = search.LastUpdate

	message = "<ul>"
	message = message + "<li><a href='./savedjobs'><font face='Sans-Serif'>Saved Jobs</font></a></li>"
	for city in treeList:
		message = message + "<li><font face='Sans-Serif'>%s</font>" % city
		message = message + "<ul>"
		for jobsite in treeList[city]:
			message = message + "<li><font face='Sans-Serif'>%s</font>" % jobsite
			message = message + "<ul>"
			for searchstring in treeList[city][jobsite]:
				updated = treeList[city][jobsite][searchstring].strftime('%Y-%m-%d %H:%M:%S')
				message = message + "<li><a href='./%s/%s/%s?page=1'><font face='Sans-Serif'>%s - %s</font></a></li>" % (jobsite, city, searchstring, searchstring, updated)
			message = message + "</ul></li>"
		message = message + "</ul></li>"
	message = message + "</ul>"

	return HttpResponse(message) 

def savedjobs(request):
	if request.method == "POST":
		form = GetJobListForm(request.POST)
		cursor = connection.cursor()
		if form.data['idToUnSave'] != 0:
			cursor.execute("update job_list set Saved = 0 where Id = %s" % form.data['idToUnSave'])

	savedJobList = JobList.objects.filter(Saved=1)
	context = {'savedJobList': savedJobList}
	return render(request, 'getjoblist/savedjobs.html', context)

def joblist(request, jobsite, city, searchstring):
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
