import json
from math import *
import math
import random
import itertools as it
import numpy as np
from scipy.stats.stats import pearsonr
from collections import Counter
from statistics import mode
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
from survey.models import Question,Answer,Survey
from survey.models.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from survey.models.response import Response as ResponseModel
from .serializers import MyUserSerializer, ProjectSerializer, TeamSerializer
from rest_framework.renderers import TemplateHTMLRenderer
from django.template.defaulttags import register

class HomePage(TemplateView):
    template_name= 'index.html'

class PricingPage(TemplateView):
    template_name="pricing.html"

class LinkTeam(generic.ListView):
    template_name = 'link_project.html'

    def get_queryset(self):
        #import pdb; pdb.set_trace()
        #team2 = Team.objects.all().filter(team_hr_admin = self.request.user)
        queryset = Team.objects.filter(team_hr_admin=self.request.user)
        return queryset


def TeamSelect(request, pk1=None):
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
                return HttpResponseRedirect(reverse('website:ProjectDetails', kwargs={'pk1':obj3.id}))
            else:
                print('this project has already a team')
        else:
            print('Non Valid form')

    else:
        #import pdb; pdb.set_trace()
        select_form = EditSelectTeam(request.user)
    return render(request,'link_project.html',
                            {'select_form':select_form })

class HRIndex(generic.ListView):
    #import pdb; pdb.set_trace()
    template_name = "HR_index.html"
    model = Project


    def get_queryset(self):
        return Project.objects.filter(project_hr_admin_id = self.request.user).order_by('-created_at')



    def get_context_data(self, **kwargs):
        #import pdb; pdb.set_trace()
        context = super(HRIndex,self).get_context_data(**kwargs)
        status_dict = {}
        for project in Project.objects.filter(project_hr_admin_id = self.request.user):
            proj_team_id = project.team_id
            proj_memb = proj_team_id.members.all()
            open_close = 1
            for memb in proj_memb:
                if not list(memb.response_set.all()):
                    status = False
                else:
                    status = True
                open_close = open_close*status
            status_dict.update({project.id:open_close})

        context['status_dict'] = status_dict
        return context




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

class ProjectCreate(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['name']
    template_name = 'project_form.html'

    def form_valid(self, form):
        form.instance.project_hr_admin = self.request.user
        return super(ProjectCreate, self).form_valid(form)

class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    #import pdb; pdb.set_trace()
    model = Project
    template_name = 'project_details.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Project,id=self.kwargs['pk1'])

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        try:

            team_name = Project.objects.get(id=self.kwargs['pk1']).team_id.members.all()
            score = get_team_cohesivenss_score(self)[0]

            all_user_response = 1
            for i in Project.objects.get(id=self.kwargs['pk1']).team_id.members.all():
                if i.response_set.all().count() == 0:
                    all_user_response = all_user_response * 0
                else:
                    all_user_response = all_user_response * 1

            context['team_name'] = team_name
            context['score'] = score
            context['all_user_response'] = all_user_response
        except AttributeError:
            pass
        return context

class EmployeeDetailView(LoginRequiredMixin, generic.DetailView):
    #import pdb; pdb.set_trace()
    model = MyUser
    template_name = 'employee_details.html'


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
            'team_list_pop' : team_list_pop,
        }
        return context

class CandidateDetailView(LoginRequiredMixin, generic.DetailView):
    #import pdb; pdb.set_trace()
    model = MyUser
    template_name = 'applicant_details.html'

    def get_object(self, queryset=None):
        return get_object_or_404(MyUser, pk=self.kwargs['pk2'])

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        team_score = get_team_cohesivenss_score(self)[0]
        applicant_score = get_applicant_cohesivenss_score(self)[0][0]
        diff_score = get_applicant_cohesivenss_score(self)[0][0] - get_team_cohesivenss_score(self)[0]
        team_list_pop = Project.objects.get(id=self.kwargs['pk1']).team_id.members.all().exclude(id=self.kwargs['pk2'])
        context['team_score'] = team_score
        context['applicant_score'] = applicant_score
        context['diff_score'] = diff_score
        context['team_list_pop'] = team_list_pop

        return context



class TeamCreate(CreateView):

    model = Team
    fields = ['team_name']
    template_name = 'team_form.html'

    def form_valid(self, form):
        #import pdb; pdb.set_trace()
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
    #queryset = MyUser.objects.all()
    #serializer_class = MyUserSerializer
    #permission_classes = []
    http_method_names = ['get',]

    #authentication_classes = []
    #permission_classes = []
    #serializer_class = MyUserSerializer

    def get_serializer_class(self):
        return self.serializer_class



    def get(self, request, format=None, *args, **kwargs):
        current_project = get_current_team(self)
        #info Process
        info_array2 = get_employee_info_array(self)
        motivation_array2 = get_employee_motivation_array(self)
        action_array2 = get_employee_action_array(self)
        behav_array2 = get_employee_behav_array(self)
        #info_array = get_info_array(self)[1]
        #motivation_array = get_motivation_array(self)[1]
        #action_array = get_action_array(self)[1]
        #behaviour_array = get_behaviour_array(self)[1]
        complete = get_complete_data(self)
        current_user = get_current_user(self)
        current_team_member_id = get_current_team_member_id(self)

        label_pref = get_employee_motivation_array(self)[2][int(self.kwargs['pk2'])]
        affiliation_label = get_employee_action_array(self)[2][int(self.kwargs['pk2'])]
        knowledge_label = get_employee_behav_array(self)[2][int(self.kwargs['pk2'])]





        processing_information_label = [
                                        ["General","Details"],
                                        ["Sameness","Difference"],
                                        ["Visual","Auditory"],
                                        ["Static","Process"],
                                        ["Best Scenario","Worst Scenario"],
                                        ["Binary","Shades"],
                                        ]

        motivation_label =[
                            ["External","Internal"],
                            ["Go Away","Toward"],
                            [label_pref],
                            ["Variety","Routine"],
                          ]

        action_label = [
                    ["Active","Reaction"],
                    [affiliation_label],
                    ["Option","Procedure"],
                    ["Perfection","Optimizing"],
                    ["Sensor","Intuition"]

        ]


        other_data_label = [
                    ["External locus","Internal locus"],
                    ["Strong Will","Compliant"],
                    ["In time","Through time"],
                    [knowledge_label],


        ]


        complete_label = [
                         ["General","Details"],
                         ["Sameness","Difference"],
                         ["Visual","Auditory"],
                         ["Static","Process"],
                         ["Best Scenario","Worst Scenario"],
                         ["Binary","Shades"],
                         ["External","Internal"],
                         ["Go Away","Toward"],
                         [label_pref],
                         ["Variety","Routine"],
                         ["Active","Reaction"],
                         [affiliation_label],
                         ["Option","Procedure"],
                         ["Perfection","Optimizing"],
                         ["Sensor","Intuition"],
                         ["External locus","Internal locus"],
                         ["Strong Will","Compliant"],
                         ["In time","Through time"],
                         [knowledge_label]
                         ]

        data = {
            #data
            "complete":complete,
            #"info_array":info_array,
            #"motivation_array":motivation_array,
            #"action_array": action_array,
            #"behaviour_array":behaviour_array,

            #labels
            "complete_label":complete_label,
            "processing_information_label":processing_information_label,
            "motivation_label":motivation_label,
            "action_label":action_label,
            "other_data_label": other_data_label,

            #other
            "current_user":current_user,
            "current_team_member_id":current_team_member_id,
            "info_array2":info_array2,
            "motivation_array2":motivation_array2,
            "action_array2":action_array2,
            'behav_array2':behav_array2

        }
        return Response(data)


def get_current_user(self):
    current_user = MyUser.objects.get(id = self.kwargs['pk2'])
    current_user_id = current_user.id
    return current_user_id

def get_current_team_member_id(self):
    current_team = Project.objects.get(id = self.kwargs['pk1']).team_id.members.all()
    team_id_list = [0]
    for member in current_team:
        member_id = member.id
        team_id_list.append(member_id)

    ind = team_id_list.index(int(self.kwargs['pk2']))
    team_id_list.pop(ind)
    return team_id_list

def get_current_team(self, format=None, *args, **kwargs):
    #import pdb; pdb.set_trace()
    current_team_member = Project.objects.get(id = self.kwargs['pk1']).team_id.members.all()
    members_response_list = []
    for member in current_team_member:
        member_id = member.id
        member_response = get_user_response(member_id)
        members_response_list.append({member_id:member_response})

    return members_response_list

def get_user_response(member_id):
    current_user = MyUser.objects.get(id = member_id) #current_user
    survey_team = Survey.objects.get(name= 'Survey SoftScores') #survey team (to change to final one)
    if ResponseModel.objects.filter(user = current_user, survey = survey_team):
        current_response = ResponseModel.objects.filter(user = current_user, survey = survey_team)[0]
        return current_response
    else:
        pass


def get_current_response(self, format=None, *args, **kwargs):
    current_user = MyUser.objects.get(id = self.kwargs['pk2']) #current_user
    survey_team = Survey.objects.get(name= 'Survey SoftScores') #survey team (to change to final one)
    if ResponseModel.objects.filter(user = current_user, survey = survey_team):
        current_response = ResponseModel.objects.filter(user = current_user, survey = survey_team)[0]
    else:
        pass
    return current_response


############ Complete Data ##############
def get_complete_data(self, format=None, *args, **kwargs):

    total_array = [get_employee_info_array(self)[0],get_employee_motivation_array(self)[0],get_employee_action_array(self)[0],get_employee_behav_array(self)[0]]
    test = get_employee_motivation_array(self)[2]
    complete_array = []
    for i in total_array:
        f = i[int(self.kwargs['pk2'])]
        complete_array = complete_array + f

    return complete_array

############ Processing Informations ##############

def get_employee_info_array(self, format=None, *args, **kwargs):
    response_list = get_current_team(self)
    info_array = get_info_array(response_list)
    return info_array

def get_info_array(array):
    #import pdb; pdb.set_trace()
    #current_response_list = get_current_team(self)
    current_response_list = array
    member_info_array_10 = {}
    member_info_array = {}
    for response_dic in current_response_list:
        current_response = list(response_dic.values())[0]
        chunk_score = get_chunk_score3(current_response)
        chunk_score_10 = (abs(get_chunk_score3(current_response)))/10
        info_score = get_info_relationship3(current_response)
        info_score_10 = abs((get_info_relationship3(current_response)))/10
        rep_system = get_rep_system3(current_response)
        rep_system_10 = (abs(get_rep_system3(current_response)))/10
        reality = get_reality_structure3(current_response)
        reality_10 = (abs(get_reality_structure3(current_response)))/10
        scenario = get_scenario_thinking3(current_response)
        scenario_10 = (abs(get_scenario_thinking3(current_response)))/10
        perceptual = get_perceptual_category3(current_response)
        perceptual_10 = (abs(get_perceptual_category3(current_response)))/10

        info_array_10 = [chunk_score_10,info_score_10,rep_system_10,reality_10,scenario_10,perceptual_10]
        member_info_array_10.update({current_response.user_id:info_array_10})
        info_array = [chunk_score,info_score,rep_system,reality,scenario,perceptual]
        member_info_array.update({current_response.user_id:info_array})
    return member_info_array, member_info_array_10

#------------------------------------------------------#

def get_chunk_score3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 1)
    answer_question2 = current_response.answers.get(question__quest_numb = 2)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "3":
        score1 = list(json_answer_question1.values())[0] #general
    else:
        score1 = -list(json_answer_question1.values())[0] #details

    if answer_key_question2 == "1" or "3":
        score2 = list(json_answer_question2.values())[0] #General
    else:
        score2 = -list(json_answer_question2.values())[0] #detail

    chunk_score = math.ceil((score1+score2)/2)

    return chunk_score

def get_info_relationship3(current_response):

    answer_question1 = current_response.answers.get(question__quest_numb = 5)
    answer_question2 = current_response.answers.get(question__quest_numb = 17)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0] #Sameness
    else:
        score1 = -list(json_answer_question1.values())[0] #Difference


    if answer_key_question2 == "1" or "2":
        score2 = list(json_answer_question2.values())[0]  #sameness
    else:
        score2 = -list(json_answer_question2.values())[0] #difference

    info_relationship_score = math.ceil((score1+score2)/2)

    return info_relationship_score

def get_rep_system3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 1)
    answer_question2 = current_response.answers.get(question__quest_numb = 16)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0] #visual
    else:
        score1 = -list(json_answer_question1.values())[0] #auditory


    if answer_key_question2 == "2" or "3":
        score2 = list(json_answer_question2.values())[0] #visual
    else:
        score2 = -list(json_answer_question2.values())[0] #auditory

    rep_system_score = math.ceil((score1+score2)/2)

    return rep_system_score

def get_reality_structure3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 1)
    answer_question2 = current_response.answers.get(question__quest_numb = 16)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]


    if answer_key_question2 == "2" or "3":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]
    info_relationship_score = math.ceil((score1+score2)/2)

    return info_relationship_score

def get_scenario_thinking3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 6)
    #answer_question2 = current_response.answers.get(question_id = 16)
    json_answer_question1 = json.loads(answer_question1.body)
    #json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    #answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "2" or "4":
        score1 = list(json_answer_question1.values())[0] #best scenario
    else:
        score1 = -list(json_answer_question1.values())[0] #worst scenario

    scenario_thinking_score = math.ceil((score1))

    return scenario_thinking_score

def get_perceptual_category3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 5)
    #answer_question2 = current_response.answers.get(question_id = 16)
    json_answer_question1 = json.loads(answer_question1.body)
    #json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    #answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0] #Binary
    else:
        score1 = -list(json_answer_question1.values())[0] #Shades

    perceptual_category_score = math.ceil(score1)

    return perceptual_category_score


############ End Processing Informations ##############

############ Motivation ##############

def get_employee_motivation_array(self, format=None, *args, **kwargs):
    response_list = get_current_team(self)
    motiv_array = get_motivation_array(response_list)
    return motiv_array

def get_motivation_array(array):

    current_response_list = array


    member_motivation_array = {}
    member_motivation_array_10 = {}
    pref_label_array = {}
    for response_dic in current_response_list:
        current_response = list(response_dic.values())[0]

        frame_reference = get_frame_reference2(current_response)
        frame_10 = (abs(frame_reference))/10
        motivation_direction = get_motivation_direction2(current_response)
        motivation_direction_10 = (abs(motivation_direction))/10
        pref_sort = get_preference_sort2(current_response)[0]
        pref_sort_10 = (abs(pref_sort))/10
        openess = get_openess2(current_response)
        openess_10 = (abs(openess))/10


        pref_sort_label = get_preference_sort2(current_response)[1]
        pref_label_array.update({current_response.user_id:pref_sort_label})
        motivation_array = [frame_reference,motivation_direction,pref_sort,openess]
        member_motivation_array.update({current_response.user_id:motivation_array})
        motivation_array_10 = [frame_10,motivation_direction_10,pref_sort_10,openess_10]
        member_motivation_array_10.update({current_response.user_id:motivation_array_10})

    return member_motivation_array,member_motivation_array_10,pref_label_array

#---------------------------------------------------------------#

def get_frame_reference2(current_response):

    answer_question1 = current_response.answers.get(question__quest_numb = 16)
    answer_question2 = current_response.answers.get(question__quest_numb = 4)
    answer_question3 = current_response.answers.get(question__quest_numb = 8)
    answer_question4 = current_response.answers.get(question__quest_numb = 12)

    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    json_answer_question3 = json.loads(answer_question3.body)
    json_answer_question4 = json.loads(answer_question4.body)

    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    answer_key_question3 = list(json_answer_question3.keys())[0][0]
    answer_key_question4 = list(json_answer_question4.keys())[0][0]

    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0] #external
    else:
        score1 = -list(json_answer_question1.values())[0] #internal

    if answer_key_question2 == "2" or "4":
        score2 = list(json_answer_question2.values())[0] #external
    else:
        score2 = -list(json_answer_question2.values())[0] #internal

    if answer_key_question3 == "2":
        score3 = list(json_answer_question3.values())[0] #external
    else:
        score3 = -list(json_answer_question3.values())[0] #internal

    if answer_key_question4 == "1" or "4":
        score4 = list(json_answer_question4.values())[0] #external
    else:
        score4= -list(json_answer_question4.values())[0] #internal

    frame_reference_score = math.ceil((score1+score2+score3+score4)/4)

    return frame_reference_score

def get_motivation_direction2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 15)
    answer_question2 = current_response.answers.get(question__quest_numb = 7)
    answer_question3 = current_response.answers.get(question__quest_numb = 4)

    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    json_answer_question3 = json.loads(answer_question2.body)

    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    answer_key_question3 = list(json_answer_question3.keys())[0][0]

    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0] #toward
    else:
        score1 = -list(json_answer_question1.values())[0] #away from

    if answer_key_question2 == "1" or "2":
        score2 = list(json_answer_question2.values())[0] #toward
    else:
        score2 = -list(json_answer_question2.values())[0] #away from

    if answer_key_question3 == "1" or "2":
        score3 = list(json_answer_question3.values())[0] #toward
    else:
        score3 = -list(json_answer_question3.values())[0] #away from


    motivation_direction_score = math.ceil((score1+score2+score3)/3)

    return motivation_direction_score

def get_preference_sort2(current_response):

    answer_question1 = current_response.answers.get(question__quest_numb = 3)
    answer_question2 = current_response.answers.get(question__quest_numb = 18)

    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)

    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]

    score1 = list(json_answer_question1.values())[0]
    score2 = list(json_answer_question2.values())[0]

    if answer_key_question1 == "1" and answer_key_question2 == "1":
        pref_sort_score = math.ceil((score1+score2)/2) ## case both are people
        pref_label = "People"
    elif answer_key_question1 == "2" and answer_key_question2 == "3":
        pref_sort_score = math.ceil((score1+score2)/2) ## case both are Places
        pref_label = "Place"
    elif answer_key_question1 == "3" and answer_key_question2 == "2":
        pref_sort_score = math.ceil((score1+score2)/2) ## case both are things
        pref_label = "Things"
    elif answer_key_question1 == "4" and answer_key_question2 == "4":
        pref_sort_score = math.ceil((score1+score2)/2) ## case both are Intellect
        pref_label = "Intellect"

    else:
        if score1>score2:
            pref_sort_score = score1 - score2
            if answer_key_question1 == "1":
                pref_label = "People"
            elif answer_key_question1 == "2":
                pref_label = "Place"
            elif answer_key_question1 == "3":
                pref_label = "Things"
            else:
                pref_label = "Intellect"
        else:
            pref_sort_score = score2 - score1
            if answer_key_question1 == "1":
                pref_label = "People"
            elif answer_key_question1 == "3":
                pref_label = "Place"
            elif answer_key_question1 == "2":
                pref_label = "Things"
            else:
                pref_label = "Intellect"

    return pref_sort_score, pref_label

def get_openess2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 7)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]


    if answer_key_question1 == "1" or "3":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    openess_score = math.ceil(score1)

    return openess_score

############ End Motivation ##############

############ Action sort ##############

def get_employee_action_array(self, format=None, *args, **kwargs):
    response_list = get_current_team(self)
    action_array = get_action_array(response_list)

    return action_array


def get_action_array(array):

    current_response_list = array
    member_action_array = {}
    member_action_array_10 = {}
    affil_label_array = {}
    for response_dic in current_response_list:
        current_response = list(response_dic.values())[0]

        active = get_active_reactive2(current_response)
        active_10 = (abs(active))/10
        affiliation = get_affliation_management2(current_response)[0]
        affiliation_10 = (abs(affiliation))/10
        option = get_option_proc2(current_response)
        option_10 = (abs(option))/10
        expect = get_expectation2(current_response)
        expect_10 = (abs(expect))/10
        sensor = get_sensor_intuition2(current_response)
        sensor_10 = (abs(sensor))/10

        affiliation_label = get_affliation_management2(current_response)[1]
        affil_label_array.update({current_response.user_id:affiliation_label})
        action_array = [active,affiliation,option,expect,sensor]
        member_action_array.update({current_response.user_id:action_array})
        action_array_10 = [active_10,affiliation_10,option_10,expect_10,sensor_10]
        member_action_array_10.update({current_response.user_id:action_array_10})

    return member_action_array,member_action_array_10,affil_label_array

#---------------------------------------------------------------#

def get_active_reactive2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 14)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]


    if answer_key_question1 == "1" or "3":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    act_score = math.ceil(score1)

    return act_score

def get_affliation_management2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 10)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]

    if answer_key_question1 == "1":
        affiliation_label = "Independant worker"
    elif answer_key_question1 == "2":
        affiliation_label = "Manager worker"
    else:
        affiliation_label = "Team Player independant"

    act_score = list(json_answer_question1.values())[0]

    return act_score, affiliation_label

def get_option_proc2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 2)
    answer_question2 = current_response.answers.get(question__quest_numb = 14)
    answer_question3 = current_response.answers.get(question__quest_numb = 6)

    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    json_answer_question3 = json.loads(answer_question2.body)

    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    answer_key_question3 = list(json_answer_question3.keys())[0][0]

    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    if answer_key_question2 == "3" or "4":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]

    if answer_key_question3 == "1" or "2":
        score3 = list(json_answer_question3.values())[0]
    else:
        score3 = -list(json_answer_question3.values())[0]


    option_proc = math.ceil((score1+score2+score3)/3)

    return option_proc

def get_expectation2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 9)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]


    expect_score = math.ceil(score1)

    return expect_score

def get_sensor_intuition2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 12)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]

    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    sensor_intuition_score = math.ceil(score1)

    return sensor_intuition_score

############ End Action sort ##############

############ To Define ##############

def get_employee_behav_array(self, format=None, *args, **kwargs):
    response_list = get_current_team(self)
    behav_array = get_behaviour_array(response_list)
    return behav_array


def get_behaviour_array(array):

    current_response_list = array
    member_behaviour_array_10 = {}
    member_behaviour_array = {}
    knowledge_label_array = {}
    for response_dic in current_response_list:
        current_response = list(response_dic.values())[0]

        locus = get_locus_control2(current_response)
        locus_10 = (abs(locus))/10
        temper = get_temper_to_instruction2(current_response)
        temper_10 = (abs(temper))/10
        time = get_time_sorting2(current_response)
        time_10 = (abs(time))/10
        knowledge = get_knowledge_sort2(current_response)[0]
        knowledge_10 = (abs(knowledge))/10

        knowledge_label = get_knowledge_sort2(current_response)[1]
        knowledge_label_array.update({current_response.user_id:knowledge_label})
        behaviour_array = [locus,temper,time,knowledge]
        behaviour_array_10 = [locus_10,temper_10,time_10,knowledge_10]
        member_behaviour_array.update({current_response.user_id:behaviour_array})
        member_behaviour_array_10.update({current_response.user_id:behaviour_array_10})

    return member_behaviour_array,member_behaviour_array_10,knowledge_label_array

#---------------------------------------------------------------#

def get_locus_control2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 20)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    locus_score = math.ceil(score1)

    return locus_score

def get_temper_to_instruction2(current_response):

    answer_question1 = current_response.answers.get(question__quest_numb = 21)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    temper_score = math.ceil(score1)

    return temper_score

def get_time_sorting2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 13)
    answer_question2 = current_response.answers.get(question__quest_numb = 19)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]

    if answer_key_question1 == "2" or answer_key_question2 == "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]


    time_sorting_score = math.ceil(score1)

    return time_sorting_score

def get_knowledge_sort2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb = 11)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]

    if answer_key_question1 == "1":
        knowledge_sort_label = "Modeling"
    elif answer_key_question1 == "2":
        knowledge_sort_label = "Conceptualizing"
    elif answer_key_question1 == "3":
        knowledge_sort_label = "Autorizing"
    else:
        knowledge_sort_label = "Experiencing"

    score1 = list(json_answer_question1.values())[0]
    knowledge_sort_score = math.ceil(score1)


    return knowledge_sort_score,knowledge_sort_label



############ End To Define ##############

class TeamChartData(APIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer, #ProjectSerializer
    permission_classes = []
    http_method_names = ['get',]
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'project_details.html'


    def get_serializer_class(self):
        return self.serializer_class


    def get(self, request, format=None, *args, **kwargs):
        project_id = id=self.kwargs['pk1']

        #test = get_team_response_context(self)
        #test2 = get_applicant_response_context(44)

        chunk_team = get_team_info_score(self)
        motiv_team = get_team_motivation_score(self)
        action_team = get_team_action_score(self)
        behav_team = get_behaviour_action_score(self)
        team_complete = get_team_complete_data(self)
        cohesiveness_score = get_team_cohesivenss_score(self)
        info_dist = get_question_similarities(self)[0]
        motiv_dist = get_question_similarities(self)[1]
        action_dist = get_question_similarities(self)[2]
        behav_dist = get_question_similarities(self)[3]
        #dist_multiple_variable = get_dist_multiple_variable(self)

        processing_information_label = [
                                       ["General","Details"],
                                       ["Sameness","Difference"],
                                       ["Visual","Auditory"],
                                       ["Static","Process"],
                                       ["Best Scenario","Worst Scenario"],
                                       ["Binary","Shades"],
                                       ]
        motivation_label =[
                          ["External","Internal"],
                          ["Go Away","Toward"],
                          [[motiv_team[1]['label']]],
                          ["Variety","Routine"],
                          ]
        action_label = [
                       ["Active","Reaction"],
                       [[action_team[1]['label']]],
                       ["Option","Procedure"],
                       ["Perfection","Optimizing"],
                       ["Sensor","Intuition"]
                       ]
        other_data_label = [
                           ["External locus","Internal locus"],
                           ["Strong Will","Compliant"],
                           ["In time","Through time"],
                           [[behav_team[1]['label']]],
                           ]
        complete_label = [
                         ["General","Details"],
                         ["Sameness","Difference"],
                         ["Visual","Auditory"],
                         ["Static","Process"],
                         ["Best Scenario","Worst Scenario"],
                         ["Binary","Shades"],
                         ["External","Internal"],
                         ["Go Away","Toward"],
                         [[motiv_team[1]['label']]],
                         ["Variety","Routine"],
                         ["Active","Reaction"],
                         [[action_team[1]['label']]],
                         ["Option","Procedure"],
                         ["Perfection","Optimizing"],
                         ["Sensor","Intuition"],
                         ["External locus","Internal locus"],
                         ["Strong Will","Compliant"],
                         ["In time","Through time"],
                         [[behav_team[1]['label']]]
                         ]

        data = {
            "team_info_score":chunk_team,
            "team_motiv_score":motiv_team,
            "team_action_score":action_team,
            "team_behaviour_score":behav_team,
            "team_complete":team_complete,
            "cohesiveness_score":cohesiveness_score[0],
            "users":cohesiveness_score[1],
            "user_dist":cohesiveness_score[2],
            "info_dist":info_dist,
            "motiv_dist": motiv_dist,
            "action_dist":action_dist,
            "behav_dist":behav_dist,
            "complete_label":complete_label,

            "info_label":processing_information_label,
            "motivation_label": motivation_label,
            "action_label":action_label,
            "behav_label":other_data_label,

            #"test":test,
            #"test2":test2,

        }
        return Response(data)

### TEAM CALCULATION ###

def get_team_complete_data(self, format=None, *args, **kwargs):
    total_array = [get_team_info_score(self),get_team_motivation_score(self)[0],get_team_action_score(self)[0],get_behaviour_action_score(self)[0]]
    complete_array = []
    for i in total_array:
        complete_array  = complete_array + i

    return complete_array

def get_weighted_average_array(team_values):
    team_values_list = team_values ## get the array to average
    np_team_values_list = np.array(team_values_list) # transform it to a numpay array
    numb = (list(range(len(np_team_values_list[0])))) # get list of items in previous array to be used as index

    team_score = []
    for n in numb:
        col = np_team_values_list[:,n]
        trend_a = np.sum(col>0)
        trend_b = np.sum(col<0)
        sum_value = 0
        for i in col:
            if i>0:
                val = i*trend_a
                sum_value = sum_value + val
            else:
                val = i*trend_b
                sum_value = sum_value + val
        means_value = round((sum_value)/((trend_a ** 2)+(trend_b ** 2)))
        team_score.append(means_value)
    return(team_score)

def get_team_info_score(self, format=None, *args, **kwargs):

    team_info_tupple =  get_employee_info_array(self) # --> get tupple
    team_info_array = team_info_tupple[0] # extract the dict needed
    team_info_values = team_info_array.values()
    team_values = list(team_info_values)
    info_scores = get_weighted_average_array(team_values)
    return info_scores

def euclidean_distance(x,y):
    return sqrt(sum(pow(a-b,2) for a, b in zip(x, y)))


def get_team_motivation_score(self, format=None, *args, **kwargs):
    team_motivation_tupple =  get_employee_motivation_array(self) ## extract {user id : [values]} + {user id : [values/100]} + {user id : label} for each user
    team_motivation_array = team_motivation_tupple[0]  ## extract {user id : [values]}
    team_motivation_values = team_motivation_array.values() ## extract dict values
    team_values = list(team_motivation_values) ## transform dict values to a list
    motiv_scores = get_weighted_average_array(team_values) ## call the weighted average method and return average

    interest = get_trend(team_motivation_tupple,2) #extract value for the interest question
    motiv_scores[2] = list(interest.values())[0]
    team_motive_labels = {"label":list(interest.keys())[0]}
    return motiv_scores,team_motive_labels

def get_team_action_score(self, format=None, *args, **kwargs):

    team_action_tupple =  get_employee_action_array(self)
    team_action_array = team_action_tupple[0]
    team_action_values = team_action_array.values()
    team_values = list(team_action_values)

    action_scores = get_weighted_average_array(team_values)
    analyzed_array = get_employee_action_array(self)

    action = get_trend(analyzed_array,1)
    action_scores[1] = list(action.values())[0]
    team_action_labels = {"label":list(action.keys())[0]}

    return action_scores, team_action_labels

def get_behaviour_action_score(self, format=None, *args, **kwargs):

    team_behaviour_tupple =  get_employee_behav_array(self)
    team_behaviour_array = team_behaviour_tupple[0]
    team_behaviour_values = team_behaviour_array.values()
    team_values = list(team_behaviour_values)
    behav_scores = get_weighted_average_array(team_values)
    analyzed_array = get_employee_behav_array(self)
    behav = get_trend(analyzed_array,3)
    behav_scores[3] = list(behav.values())[0]

    team_behaviour_labels = {"label":list(behav.keys())[0]}

    return behav_scores,team_behaviour_labels

def get_trend(analyzed_array, index):
    analyzed_array2 = analyzed_array[0] ## extract values 100%
    num = len(analyzed_array2)
    analyzed_array_labels =  analyzed_array[2] ## extract the dict {user_id:label}
    max_label_occ = Counter(analyzed_array_labels.values()).most_common() # count the number of occurence of each label
    max_label_occ_dict = dict(max_label_occ) #transform in a dict

    check = {}
    for t in max_label_occ:
        lab = t[0]
        pond = t[1]
        list_go = 0
        for f in analyzed_array_labels:
            if analyzed_array_labels[f] == lab:
                value = analyzed_array2[f][index]
                list_go = list_go + value
                list_go2 = round((list_go/(num*100))*100)
                check.update({analyzed_array_labels[f]:list_go2}) #return dict {label:Total value} for each label
    max_value = max(list(check.values()))
    tendence_label = []
    for x, y in check.items():
        if y == max_value:
            tendence = x
            tendence_label.append(tendence)

    max_label = random.choice(tendence_label)
    trend_array = {max_label:max_value}

    return trend_array




def get_team_cohesivenss_score(self, format=None, *args, **kwargs):
    team_info_tupple =  get_employee_info_array(self)[0]
    team_motivation_tupple =  get_employee_motivation_array(self)[0]
    team_action_tupple =  get_employee_action_array(self)[0]
    team_behaviour_tupple =  get_employee_behav_array(self)[0]
    array_dict ={}
    for a in team_info_tupple:
        w = team_info_tupple[a]
        x = team_motivation_tupple[a]
        y = team_action_tupple[a]
        z = team_behaviour_tupple[a]
        test = w + x + y + z
        array_dict.update({a:test})

    score = get_team_cohesivenss_score2(array_dict)
    return score

def get_team_cohesivenss_score2(array_dict):
    #import pdb; pdb.set_trace()

    list_keys = list(array_dict.keys())
    list_combi = list(it.combinations(list_keys, 2))

    final_dic = []
    for i in list_combi:
        temp_dict = {}
        for j in i:
            temp_dict.update({j:array_dict[j]})
        final_dic.append(temp_dict)
    dist_list = []
    max_dist = math.sqrt(19*(200**2))
    similarity_dict = {}
    users=[]
    for val in final_dic:
        x = list(val.values())
        x_keys = list(val.keys())
        x_keys_str = str(x_keys[0]) + "-" + str(x_keys[1])

        distance = (euclidean_distance(x[0],x[1]))
        dist_score= round((1-(distance/max_dist))*100)
        dist_list.append(dist_score)
        user_1 = MyUser.objects.get(id = x_keys[0]).first_name + " " + MyUser.objects.get(id = x_keys[0]).last_name
        user_2 = MyUser.objects.get(id = x_keys[1]).first_name + " " + MyUser.objects.get(id = x_keys[1]).last_name
        user_pair = user_1 + ' - ' +  user_2
        users.append(user_pair)
        similarity_dict.update({user_pair:dist_score})

    team_score = round(np.mean(dist_list))
    return team_score,users,dist_list

def get_question_similarities(self, format=None, *args, **kwargs):
    team_info_tupple =  get_employee_info_array(self)[0]
    team_motivation_tupple =  get_employee_motivation_array(self)[0]
    team_action_tupple =  get_employee_action_array(self)[0]
    team_behaviour_tupple =  get_employee_behav_array(self)[0]
    dict_user_answers ={}
    for a in team_info_tupple:
        w = team_info_tupple[a]
        x = team_motivation_tupple[a]
        y = team_action_tupple[a]
        z = team_behaviour_tupple[a]
        merged_array = w + x + y + z
        dict_user_answers.update({a:merged_array})


    numb_answers = len(list(dict_user_answers.values())[0])
    list_answers_values =list(dict_user_answers.values())

    answer_per_question = []
    for number in range(0,numb_answers):
        temp_array=[]
        for val in list_answers_values:
            answer_value = val[number]
            temp_array.append(answer_value)
        answer_per_question.append(temp_array)
    question_similarities = euclid_array(answer_per_question)
    motiv_trend = get_dist_multiple_variable(get_employee_motivation_array(self),2)
    question_similarities[8] = motiv_trend
    action_trend = get_dist_multiple_variable(get_employee_action_array(self),1)
    question_similarities[11] = action_trend
    behav_trend = get_dist_multiple_variable(get_employee_behav_array(self),3)
    question_similarities[11] = behav_trend


    info_index = len((list(team_info_tupple.values())[0]))
    info_similarities = question_similarities[0:info_index]
    motiv_index = info_index + len((list(team_motivation_tupple.values())[0]))
    motiv_similarities = question_similarities[(info_index):motiv_index]
    action_index = motiv_index + len((list(team_action_tupple.values())[0]))
    action_similarities = question_similarities[motiv_index:action_index]
    behav_index = action_index + len((list(team_behaviour_tupple.values())[0]))
    behav_similarities = question_similarities[action_index:behav_index]
    return info_similarities,motiv_similarities,action_similarities,behav_similarities



def euclid_array(answer_per_question):
    go = []
    max_dist = round(math.sqrt(len(answer_per_question[0]*(200**2))))
    for i in answer_per_question:
        combi = list(it.combinations(i, 2))

        sum_diff = 0
        for lst in combi:
            diff = (lst[0] - lst[1])**2
            sum_diff = sum_diff + diff
        sqrd_val= math.sqrt(sum_diff)
        final_val = round((1-(sqrd_val/max_dist))*100)
        go.append(final_val)
    return go

def get_dist_multiple_variable(array,index):
    labels_dict = array[2]
    labels_user_id = list(labels_dict.keys())
    labels_values = list(labels_dict.values())
    list_combi_user_id = list(it.combinations(labels_dict, 2))
    max_dist = round(math.sqrt(len(array)*(200**2)))
    list_dis = []
    for combi in list_combi_user_id:
        dict_lab ={}
        for id_val in combi:
            lab = labels_dict[id_val]
            dict_lab.update({id_val:lab})
        if dict_lab[combi[0]] == dict_lab[combi[1]]:
            x1 = array[0][combi[0]][index] ##change Index
            x2 = array[0][combi[1]][index] ##change Index
        else:
            x1 = array[0][combi[0]][2] ##change Index
            x2 = -array[0][combi[1]][2]
        dist_x = (x1-x2) ** 2
        list_dis.append(dist_x)
    euc_dist = sqrt(np.sum(list_dis))
    trend_similarity = round((1-(euc_dist/max_dist))*100)
    return trend_similarity



## Recruitment Page ##

class RecruitmentPage(generic.ListView):
    #import pdb; pdb.set_trace()
    model = Project
    template_name = "recruitment_index.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Project, id=self.kwargs['pk1'])

    def get_context_data(self, **kwargs):

        #import pdb; pdb.set_trace()
        context = super(RecruitmentPage, self).get_context_data(**kwargs)

        current_project_id = self.kwargs['pk1']
        applicant_list = Project.objects.get(id = current_project_id).applicant.all()
        team_score = get_team_cohesivenss_score(self)[0]

        app_with_resp = []
        app_without_resp = []
        for i in applicant_list:
            if len(i.response_set.all())>0:
                app_with_resp.append(i)
            else:
                app_without_resp.append(i)

        appli_score_list = {}
        for i in app_with_resp:
            list1 = get_applicant_response_context(i.id)
            list2 = get_team_response_context(self)
            list2.update(list1)
            score = get_team_cohesivenss_score2(list2)[0]
            resp_date = list(i.response_set.all())[0].created
            score_with_id = {i:[score,score-team_score,resp_date]}
            appli_score_list.update(score_with_id)


        context['current_project_id'] = current_project_id
        context['applicant_list'] = applicant_list
        context['app_with_resp'] = app_with_resp
        context['app_without_resp'] = app_without_resp
        context['appli_score_list'] = appli_score_list
        context['team_score'] = team_score

        return context

class applicantChartData(APIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer, #ProjectSerializer
    permission_classes = []
    http_method_names = ['get',]
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'project_details.html'


    def get_serializer_class(self):
        return self.serializer_class


    def get(self, request, format=None, *args, **kwargs):
        applicant_info_array = get_applicant_info_array(self)
        applicant_motivation_array = get_applicant_motivation_array(self)
        applicant_action_array = get_applicant_action_array(self)
        applicant_behav_array = get_applicant_behav_array(self)

        score = get_team_cohesivenss_score(self)
        applicant_cohesivenss_score = get_applicant_cohesivenss_score(self)
        applicant_complete_data = get_applicant_complete_data(self)
        current_user = get_current_user(self)

        processing_information_label = [
                                       ["General","Details"],
                                       ["Sameness","Difference"],
                                       ["Visual","Auditory"],
                                       ["Static","Process"],
                                       ["Best Scenario","Worst Scenario"],
                                       ["Binary","Shades"],
                                       ]
        motivation_label =[
                          ["External","Internal"],
                          ["Go Away","Toward"],
                          ["[motiv_team[1]['label']]"],
                          ["Variety","Routine"],
                          ]
        action_label = [
                       ["Active","Reaction"],
                       ["[action_team[1]['label']]"],
                       ["Option","Procedure"],
                       ["Perfection","Optimizing"],
                       ["Sensor","Intuition"]
                       ]
        other_data_label = [
                           ["External locus","Internal locus"],
                           ["Strong Will","Compliant"],
                           ["In time","Through time"],
                           ["[behav_team[1]['label']]"],
                           ]
        complete_label = [
                         ["General","Details"],
                         ["Sameness","Difference"],
                         ["Visual","Auditory"],
                         ["Static","Process"],
                         ["Best Scenario","Worst Scenario"],
                         ["Binary","Shades"],
                         ["External","Internal"],
                         ["Go Away","Toward"],
                         ["[motiv_team[1]['label']]"],
                         ["Variety","Routine"],
                         ["Active","Reaction"],
                         ["[action_team[1]['label']]"],
                         ["Option","Procedure"],
                         ["Perfection","Optimizing"],
                         ["Sensor","Intuition"],
                         ["External locus","Internal locus"],
                         ["Strong Will","Compliant"],
                         ["In time","Through time"],
                         ["[behav_team[1]['label']]"]
                         ]

        data = {
                ### data ###
                'applicant_info_array':applicant_info_array,
                'applicant_motivation_array':applicant_motivation_array,
                'applicant_action_array':applicant_action_array,
                'applicant_behav_array':applicant_behav_array,

                ## Label ##
                'complete_label':complete_label,
                'applicant_sim_label': applicant_cohesivenss_score[1],
                'applicant_sim_score' : applicant_cohesivenss_score[2],

                'applicant_complete_data':applicant_complete_data,
                'current_user':current_user,
                'processing_information_label':processing_information_label,
                'motivation_label':motivation_label,
                'action_label':action_label,
                'other_data_label':other_data_label,


        }
        return Response(data)


def get_applicant_team_list(self, format=None, *args, **kwargs):
    current_team_member = list(Project.objects.get(id = self.kwargs['pk1']).team_id.members.all())
    current_applicant = MyUser.objects.get(id =self.kwargs['pk2'])
    current_team_member.append(current_applicant)
    applicant_response_list = []
    for member in current_team_member:
        applicant_id = member.id
        applicant_response = get_user_response(applicant_id)
        applicant_response_list.append({applicant_id:applicant_response})
    return applicant_response_list

def get_applicant_info_array(self, format=None, *args, **kwargs):
    response_list = get_applicant_team_list(self)
    info_array = get_info_array(response_list)
    return info_array

def get_applicant_motivation_array(self, format=None, *args, **kwargs):
    response_list = get_applicant_team_list(self)
    motiv_array = get_motivation_array(response_list)
    return motiv_array

def get_applicant_action_array(self, format=None, *args, **kwargs):
    response_list = get_applicant_team_list(self)
    action_array = get_action_array(response_list)
    return action_array

def get_applicant_behav_array(self, format=None, *args, **kwargs):
    response_list = get_applicant_team_list(self)
    behav_array = get_behaviour_array(response_list)
    return behav_array


def get_applicant_cohesivenss_score(self, format=None, *args, **kwargs):
    team_info_tupple =  get_applicant_info_array(self)[0]
    team_motivation_tupple =  get_applicant_motivation_array(self)[0]
    team_action_tupple =  get_applicant_action_array(self)[0]
    team_behaviour_tupple =  get_applicant_behav_array(self)[0]
    array_dict ={}
    for a in team_info_tupple:
        w = team_info_tupple[a]
        x = team_motivation_tupple[a]
        y = team_action_tupple[a]
        z = team_behaviour_tupple[a]
        test = w + x + y + z
        array_dict.update({a:test})

    score = get_team_cohesivenss_score2(array_dict)

    applicant  = MyUser.objects.get(id = self.kwargs['pk2'])
    applicant_name = applicant.first_name + " "+applicant.last_name
    applicant_index = []
    for i in score[1]:
        if applicant_name in i:
            applicant_index.append(score[1].index(i))
    applicant_diff_labels = []
    applicant_diff_score = []
    for i in applicant_index:
        applicant_diff_labels.append(score[1][i])
        applicant_diff_score.append(score[2][i])
    return score, applicant_diff_labels, applicant_diff_score

def get_applicant_complete_data(self, format=None, *args, **kwargs):
    app_info = get_applicant_info_array(self)[0][int(self.kwargs['pk2'])]
    app_motiv = get_applicant_motivation_array(self)[0][int(self.kwargs['pk2'])]
    app_act = get_applicant_action_array(self)[0][int(self.kwargs['pk2'])]
    app_behav = get_applicant_behav_array(self)[0][int(self.kwargs['pk2'])]

    complete_app_array = app_info + app_motiv + app_act + app_behav
    return complete_app_array

def get_team_response_context(self, format=None, *args, **kwargs):
    team_info_tupple =  get_employee_info_array(self)[0]
    team_motivation_tupple =  get_employee_motivation_array(self)[0]
    team_action_tupple =  get_employee_action_array(self)[0]
    team_behaviour_tupple =  get_employee_behav_array(self)[0]
    array_dict ={}
    for a in team_info_tupple:
        w = team_info_tupple[a]
        x = team_motivation_tupple[a]
        y = team_action_tupple[a]
        z = team_behaviour_tupple[a]
        test = w + x + y + z
        array_dict.update({a:test})
    return(array_dict)

def get_applicant_response_context(app_id):
    applicant_response = get_user_response(app_id)
    applicant_response_dict = [{app_id:applicant_response}]
    info_array = get_info_array(applicant_response_dict)[0]
    motiv_array = get_motivation_array(applicant_response_dict)[0]
    action_array = get_action_array(applicant_response_dict)[0]
    behav_array = get_behaviour_array(applicant_response_dict)[0]
    array_dict ={}
    for a in info_array:
        w = info_array[a]
        x = motiv_array[a]
        y = action_array[a]
        z = behav_array[a]
        test = w + x + y + z
        array_dict.update({a:test})
    return(array_dict)
