from django.conf.urls import url
from registration import views

app_name = 'registration'
urlpatterns = [
    url(r'^hr_register/$', views.registerHR, name='hr_register'),
    url(r'^auth_HRlogin/$', views.HR_login, name='HRlogin'),
    url(r'^update/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.CandidateSignIn, name='CandidateSignIn'),
    url(r'^auth_logout/$', views.user_logout, name='logout'),
    url(r'^project/(?P<pk1>[0-9]+)/auth_team_register3/$',
        views.TeamRegister2, name='team_register3'),
    url(r'^project/(?P<pk1>[0-9]+)/auth_applicant_register3/$',
        views.applicantregister2, name='applicant_register3'),

]
