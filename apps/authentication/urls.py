# -*- encoding: utf-8 -*-


from django.urls import path
from .views import loginPage, registerPage, logoutPage
from .views import activatePage, recoverPasswordPage

urlpatterns = [
    path('login/', loginPage, name="login"),
    path('register/', registerPage, name="register"),
    path('recover/', recoverPasswordPage, name="recover"),
    path("logout/", logoutPage, name="logout"),
	path('activate/<uidb64>/<token>', activatePage, name='activate')
]
