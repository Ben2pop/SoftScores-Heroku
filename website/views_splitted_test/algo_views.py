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


def get_current_response(self, format=None, *args, **kwargs):
    current_user = MyUser.objects.get(id = self.kwargs['pk2']) #current_user
    survey_team = Survey.objects.get(name= 'Survey SoftScore') #survey team (to change to final one)
    current_response = ResponseModel.objects.filter(user = current_user, survey = survey_team)[0]

    return current_response
#
# def get_chunk_score2(self, format=None, *args, **kwargs):
#     question_list=[2,3]
#     key_listing = get_current_response(self,question_list)
#     print(key_listing)
#     return key_listing

def get_chunk_score(self, format=None, *args, **kwargs):
    current_response = get_current_response(self)
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
        print(score1)

    if answer_key_question2 == "1" or "3":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]

    chunk_score = math.ceil((score1+score2)/2)
    print("chunk Score: %s" % chunk_score)
    return chunk_score

def get_info_relationship(self, format=None, *args, **kwargs):
    current_response = get_current_response(self)
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
        print(score1)

    if answer_key_question2 == "1" or "2":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]

    info_relationship_score = math.ceil((score1+score2)/2)
    print("Info Relationship: %s" % info_relationship_score)
    return info_relationship_score

def get_rep_system(self, format=None, *args, **kwargs):
    current_response = get_current_response(self)
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
        print(score1)

    if answer_key_question2 == "2" or "3":
        score2 = list(json_answer_question2.values())[0]
    else:
        score2 = -list(json_answer_question2.values())[0]

    info_relationship_score = math.ceil((score1+score2)/2)
    if info_relationship_score > 0:
        print("Rep.System Visual: %s" % info_relationship_score)
    else:
        print("Rep.System auditory: %s" % info_relationship_score)
    return info_relationship_score

# def reality_structure(self, format=None, *args, **kwargs):
#     current_response = get_current_response(self)
#     answer_question1 = current_response.answers.get(question_id = 2)
#     answer_question2 = current_response.answers.get(question_id = 16)
#     json_answer_question1 = json.loads(answer_question1.body)
#     json_answer_question2 = json.loads(answer_question2.body)
#     answer_key_question1 = list(json_answer_question1.keys())[0][0]
#     answer_key_question2 = list(json_answer_question2.keys())[0][0]
#     if answer_key_question1 == "1" or "2":
#         score1 = list(json_answer_question1.values())[0]
#     else:
#         score1 = -list(json_answer_question1.values())[0]
#         print(score1)
#
#     if answer_key_question2 == "2" or "3":
#         score2 = list(json_answer_question2.values())[0]
#     else:
#         score2 = -list(json_answer_question2.values())[0]
#
#     info_relationship_score = math.ceil((score1+score2)/2)
#     if info_relationship_score > 0:
#         print("Rep.System Visual: %s" % info_relationship_score)
#     else:
#         print("Rep.System auditory: %s" % info_relationship_score)
#     return info_relationship_score
