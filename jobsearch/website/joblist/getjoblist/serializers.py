from django.forms import widgets
from rest_framework import serializers
from models import JobList, LastSearchTime

class JobListSerializer(serializers.ModelSerializer):
	class Meta:
		model = JobList
		fields = ('Id', 'JobSite', 'SearchString', 'CityToSearch', 'Title', 'JobLink', 'CompanyName', 'City', 'OriginalDatePosted', 'LastDatePosted', 'LastUpdate', 'CityToSearch', 'Saved')


class LastSearchTimeSerializer(serializers.ModelSerializer):
	class Meta:
		model = LastSearchTime
		fields = ('Id', 'JobSite', 'SearchString', 'City', 'LastUpdate')