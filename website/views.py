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

    def get_object(self, queryset=None):
        return get_object_or_404(Project,id=self.kwargs['pk1'])

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        try:
            team_name = Project.objects.get(id=self.kwargs['pk1']).team_id.members.all()
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

        info_array = get_info_array(self)[1]
        motivation_array = get_motivation_array(self)[1]
        action_array = get_action_array(self)[1]
        behaviour_array = get_behaviour_array(self)[1]
        complete = get_complete_data(self)
        current_user = get_current_user(self)
        current_team_member_id = get_current_team_member_id(self)

        label_pref = get_motivation_array(self)[2][int(self.kwargs['pk2'])]
        affiliation_label = get_action_array(self)[2][int(self.kwargs['pk2'])]
        knowledge_label = get_behaviour_array(self)[2][int(self.kwargs['pk2'])]




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
            "info_array":info_array,
            "motivation_array":motivation_array,
            "action_array": action_array,
            "behaviour_array":behaviour_array,

            #labels
            "complete_label":complete_label,
            "processing_information_label":processing_information_label,
            "motivation_label":motivation_label,
            "action_label":action_label,
            "other_data_label": other_data_label,

            #other
            "current_user":current_user,
            "current_team_member_id":current_team_member_id

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
    survey_team = Survey.objects.get(name= 'Survey SoftScore') #survey team (to change to final one)
    current_response = ResponseModel.objects.filter(user = current_user, survey = survey_team)[0]

    return current_response

def get_current_response(self, format=None, *args, **kwargs):
    current_user = MyUser.objects.get(id = self.kwargs['pk2']) #current_user
    survey_team = Survey.objects.get(name= 'Survey SoftScore') #survey team (to change to final one)
    current_response = ResponseModel.objects.filter(user = current_user, survey = survey_team)[0]

    return current_response


############ Complete Data ##############
def get_complete_data(self, format=None, *args, **kwargs):
    #current_response = get_current_response(self)
    #print(current_response)
    total_array = [get_info_array(self)[0],get_motivation_array(self)[0],get_action_array(self)[0],get_behaviour_array(self)[0]]
    test = get_motivation_array(self)[2]
    complete_array = []
    for i in total_array:
        f = i[int(self.kwargs['pk2'])]
        complete_array = complete_array + f
    #print(complete_array)
    #print(total_array)
    #print(total_array)

    return complete_array

############ Processing Informations ##############


def get_info_array(self, format=None, *args, **kwargs):

    current_response_list = get_current_team(self)
    #print(current_response_list)
    member_info_array_10 = {}
    member_info_array = {}
    for response_dic in current_response_list:
        current_response = list(response_dic.values())[0]
        #print(dir(current_response))
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
    #print(member_info_array)
    #print(member_info_array_10)
    return member_info_array, member_info_array_10

#------------------------------------------------------#

def get_chunk_score3(current_response):
    answer_question1 = current_response.answers.get(question_id = 2)
    answer_question2 = current_response.answers.get(question_id = 3)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "3":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    if answer_key_question2 == "1" or "3":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]

    chunk_score = math.ceil((score1+score2)/2)
            # chunk_list.append({current_response.user_id:chunk_score})
    #print("chunk:{0}".format(chunk_score))
            # if chunk_score > 0:
            #     print("Chunk - General, Score: {0}" .format(chunk_score))
            # else:
            #     print("Chunk - Details, Score: {0}" .format(chunk_score))
    return chunk_score

def get_info_relationship3(current_response):

    answer_question1 = current_response.answers.get(question_id = 6)
    answer_question2 = current_response.answers.get(question_id = 17)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]


    if answer_key_question2 == "1" or "2":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]

    info_relationship_score = math.ceil((score1+score2)/2)

    # print("info : {0}".format(info_relationship_score))
    # if info_relationship_score > 0:
    #     print("Info RelationShip - Sameness, Score: {0}".format(info_relationship_score))
    # else:
    #     print("Info RelationShip - Difference, Score: {0}".format(info_relationship_score))
    return info_relationship_score

def get_rep_system3(current_response):
    answer_question1 = current_response.answers.get(question_id = 2)
    answer_question2 = current_response.answers.get(question_id = 16)
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

    rep_system_score = math.ceil((score1+score2)/2)
    # if rep_system_score > 0:
    #     print("Rep.System - Visual, Score: {0}".format(rep_system_score))
    # else:
    #     print("Rep.System - Auditory, Score: {0}".format(rep_system_score))
    return rep_system_score

def get_reality_structure3(current_response):
    answer_question1 = current_response.answers.get(question_id = 2)
    answer_question2 = current_response.answers.get(question_id = 16)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]
        #print(score1)

    if answer_key_question2 == "2" or "3":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]
    info_relationship_score = math.ceil((score1+score2)/2)
    # if info_relationship_score > 0:
    #     print("Reality Structure: {0}".format(info_relationship_score))
    # else:
    #     print("Reality Structure: {0}".format(info_relationship_score))
    return info_relationship_score

def get_scenario_thinking3(current_response):
    answer_question1 = current_response.answers.get(question_id = 7)
    #answer_question2 = current_response.answers.get(question_id = 16)
    json_answer_question1 = json.loads(answer_question1.body)
    #json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    #answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "2" or "4":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]


    # if answer_key_question2 == "2" or "3":
    #     score2 = list(json_answer_question2.values())[0]
    # else:
    #     score2 = -list(json_answer_question2.values())[0]

    scenario_thinking_score = math.ceil((score1))
    # if scenario_thinking_score > 0:
    #     print("Scenario Thinking - Best Scenario, Score: {0}".format(scenario_thinking_score))
    # else:
    #     print("Scenario Thinking - Worst Scenario, Score: {0}".format(scenario_thinking_score))
    return scenario_thinking_score

def get_perceptual_category3(current_response):
    answer_question1 = current_response.answers.get(question_id = 6)
    #answer_question2 = current_response.answers.get(question_id = 16)
    json_answer_question1 = json.loads(answer_question1.body)
    #json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    #answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]


    # if answer_key_question2 == "2" or "3":
    #     score2 = list(json_answer_question2.values())[0]
    # else:
    #     score2 = -list(json_answer_question2.values())[0]

    perceptual_category_score = math.ceil(score1)
    # if perceptual_category_score > 0:
    #     print("Perceptual Category Binary, Score: {0}".format(perceptual_category_score))
    # else:
    #     print("Perceptual Category Shades, Score: {0}".format(perceptual_category_score))
    return perceptual_category_score


############ End Processing Informations ##############

############ Motivation ##############

def get_motivation_array(self, format=None, *args, **kwargs):

    current_response_list = get_current_team(self)

    #print(current_response_list)
    member_motivation_array = {}
    member_motivation_array_10 = {}
    pref_label_array = {}
    for response_dic in current_response_list:
        current_response = list(response_dic.values())[0]
        #print(current_response)
        frame_reference = get_frame_reference2(current_response)
        frame_10 = (abs(frame_reference))/10
        motivation_direction = get_motivation_direction2(current_response)
        motivation_direction_10 = (abs(motivation_direction))/10
        pref_sort = get_preference_sort2(current_response)[0]
        pref_sort_10 = (abs(pref_sort))/10
        openess = get_openess2(current_response)
        openess_10 = (abs(openess))/10


        #print(pref_sort_label)

        pref_sort_label = get_preference_sort2(current_response)[1]
        pref_label_array.update({current_response.user_id:pref_sort_label})
        motivation_array = [frame_reference,motivation_direction,pref_sort,openess]
        member_motivation_array.update({current_response.user_id:motivation_array})
        motivation_array_10 = [frame_10,motivation_direction_10,pref_sort_10,openess_10]
        member_motivation_array_10.update({current_response.user_id:motivation_array_10})
    #print(pref_label_array)
    return member_motivation_array,member_motivation_array_10,pref_label_array

#---------------------------------------------------------------#

def get_frame_reference2(current_response):

    answer_question1 = current_response.answers.get(question_id = 16)
    answer_question2 = current_response.answers.get(question_id = 5)
    answer_question3 = current_response.answers.get(question_id = 9)
    answer_question4 = current_response.answers.get(question_id = 13)

    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    json_answer_question3 = json.loads(answer_question3.body)
    json_answer_question4 = json.loads(answer_question4.body)

    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    answer_key_question3 = list(json_answer_question3.keys())[0][0]
    answer_key_question4 = list(json_answer_question4.keys())[0][0]

    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    if answer_key_question2 == "2" or "4":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]

    if answer_key_question3 == "2":
        score3 = list(json_answer_question3.values())[0]
    else:
        score3 = -list(json_answer_question3.values())[0]

    if answer_key_question4 == "1" or "4":
        score4 = list(json_answer_question4.values())[0]
    else:
        score4= -list(json_answer_question4.values())[0]

    frame_reference_score = math.ceil((score1+score2+score3+score4)/4)
    # if frame_reference_score > 0:
    #     print("Frame reference - External, Score: {0}".format(frame_reference_score))
    # else:
    #     print("Frame reference - Internal, Score: {0}".format(frame_reference_score))
    return frame_reference_score

def get_motivation_direction2(current_response):
    answer_question1 = current_response.answers.get(question_id = 15)
    answer_question2 = current_response.answers.get(question_id = 8)
    answer_question3 = current_response.answers.get(question_id = 16)

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

    if answer_key_question3 == "1":
        score3 = list(json_answer_question3.values())[0]
    else:
        score3 = -list(json_answer_question3.values())[0]


    motivation_direction_score = math.ceil((score1+score2+score3)/3)
    # if motivation_direction_score > 0:
    #     print("Motivation Direction - Go Away, Score: {0}".format(motivation_direction_score))
    # else:
    #     print("Motivation Direction - Toward, Score: {0}".format(motivation_direction_score))
    return motivation_direction_score

def get_preference_sort2(current_response):

    answer_question1 = current_response.answers.get(question_id = 4)
    answer_question2 = current_response.answers.get(question_id = 18)

    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)

    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]

    if answer_key_question1 or answer_key_question2 == "1":
        pref_label = "People"
    elif answer_key_question1 == "2" or answer_key_question2 == "3":
        pref_label = "Place"
    elif answer_key_question1 == "3" or answer_key_question2 == "2":
        pref_label = "Things"
    else:
        pref_label = "Intellect"


    score1 = list(json_answer_question1.values())[0]
    score2 = list(json_answer_question2.values())[0]

    if answer_key_question1 == "1" and answer_key_question2 == "1":
        pref_sort_score = math.ceil((score1+score2)/2)
        # print("Pref Score - People, score: {0}".format(pref_sort_score))
    elif answer_key_question1 == "2" and answer_key_question2 == "3":
        pref_sort_score = math.ceil((score1+score2)/2)
        # print("Pref Score - Place, score: {0}".format(pref_sort_score))
    elif answer_key_question1 == "3" and answer_key_question2 == "2":
        pref_sort_score = math.ceil((score1+score2)/2)
        # print("Pref Score - Things, score: {0}".format(pref_sort_score))
    elif answer_key_question1 == "4" and answer_key_question2 == "4":
        pref_sort_score = math.ceil((score1+score2)/2)
        # print("Pref Score - Intellect, score: {0}".format(pref_sort_score))

    else:
        if score1>score2:
            pref_sort_score = score1
            # print("Pref Score Diff - {0}, score:{1}".format(pref_label,pref_sort_score))
        else:
            pref_sort_score = score2
            # print("Pref Score Diff - {0}, score: {1}".format(pref_label, pref_sort_score))
    return pref_sort_score, pref_label

def get_openess2(current_response):
    answer_question1 = current_response.answers.get(question_id = 8)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]


    if answer_key_question1 == "1" or "3":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    openess_score = math.ceil(score1)
    # if openess_score > 0:
    #     print("Openess - Open, Score: {0}".format(openess_score))
    # else:
    #     print("Openess - Routine, Score: {0}".format(openess_score))
    return openess_score

############ End Motivation ##############

############ Action sort ##############

def get_action_array(self, format=None, *args, **kwargs):

    current_response_list = get_current_team(self)
    #print(current_response_list)
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
    #print(affil_label_array)
    return member_action_array,member_action_array_10,affil_label_array

#---------------------------------------------------------------#

def get_active_reactive2(current_response):
    answer_question1 = current_response.answers.get(question_id = 15)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]


    if answer_key_question1 == "1" or "3":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    act_score = math.ceil(score1)
    # if act_score > 0:
    #     print("Active/Reactive - Active, Score: {0}".format(act_score))
    # else:
    #     print("Active/Reactive - Reactive, Score: {0}".format(act_score))
    return act_score

def get_affliation_management2(current_response):
    answer_question1 = current_response.answers.get(question_id = 11)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]

    if answer_key_question1 == "1":
        affiliation_label = "Independant worker"
    elif answer_key_question1 == "2":
        affiliation_label = "Manager worker"
    else:
        affiliation_label = "Team Player independant"

    act_score = list(json_answer_question1.values())[0]
    # print("Affilation Management - {0}, Score: {1}".format(affiliation_label,act_score))
    return act_score, affiliation_label

def get_option_proc2(current_response):
    answer_question1 = current_response.answers.get(question_id = 3)
    answer_question2 = current_response.answers.get(question_id = 15)
    answer_question3 = current_response.answers.get(question_id = 7)

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
    # if option_proc > 0:
    #     print("Option/Procedure - Options, Score:{0}".format(option_proc))
    # else:
    #     print("Option/Procedure - Procedure, Score: {0}".format(option_proc))
    return option_proc

def get_expectation2(current_response):
    answer_question1 = current_response.answers.get(question_id = 2)
    answer_question2 = current_response.answers.get(question_id = 16)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]
        #print(score1)

    if answer_key_question2 == "2" or "3":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]

    expect_score = math.ceil((score1+score2)/2)
    # if info_relationship_score > 0:
    #     print("Perfection: {0}".format(info_relationship_score))
    # else:
    #     print("Optimizing:{0}".format(info_relationship_score))
    return expect_score

def get_sensor_intuition2(current_response):
    answer_question1 = current_response.answers.get(question_id = 13)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]

    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    sensor_intuition_score = math.ceil(score1)
    # if sensor_intuition_score > 0:
    #     print("Sensor/Intuition - Sensor, Score:{0}".format(sensor_intuition_score))
    # else:
    #     print("Sensor/Intuition - Intuition, Score: {0}".format(sensor_intuition_score))
    return sensor_intuition_score

############ End Action sort ##############

############ To Define ##############

def get_behaviour_array(self, format=None, *args, **kwargs):

    current_response_list = get_current_team(self)
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
    #print(knowledge_label_array)
    return member_behaviour_array,member_behaviour_array_10,knowledge_label_array

#---------------------------------------------------------------#

def get_locus_control2(current_response):
    answer_question1 = current_response.answers.get(question_id = 2)
    answer_question2 = current_response.answers.get(question_id = 16)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]
        #print(score1)

    if answer_key_question2 == "2" or "3":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]

    locus_score = math.ceil((score1+score2)/2)
    # if info_relationship_score > 0:
    #     print("Locus of Control - Internal: {0}" .format(info_relationship_score))
    # else:
    #     print("Locus of Control - Internal: {0}" .format(info_relationship_score))
    return locus_score

def get_temper_to_instruction2(current_response):

    answer_question1 = current_response.answers.get(question_id = 2)
    answer_question2 = current_response.answers.get(question_id = 16)
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

    temper_score = math.ceil((score1+score2)/2)
    # if info_relationship_score > 0:
    #     print("Temper to instruction - StrongWill: {0}".format(info_relationship_score))
    # else:
    #     print("Temper to instruction - Compliant: {0}".format(info_relationship_score))
    return temper_score

def get_time_sorting2(current_response):
    answer_question1 = current_response.answers.get(question_id = 14)
    answer_question2 = current_response.answers.get(question_id = 19)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]

    if answer_key_question1 == "2" or answer_key_question2 == "2":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]


    time_sorting_score = math.ceil(score1)
    # if time_sorting_score > 0:
    #     print("Time Sorting - In Time: %s" % time_sorting_score)
    # else:
    #     print("Time Sorting - Through Time: %s" % time_sorting_score)
    return time_sorting_score

def get_knowledge_sort2(current_response):
    answer_question1 = current_response.answers.get(question_id = 12)
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

    # print("Knowledge Sort - {0}, Score: {1}".format(knowledge_sort_label,knowledge_sort_score))
    return knowledge_sort_score,knowledge_sort_label



############ End To Define ##############

class TeamChartData(APIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer, #ProjectSerializer
    permission_classes = []
    http_method_names = ['get',]


    def get_serializer_class(self):
        return self.serializer_class


    def get(self, request, format=None, *args, **kwargs):
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

        }
        return Response(data)

### TEAM CALCULATION ###

def get_team_complete_data(self, format=None, *args, **kwargs):
    total_array = [get_team_info_score(self),get_team_motivation_score(self)[0],get_team_action_score(self)[0],get_behaviour_action_score(self)[0]]
    complete_array = []
    for i in total_array:
        complete_array  = complete_array + i
    #print(complete_array)
    return complete_array

def get_weighted_average_array(team_values):
    team_values_list = list(team_values)
    np_team_values_list = np.array(team_values_list)
    numb = (list(range(len(np_team_values_list[0]))))
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

    team_info_tupple =  get_info_array(self) # --> get tupple
    team_info_array = team_info_tupple[0] # extract the dict needed
    team_info_values = team_info_array.values()
    team_values = list(team_info_values)
    info_scores = get_weighted_average_array(team_values)
    return info_scores

def euclidean_distance(x,y):
    return sqrt(sum(pow(a-b,2) for a, b in zip(x, y)))


def get_team_motivation_score(self, format=None, *args, **kwargs):
    team_motivation_tupple =  get_motivation_array(self)
    team_motivation_array = team_motivation_tupple[0]
    team_motivation_values = team_motivation_array.values()
    team_values = list(team_motivation_values)

    motiv_scores = get_weighted_average_array(team_values)
    analyzed_array = get_motivation_array(self)
    interest = get_trend(analyzed_array)
    motiv_scores[2] = list(interest.values())[0]
    team_motive_labels = {"label":list(interest.keys())[0]}
    return motiv_scores,team_motive_labels

def get_team_action_score(self, format=None, *args, **kwargs):

    team_action_tupple =  get_action_array(self)
    team_action_array = team_action_tupple[0]
    team_action_values = team_action_array.values()
    team_values = list(team_action_values)

    action_scores = get_weighted_average_array(team_values)
    analyzed_array = get_action_array(self)
    action = get_trend(analyzed_array)
    action_scores[1] = list(action.values())[0]
    team_action_labels = {"label":list(action.keys())[0]}

    return action_scores, team_action_labels

def get_behaviour_action_score(self, format=None, *args, **kwargs):

    team_behaviour_tupple =  get_behaviour_array(self)
    team_behaviour_array = team_behaviour_tupple[0]
    team_behaviour_values = team_behaviour_array.values()
    team_values = list(team_behaviour_values)
    behav_scores = get_weighted_average_array(team_values)
    analyzed_array = get_behaviour_array(self)
    behav = get_trend(analyzed_array)
    behav_scores[1] = list(behav.values())[0]
    team_behaviour_labels = {"label":list(behav.keys())[0]}

    return behav_scores,team_behaviour_labels

def get_trend(analyzed_array):
    analyzed_array2 = analyzed_array[0]
    analyzed_array_labels =  analyzed_array[2]
    max_label_occ = Counter(analyzed_array_labels.values()).most_common()
    max_label_occ_dict = dict(max_label_occ)

    check = {}
    for t in max_label_occ:
        lab = t[0]
        pond = t[1]
        list_go = 0
        for f in analyzed_array_labels:
            if analyzed_array_labels[f] == lab:
                value = analyzed_array2[f][2]
                list_go = list_go + value
                check.update({analyzed_array_labels[f]:list_go})

    max_value = max(list(check.values()))
    tendence_label = []
    for x, y in check.items():
        if y == max_value:
            tendence = x
            tendence_label.append(tendence)
    #print("tendence label: {0}".format(tendence_label))
    max_label = random.choice(tendence_label)
    score = max_value/max_label_occ_dict[max_label]
    trend_array = {max_label:round(score)}
    #print("interest:{0}".format(interest_trend_array))
    return trend_array


def get_team_cohesivenss_score(self, format=None, *args, **kwargs):
    team_info_tupple =  get_info_array(self)[0]
    team_motivation_tupple =  get_motivation_array(self)[0]
    team_action_tupple =  get_action_array(self)[0]
    team_behaviour_tupple =  get_behaviour_array(self)[0]
    array_dict ={}

    for a in team_info_tupple:
        w = team_info_tupple[a]
        x = team_motivation_tupple[a]
        y = team_action_tupple[a]
        z = team_behaviour_tupple[a]
        test = w + x + y + z
        array_dict.update({a:test})

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
    #print("Similarity bewteen users :{0}".format(simalarity_dict))
    team_score = round(np.mean(dist_list))
    return team_score,users,dist_list

def get_question_similarities(self, format=None, *args, **kwargs):
    team_info_tupple =  get_info_array(self)[0]
    team_motivation_tupple =  get_motivation_array(self)[0]
    team_action_tupple =  get_action_array(self)[0]
    team_behaviour_tupple =  get_behaviour_array(self)[0]
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
    info_index = len((list(team_info_tupple.values())[0]))
    info_similarities = question_similarities[0:info_index]
    motiv_index = info_index + len((list(team_motivation_tupple.values())[0]))
    motiv_similarities = question_similarities[(info_index):motiv_index]
    action_index = motiv_index + len((list(team_action_tupple.values())[0]))
    action_similarities = question_similarities[motiv_index:action_index]
    behav_index = action_index + len((list(team_behaviour_tupple.values())[0]))
    behav_similarities = question_similarities[action_index:behav_index]
    print(action_similarities)
    print(behav_similarities)
    return info_similarities,motiv_similarities,action_similarities,behav_similarities



def euclid_array(answer_per_question):
    go = []
    max_dist = round(math.sqrt(len(answer_per_question[0]*(200**2))))
    for i in answer_per_question:
        combi = list(it.combinations(i, 2))
        #print(combi)
        sum_diff = 0
        for lst in combi:
            diff = (lst[0] - lst[1])**2
            sum_diff = sum_diff + diff
        sqrd_val= math.sqrt(sum_diff)
        final_val = round((1-(sqrd_val/max_dist))*100)
        go.append(final_val)
    return go
