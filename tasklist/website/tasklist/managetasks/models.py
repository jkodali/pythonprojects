from django.db import models
import datetime

# Create your models here.
class TaskList(models.Model):
	id = models.DecimalField(max_digits=19, decimal_places=0, primary_key=True)
	user_id = models.DecimalField(max_digits=19, decimal_places=0)
	task = models.CharField(max_length=8000)
	create_date = models.DateTimeField()
	last_update = models.DateTimeField()
	category = models.DecimalField(max_digits=4, decimal_places=0)
	store = models.DecimalField(max_digits=4, decimal_places=0)
	start_date = models.DateTimeField()
	next_date = models.DateTimeField()
	custom_reminder_in_hours = models.DecimalField(max_digits=5, decimal_places=0)
	frequency = models.CharField(max_length=255)
	end_date = models.DateTimeField()
	instances_to_stop_after = models.DecimalField(max_digits=5, decimal_places=0)
	repeat_after_previous_done = models.BooleanField()

	def __str__(self):
		return self.task

	def getFriendlyDate(self):
		return self.next_date
		if self.next_date.year != datetime.date.today().year:
			return self.next_date
		else:
			return '%s/%s' % (self.next_date.month, self.next_date.day) 

	class Meta:
		db_table = "task_list"
		ordering = ['next_date','id']
