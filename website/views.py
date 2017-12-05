from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Project, Team
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from registration.views import MyUser
from .forms import EditSelectTeam
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from registration.models import MyUser
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from survey.models.survey import Survey
from rest_framework.views import APIView
from rest_framework.response import Response

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


class EmployeeChartData(APIView):
    #import pdb; pdb.set_trace()
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None, *args, **kwargs):

        project_name = Project.objects.get(id=kwargs['pk1']).name
        team_name_list = Project.objects.get(id=kwargs['pk1']).team_id.members.all()
        team_member_count = Project.objects.get(id=kwargs['pk1']).team_id.members.count()
        main_items2 = [1,2,3,-4,5,6,-7,8,9,-10,-11,12,13,14,15,16]
        info_process_data = [4,6,2,8,4]
        info_process_data2 = [8,2,5,2,4]
        action_process_data = [5,3,9]
        motivation_data = [4,5,1,8]
        behaviour_data = [6,3,9,1]

        data = {
            #labels

            "labels_main_graph":labels_main_graph,
            "information_processing_label": information_processing_label,
            "action_process_label": action_process_label,
            "motivation_label": motivation_label,
            "behaviour_label":behaviour_label,
            #data

            "main2": main_items2,
            "info_process_data": info_process_data,
            "info_process_data2": info_process_data2,
            "action_process_data": action_process_data,
            "motivation_data":motivation_data,
            "behaviour_data":behaviour_data,
            #other
            "project_name":project_name,
            "team_member_count":team_member_count,
            #"team_name_list":team_name_list

        }
        return Response(data)




class ChartData(APIView):

    authentication_classes = []
    permission_classes = []


    def get(self, request, format=None, *args, **kwargs):

        team_name = Project.objects.get(id=kwargs['pk']).team_id.team_name

        main_items = [user_count, project_count,team_member_count,28,12,32]
        main_items2 = [1,2,3,-4,5,6,-7,8,9,-10,-11,12,13,14,15,16]
        info_process_data = [4,6,2,8,4]
        info_process_data2 = [8,2,5,2,4]
        action_process_data = [5,3,9]
        motivation_data = [4,5,1,8]
        behaviour_data = [6,3,9,1]
        data = {
            #labels
            "labels":labels,
            "labels_main_graph":labels_main_graph,
            "information_processing_label": information_processing_label,
            "action_process_label": action_process_label,
            "motivation_label": motivation_label,
            "behaviour_label":behaviour_label,
            #data
            "main":main_items,
            "main2": main_items2,
            "info_process_data": info_process_data,
            "info_process_data2": info_process_data2,
            "action_process_data": action_process_data,
            "motivation_data":motivation_data,
            "behaviour_data":behaviour_data,

            #other
            "team_name":team_name,
            "team_list":team_list
        }
        return Response(data)


# labels data #
labels_main_graph = [
                         ["ProActive", "Reactive"],
                         ["General","Details"],
                         ["Black/White", "Continuum"],
                         ["Best Scenario","Worst Scenerio"],
                         ["Toward","Away from"],
                         ["Option","Procedure"],
                         ["Frame of reference"],
                         ["Externally referenced", "Internally Referenced"],
                         ["Perceiving Process"],
                         ["Affiliation Management"],
                         ["Knowledge sort"],
                         ["Time Sense"],
                         ["Variety", "Routine"],
                         ["Matching","Mismatching"],
                         ["Representational Sort"],
                         ["Preferences Sort"],
                        ]

information_processing_label = [
                                    "Black/White - Continuum",
                                    "Best Scenario - Worst Scenerio",
                                    "General-Details",
                                    "Matching VS Mismatching",
                                    "Time Sense"
                                   ]

action_process_label = [
                    ["Option - Procedure", ""],
                    ["","Knowledge sort"],
                    ["","ProActive - Reactive"]
                     ]

motivation_label = [
                        "Toward - Away from",
                        "Variety VS Routine",
                        "Preferences-Sort",
                        "Representational Sort"
                      ]

behaviour_label = [
              "Frame of reference",
              "Externally referenced – Internally Referenced",
              "Perceiving Process",
              "Affiliation – Management"
              ]

#end labels
