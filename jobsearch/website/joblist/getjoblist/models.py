from django.db import models

# Create your models here.
class DiceJobList(models.Model):
	Title = models.CharField(max_length=128)
	JobLink = models.CharField(max_length=512)
	CompanyName = models.CharField(max_length=64)
	City = models.CharField(max_length=128)
	OriginalDatePosted = models.DateTimeField()
	LastDatePosted = models.DateTimeField()
	LastUpdate = models.DateTimeField()

	def __str__(self):
		return self.Title

	class Meta:
		db_table = "dice_job_list"
		ordering = ['-OriginalDatePosted']