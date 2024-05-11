# -*- encoding: utf-8 -*-


from django.db import models
from django.contrib.auth.models import User
from django_random_id_model import RandomIDModel

class Competition(RandomIDModel):
	title = models.CharField(max_length=500, null = False)
	start_date = models.DateTimeField(auto_now_add=False,null = True)
	end_date = models.DateTimeField(auto_now_add=False,null = True)
	description = models.TextField(null = True)
	alignment = models.IntegerField(default=0) # 0 means right and 1 means left
	is_hackathon = models.BooleanField(default=False)
 
class Reference(RandomIDModel):
	level = models.CharField(max_length=20,null = True)
	type = models.TextField(null = True)
	references = models.TextField(null = True)
 
class Challenge(RandomIDModel):
	title = models.CharField(max_length=50,null = True)
	level = models.CharField(max_length=20,null = True)
	description = models.TextField(null = True)
	alignment = models.IntegerField(default=0) # 0 means right and 1 means left
	attachment = models.FileField(null=True)
	code = models.TextField(null = True)
	type = models.TextField(null = True)
	start_date = models.DateTimeField(auto_now_add=False,null = True)
	end_date = models.DateTimeField(auto_now_add=False,null = True)
	pub_date = models.DateTimeField(auto_now_add=True)
	filepath = models.FileField(null=True) # for Java by default
	filepathPy = models.FileField(null=True)
	filepathCpp = models.FileField(null=True)
	solve = models.TextField(null = True)
	width = models.IntegerField( default = 0)
	height = models.IntegerField( default = 0)
	references = models.TextField(null=True)
 
	# foreignkeys
	belongsToEvent = models.ForeignKey(Competition, on_delete=models.CASCADE, unique=False, null=True)
	reference = models.ForeignKey(Reference, on_delete=models.CASCADE, unique=False, null=True)
	class Meta:
		ordering = ['-pub_date']

class Contestant(RandomIDModel):
	user_id = models.CharField(max_length=10, null = False)
	user_nameF = models.CharField(max_length=50, null = True)
	user_nameM = models.CharField(max_length=50, null = True)
	user_nameM2 = models.CharField(max_length=50, null = True)
	user_nameL = models.CharField(max_length=50, null = True)
	is_user = models.BooleanField(default=True) # determine whether user is contestant or admin/staff
	user_scoreL1 = models.FloatField(default=0)
	user_scoreL2 = models.FloatField(default=0)
	user_scoreL3 = models.FloatField(default=0)
	user_scoreL4 = models.FloatField(default=0)
	user_scoreL5 = models.FloatField(default=0)

class Group(RandomIDModel):
    
    name = models.CharField(max_length=100, null = True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, null=True, related_name="user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, null=True, related_name="user2")
    user3 = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, null=True, related_name="user3")
    user4 = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, null=True, related_name="user4")
    user5 = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, null=True, related_name="user5")
    
    event = models.ForeignKey(Competition, on_delete=models.CASCADE, unique=False, null=True)

class Submission(RandomIDModel):
	level = models.CharField(max_length=20,null = True)
	user_solve = models.TextField(null = True)
	language = models.CharField(max_length=500,null=True)
	view_date = models.DateTimeField(auto_now_add=False, null=True)
	solve_date = models.DateTimeField(auto_now_add=False, null=True)
	result = models.FloatField(default=0)
	filepath = models.FileField(null=True)
	status = models.IntegerField(default=-1) # -1 means just viewed/opened by contestant, 0 needs execution, 1 means processed and done, 3 means error while compiling/executing
	json_text = models.TextField(null = True)
	sum_result = models.FloatField(default=0)
	counter = models.IntegerField(default=0)
	note = models.TextField(null=True) # for execution errors
	diff = models.FloatField(null = True)
	
 	# foreignkeys
	challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, unique=False)
	contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE, unique=False, null=True)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, unique=False, null=True)
	class Meta:
		ordering = ['-solve_date']