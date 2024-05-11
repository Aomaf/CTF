# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.home import views
from .forms import ImageFileUploadForm
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView


urlpatterns = [
    
    # The home page
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
	path('challenges', views.viewChallenges, name='challenges'),
   	path('addChallenge', views.addChallenge, name='addChallenge'),
	path('editChallenge/<viewc>', views.editChallenge, name='editChallenge'),
 	path('challenge/<viewc>', views.viewChallenge, name='challenge'),
 	path('submissions', views.viewSubmissions, name='submissions'),
 	path('submission/<sid>', views.submission, name='submission'),
  	path('competitions', views.viewEvents, name='competitions'),
 	path('addEvent', views.addEvent, name='addEvent'),
	path('editEvent/<eID>', views.editEvent, name='editEvent'),
	path('competition/<eID>', views.viewEvent, name='competition'),
   	path('challengeResult/<chId>', views.showResult, name='challengeResult'),
	path('references', views.viewReferences, name='references'),
 	path('addRef', views.addReference, name='addRef'),
	path('editRef/<refID>', views.editReference, name='editRef'),
	path('groupRegisteration/<compID>', views.registerAGroup, name='groupRegisteration'),
	path('groupEditing/<str:eID>/<str:gID>', views.editGroup, name='groupEditing'),
	path('scoreboard/<eID>', views.viewScoreBoard, name='scoreboard'),
	re_path(r'^api/getMember/', views.getMember, name='getMember'),

	path('pageuser', views.page_user, name='pageuser'),
	path('users', views.users, name='users'),
 	path('userEdit/<uid>', views.userEdit, name='userEdit'),
	path('contestants', views.viewContestants, name='contestants'),
	path('contestant/<cID>', views.viewContestant, name='contestant'),
	path('file/<sID>', views.viewFile, name='file'),
	path('viewMainFile/<str:cID>/<str:target>', views.viewMainFile, name='viewMainFile'),
 
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]