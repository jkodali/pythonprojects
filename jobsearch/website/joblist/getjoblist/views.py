from django.shortcuts import render
from django.http import HttpResponse
from models import DiceJobList

# Create your views here.
def index(request):
	return HttpResponse("Hello, world. You're at the polls index.")

def dicelist(request, pageNumber):
	if pageNumber is None:
		pageNumber = 1
	else:
		pageNumber = int(pageNumber)
	joblist = DiceJobList.objects.all()[((pageNumber-1)*50+1):((pageNumber)*50)]
	#return HttpResponse(joblist[0].City)
	context = {'joblist': joblist, 'nextPageNumber': pageNumber+1, 'prevPageNumber': pageNumber-1 }
	return render(request, 'getjoblist/index.html', context)
