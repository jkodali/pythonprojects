from django.shortcuts import render
from forms import UserForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from models import TaskList
from django.db import connection
import json
import datetime

# Create your views here.
def register(request):

	# A boolean value for telling the template whether the registration was successful.
	# Set to False initially. Code changes value to True when registration succeeds.
	registered = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm.
		user_form = UserForm(data=request.POST)

		# If the two forms are valid...
		if user_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()

			# Update our variable to tell the template registration was successful.
			registered = True

		# Invalid form or forms - mistakes or something else?
		# Print problems to the terminal.
		# They'll also be shown to the user.
		else:
			print user_form.errors

	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank, ready for user input.
	else:
		user_form = UserForm()

	# Render the template depending on the context.
	return render(
			request,
			'register.html',
			{'user_form': user_form, 'registered': registered}
	)

def user_login(request):
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the login form.
		username = request.POST['username']
		password = request.POST['password']

		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)

		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user
		# with matching credentials was found.
		if user:
			# Is the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We'll send the user back to the homepage.
				login(request, user)
				return HttpResponseRedirect('/managetasks/')
			else:
				# An inactive account was used - no logging in!
				return HttpResponse("Your account is disabled.")
		else:
			# Bad login details were provided. So we can't log the user in.
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")

	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the
		# blank dictionary object...
		return render(request, 'login.html')

@login_required
def savetasks(request):
	if request.method == "POST":
		now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		today = datetime.datetime.now().strftime('%Y-%m-%d')
		save_type = request.POST['save_type']
		task_name = request.POST['task_name']
		due_date = request.POST['due_date']
		if (save_type == 'add'):
			cursor = connection.cursor()
			sqlscript = "insert into task_list (user_id, task, create_date, last_update, start_date, next_date) values (%s, '%s', '%s', '%s', '%s', '%s')" % (request.user.id, task_name, today, now, due_date, due_date)
			cursor.execute(sqlscript)

			response_dict = {}
			response_dict.update({'server_response': 'hi'})
			return HttpResponse(json.dumps(response_dict), mimetype='application/javascript')

@login_required
def index(request):
	taskList = TaskList.objects.filter(user_id=request.user.id)
	today = datetime.date.today()
	tomorrow = today + datetime.timedelta(days=1)

	list_past = []
	list_today = []
	list_tomorrow = []
	list_future = []
	list_nodate = []

	for task in taskList:
		if task.next_date is None:
			list_nodate.append(task)
		elif task.next_date < today:
			list_past.append(task)
		elif task.next_date == today:
			list_today.append(task)
		elif task.next_date == tomorrow:
			list_tomorrow.append(task)
		elif task.next_date > tomorrow:
			list_future.append(task)

	return render(
			request,
			'index.html',
			{'list': taskList, 'list_past': list_past, 'list_today': list_today, 'list_tomorrow': list_tomorrow, 'list_future': list_future, 'list_nodate': list_nodate, 'today': today}
	)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
	# Since we know the user is logged in, we can now just log them out.
	logout(request)

	# Take the user back to the homepage.
	return HttpResponseRedirect('/managetasks/login/')