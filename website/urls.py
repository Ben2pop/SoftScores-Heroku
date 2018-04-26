from django.conf.urls import url, include
from website.views import *
from website import views

app_name = 'website'
urlpatterns = [
    url(r'^hr_index/$', HRIndex.as_view(), name='hr_index'),
    url(r'^create_project/$', CreateProject.as_view(), name='create_project'),
    url(r'^candidate_index/$', CandidateIndex.as_view(),name='candidate_index'),
    url(r'^employee_index/(?P<pk2>[0-9]+)/$', EmployeeIndex.as_view(),name='employee_index'),
    url(r'^addproject/$', ProjectCreate.as_view(), name='add_project'),
    url(r'^project/(?P<pk1>[0-9]+)/create_team/$', CreateTeam.as_view(), name='create_team'),
    url(r'^project/(?P<pk1>[0-9]+)/addteam/$', TeamCreate.as_view(), name='add_team'),
    #url(r'^project/(?P<pk1>[0-9]+)/linkteam2/$', TeamSelect, name='team_select'),
    url(r'^project/(?P<pk1>[0-9]+)/$',ProjectDetailView.as_view(), name='ProjectDetails'),
    url(r'^project/(?P<pk1>[0-9]+)/api/chart/data2/$',TeamChartData.as_view(), name='TeamChartData'),
    url(r'^project/employee/(?P<pk1>[0-9]+)/(?P<pk2>[0-9]+)/$',EmployeeDetailView.as_view(), name='EmployeDetails'),
    url(r'^project/applicant/(?P<pk1>[0-9]+)/(?P<pk2>[0-9]+)/$',CandidateDetailView.as_view(), name='CandidateDetails'),
    url(r'^project/employee/(?P<pk1>[0-9]+)/(?P<pk2>[0-9]+)/api/chart/data/$',EmployeeChartData.as_view(), name='EmployeeChartData'),
    url(r'^project/applicant/(?P<pk1>[0-9]+)/(?P<pk2>[0-9]+)/api/chart/data3/$',applicantChartData.as_view(), name='CandidateChartData'),
    url(r'^project/(?P<pk1>[0-9]+)/recruitment/$', RecruitmentPage.as_view(), name='recruitment'),
    url(r'^payment_form/$', payment_form.as_view(), name='payment'),
    url(r'^checkout/$', views.checkout, name="checkout_page"),
]
