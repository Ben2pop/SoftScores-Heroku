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



class EmployeeChartData(APIView):
    #import pdb; pdb.set_trace()
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = []
    http_method_names = ['get',]

    #authentication_classes = []
    #permission_classes = []
    #serializer_class = MyUserSerializer

    def get_serializer_class(self):
        return self.serializer_class



    def get(self, request, format=None, *args, **kwargs):

        project_name = Project.objects.get(id=kwargs['pk1']).name
        #team_name_list = Project.objects.get(id=kwargs['pk1']).team_id.members.all()
        team_name_list = Project.objects.get(id=kwargs['pk1']).team_id.members.values_list('email', flat=True)
        team_name_list2 = Project.objects.get(id=kwargs['pk1']).team_id.members.all()
        serializer=self.serializer_class
        chunk_score = get_chunk_score(self)
        info_relationship = get_info_relationship(self)
        rep_system = get_rep_system(self)
        team_name_data = serializer(team_name_list2, many=True)
        team_name_data = team_name_data.data
        team_member_count = Project.objects.get(id=kwargs['pk1']).team_id.members.count()
        main_items2 = [1,2,3,-4,5,6,-7,8,9,-10,-11,12,13,14,15,16]
        #Test

        #end test
        info_process_data = [4,6,2,8,4]
        info_process_data2 = [8,2,5,2,4]
        action_process_data = [5,3,9]
        motivation_data = [4,5,1,8]
        behaviour_data = [6,3,9,1]
        raf_data = [3,5,8,9]


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
            "team_name_list":team_name_list,
            "team_name_list2":team_name_data,


        }
        return Response(data)




# class ChartData(APIView):
#
#     authentication_classes = []
#     permission_classes = []
#
#
#     def get(self, request, format=None, *args, **kwargs):
#
#         team_name = Project.objects.get(id=kwargs['pk']).team_id.team_name
#
#         main_items = [user_count, project_count,team_member_count,28,12,32]
#         main_items2 = [1,2,3,-4,5,6,-7,8,9,-10,-11,12,13,14,15,16]
#         info_process_data = [4,6,2,8,4]
#         info_process_data2 = [8,2,5,2,4]
#         action_process_data = [5,3,9]
#         motivation_data = [4,5,1,8]
#         behaviour_data = [6,3,9,1]
#         data = {
#             #labels
#             "labels":labels,
#             "labels_main_graph":labels_main_graph,
#             "information_processing_label": information_processing_label,
#             "action_process_label": action_process_label,
#             "motivation_label": motivation_label,
#             "behaviour_label":behaviour_label,
#             #data
#             "main":main_items,
#             "main2": main_items2,
#             "info_process_data": info_process_data,
#             "info_process_data2": info_process_data2,
#             "action_process_data": action_process_data,
#             "motivation_data":motivation_data,
#             "behaviour_data":behaviour_data,
#
#             #other
#             "team_name":team_name,
#             "team_list":team_list,
#             "team_name_list":team_name_list,
#         }
#         return Response(data)


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
