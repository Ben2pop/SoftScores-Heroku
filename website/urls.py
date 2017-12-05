from django.conf.urls import url, include
from website import views

app_name = 'website'
urlpatterns = [
    url(r'^hr_index/$', views.HRIndex.as_view(), name='hr_index'),
    url(r'^candidate_index/$', views.CandidateIndex.as_view(),name='candidate_index'),
    url(r'^employee_index/$', views.EmployeeIndex.as_view(),name='employee_index'),
    url(r'^addproject/$', views.ProjectCreate.as_view(), name='add_project'),
    url(r'^addteam/$', views.TeamCreate.as_view(), name='add_team'),
    url(r'^linkteam/$', views.LinkTeam.as_view(), name='link_team'),
    url(r'^linkteam2/$', views.TeamSelect, name='team_select'),
    url(r'^project/(?P<pk>[0-9]+)/$',views.ProjectDetailView.as_view(), name='ProjectDetails'),
    url(r'^project/(?P<pk1>[0-9]+)/(?P<pk2>[0-9]+)/$',views.EmployeeDetailView.as_view(), name='EmployeDetails'),
    url(r'^project/(?P<pk1>[0-9]+)/(?P<pk2>[0-9]+)/api/chart/data/$',views.EmployeeChartData.as_view(), name='employeechartdata'),
    url(r'^project/(?P<pk>[0-9]+)/api/chart/data/$', views.ChartData.as_view(), name='chartdata'),

]
