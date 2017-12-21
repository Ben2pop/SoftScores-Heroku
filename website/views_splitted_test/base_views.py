import json
import math
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from website.models import Project, Team
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from registration.views import MyUser
from website.forms import EditSelectTeam
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from registration.models import MyUser
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from survey.models import Question,Answer,Survey
from survey.models.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from survey.models.response import Response as ResponseModel
from website.serializers import MyUserSerializer


class HomePage(TemplateView):
    template_name= 'index.html'

class LinkTeam(generic.ListView):
    template_name = 'link_project.html'

    def get_queryset(self):
        #import pdb; pdb.set_trace()
        #team2 = Team.objects.all().filter(team_hr_admin = self.request.user)
        queryset = Team.objects.filter(team_hr_admin=self.request.user)
        return queryset

def TeamSelect(request):
    #import pdb; pdb.set_trace()
    if request.method == "POST":
        select_form = EditSelectTeam(request.user, request.POST)
        if select_form.is_valid():
            data = select_form.cleaned_data['team_choice']
            obj2 = Project.objects.filter(project_hr_admin=request.user)
            obj3 = obj2.latest('id')
            if obj3.team_id == None:
                obj3.team_id = data
                obj3.save()
                obj4 = obj3.team_id
                obj5 = obj4.members.all()

                for i in obj5:
                    current_site = get_current_site(request)
                    message = render_to_string('acc_join_email.html', {
                        'user': i.first_name,
                        'domain':current_site.domain,
                        })
                    mail_subject = 'You have been invited to SoftScores.com please LogIn to get access to the app'
                    to_email = i.email
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.send()
                messages.success(request, 'test')
                return HttpResponseRedirect(reverse('website:ProjectDetails', kwargs={'pk':obj3.id}))
            else:
                print('this project has already a team')
        else:
            print('Non Valid form')

    else:
        select_form = EditSelectTeam(request.user)
    return render(request,'link_project.html',
                            {'select_form':select_form })


class HRIndex(generic.ListView):
    #import pdb; pdb.set_trace()
    template_name = "HR_index.html"
    model = Project


class CandidateIndex(TemplateView):
    #import pdb; pdb.set_trace()
    template_name = "candidate_index.html"

class EmployeeIndex(TemplateView):
    #import pdb; pdb.set_trace()
    template_name = "employee_index.html"

    def get_context_data(self, **kwargs):
        context = super(EmployeeIndex, self).get_context_data(**kwargs)
        surveys = Survey.objects.filter(is_published=True)
        if not self.request.user.is_authenticated():
            surveys = surveys.filter(need_logged_user=False)
        context['surveys'] = surveys
        return context


class ProjectCreate(CreateView, LoginRequiredMixin):
    model = Project
    fields = ['name']
    template_name = 'project_form.html'

    def form_valid(self, form):
        form.instance.project_hr_admin = self.request.user
        return super(ProjectCreate, self).form_valid(form)



class ProjectDetailView(generic.DetailView, LoginRequiredMixin):
    #import pdb; pdb.set_trace()
    model = Project
    template_name = 'project_details.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        try:
            team_name = Project.objects.get(id=self.kwargs['pk']).team_id.members.all()
            context['team_name'] = team_name
        except AttributeError:
            pass
        return context


class EmployeeDetailView(generic.DetailView, LoginRequiredMixin):
    #import pdb; pdb.set_trace()
    model = MyUser
    template_name = 'Employee_Details.html'


    def get_object(self, queryset=None):
        return get_object_or_404(MyUser, pk=self.kwargs['pk2'], members__project=self.kwargs['pk1'])

    def get_context_data(self, **kwargs):
        context = super(EmployeeDetailView, self).get_context_data(**kwargs)
        employee_name = MyUser.objects.get(id=self.kwargs['pk2'])
        team_list = Project.objects.get(id=self.kwargs['pk1']).team_id.members.all()
        team_list_pop = Project.objects.get(id=self.kwargs['pk1']).team_id.members.all().exclude(id=self.kwargs['pk2'])
        context={
            'employee_name' : employee_name,
            'team_list' : team_list,
            'team_list_pop' : team_list_pop
        }
        return context








class TeamCreate(CreateView):

    model = Team
    fields = ['team_name']
    template_name = 'team_form.html'

    def form_valid(self, form):
        import pdb; pdb.set_trace()
        valid = super(TeamCreate, self).form_valid(form)
        form.instance.team_hr_admin = self.request.user
        obj = form.save()
        #SELECT * FROM project WHERE user = 'current_user' AND team_id = NULL
        obj2 = Project.objects.get(project_hr_admin=self.request.user, team_id=None)
        obj2.team_id = obj
        obj2.save()
        return valid
        return super(TeamCreate, self).form_valid(form)

    def get_success_url(self):
        #import pdb; pdb.set_trace()
        project = Project.objects.get(team_id=None, project_hr_admin=self.request.user)
        return project.get_absolute_url()
