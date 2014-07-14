from django.shortcuts import render
from django.http import HttpResponse
from models import JobList, SavedJobs
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
			savedJob = SavedJobs(JobId=form.cleaned_data['idToSave'], LastUpdate=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			savedJob.save()

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
