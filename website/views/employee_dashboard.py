import json
import math
import itertools as it
from registration.views import MyUser
from survey.models import Survey
from survey.models.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from survey.models.response import Response as ResponseModel
from .team_dashboard import *
from .candidate_dashboard import *
from .website_pages import *


class EmployeeChartData(APIView):
    http_method_names = ['get', ]

    def get_serializer_class(self):
        return self.serializer_class

    def get(self, request, format=None, *args, **kwargs):

        info_array2 = get_employee_info_array(self)
        motivation_array2 = get_employee_motivation_array(self)
        action_array2 = get_employee_action_array(self)
        behav_array2 = get_employee_behav_array(self)
        complete = get_complete_data(self)
        current_user = get_current_user(self)
        current_team_member_id = get_current_team_member_id(self)
        label_pref = get_employee_motivation_array(self)[2][int(self.kwargs['pk2'])]
        affiliation_label = get_employee_action_array(self)[2][int(self.kwargs['pk2'])]
        knowledge_label = get_employee_behav_array(self)[2][int(self.kwargs['pk2'])]
        team_model_array = get_team_model_array(self)
        explanation = get_explanation(self)
        gender = get_gender(self)

        processing_information_label = [
                                        ["General", "Details"],
                                        ["Sameness", "Difference"],
                                        ["Visual", "Auditory"],
                                        ["Static", "Process"],
                                        ["Best Scenario", "Worst Scenario"],
                                        ["Binary", "Shades"],
                                        ]

        motivation_label = [
                           ["External", "Internal"],
                           ["Go Away", "Toward"],
                           ["Preference filter", label_pref],
                           ["Variety", "Routine"],
                           ]

        action_label = [
                    ["Active", "Reaction"],
                    [affiliation_label],
                    ["Option", "Procedure"],
                    ["Perfection", "Optimizing"],
                    ["Sensor", "Intuition"]

        ]

        other_data_label = [
                    ["External locus", "Internal locus"],
                    ["Strong Will", "Compliant"],
                    ["In time", "Through time"],
                    [knowledge_label],


        ]

        complete_label = [
                         ["General/", "Details"],
                         ["Sameness/", "Difference"],
                         ["Visual/", "Auditory"],
                         ["Static/", "Process"],
                         ["Best Scenario/", "Worst Scenario"],
                         ["Binary/", "Shades"],
                         ["External/", "Internal"],
                         ["Go Away/", "Toward"],
                         ["Preference filter:", label_pref],
                         ["Variety/", "Routine"],
                         ["Active/", "Reaction"],
                         [affiliation_label],
                         ["Option/", "Procedure"],
                         ["Perfection/", "Optimizing"],
                         ["Sensor/", "Intuition"],
                         ["External locus/", "Internal locus"],
                         ["Strong Will/", "Compliant"],
                         ["In time/", "Through time"],
                         [knowledge_label]
                         ]

        data = {
            "complete": complete,
            "complete_label": complete_label,
            "processing_information_label": processing_information_label,
            "motivation_label": motivation_label,
            "action_label": action_label,
            "other_data_label": other_data_label,
            "current_user": current_user,
            "current_team_member_id": current_team_member_id,
            "info_array2": info_array2,
            "motivation_array2": motivation_array2,
            "action_array2": action_array2,
            'behav_array2': behav_array2,
            "team_model_array": team_model_array,
            "explanation": explanation,
            "gender": gender,

        }
        return Response(data)


def get_current_user(self):
    current_user = MyUser.objects.get(id=self.kwargs['pk2'])
    current_user_id = current_user.id
    return current_user_id


def get_current_team_member_id(self):
    current_team = Project.objects.get(id=self.kwargs['pk1']).team_id.members.all()
    team_id_list = [0]
    for member in current_team:
        member_id = member.id
        team_id_list.append(member_id)

    ind = team_id_list.index(int(self.kwargs['pk2']))
    team_id_list.pop(ind)
    return team_id_list


def get_current_team(self, format=None, *args, **kwargs):
    current_team_member = Project.objects.get(id=self.kwargs['pk1']).team_id.members.all()
    members_response_list = []
    for member in current_team_member:
        member_id = member.id
        member_response = get_user_response(member_id)
        members_response_list.append({member_id: member_response})

    return members_response_list


def get_user_response(member_id):
    current_user = MyUser.objects.get(id=member_id)
    survey_team = Survey.objects.get(name='Survey SoftScores')
    if ResponseModel.objects.filter(user=current_user, survey=survey_team):
        current_response = ResponseModel.objects.filter(user=current_user, survey=survey_team)[0]
        return current_response
    else:
        pass


def get_current_response(self, format=None, *args, **kwargs):
    current_user = MyUser.objects.get(id=self.kwargs['pk2'])
    survey_team = Survey.objects.get(name='Survey SoftScores')
    if ResponseModel.objects.filter(user=current_user, survey=survey_team):
        current_response = ResponseModel.objects.filter(user=current_user, survey=survey_team)[0]
    else:
        pass
    return current_response


def get_complete_data(self, format=None, *args, **kwargs):

    total_array = [get_employee_info_array(self)[0],
                   get_employee_motivation_array(self)[0],
                   get_employee_action_array(self)[0],
                   get_employee_behav_array(self)[0]]
    complete_array = []
    for i in total_array:
        f = i[int(self.kwargs['pk2'])]
        complete_array = complete_array + f

    return complete_array

# Processing Informations


def get_employee_info_array(self, format=None, *args, **kwargs):
    response_list = get_current_team(self)
    info_array = get_info_array(response_list)
    return info_array


def get_info_array(array):
    current_response_list = array
    member_info_array_10 = {}
    member_info_array = {}
    for response_dic in current_response_list:
        current_response = list(response_dic.values())[0]
        chunk_score = get_chunk_score3(current_response)
        chunk_score_10 = (abs(get_chunk_score3(current_response))) / 10
        info_score = get_info_relationship3(current_response)
        info_score_10 = abs((get_info_relationship3(current_response))) / 10
        rep_system = get_rep_system3(current_response)
        rep_system_10 = (abs(get_rep_system3(current_response))) / 10
        reality = get_reality_structure3(current_response)
        reality_10 = (abs(get_reality_structure3(current_response))) / 10
        scenario = get_scenario_thinking3(current_response)
        scenario_10 = (abs(get_scenario_thinking3(current_response))) / 10
        perceptual = get_perceptual_category3(current_response)
        perceptual_10 = (abs(get_perceptual_category3(current_response))) / 10

        info_array_10 = [chunk_score_10, info_score_10, rep_system_10,
                         reality_10, scenario_10, perceptual_10]
        member_info_array_10.update({current_response.user_id: info_array_10})
        info_array = [chunk_score, info_score, rep_system, reality,
                      scenario, perceptual]
        member_info_array.update({current_response.user_id: info_array})
    return member_info_array, member_info_array_10


def get_chunk_score3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=1)
    answer_question2 = current_response.answers.get(question__quest_numb=2)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "3":
        score1 = list(json_answer_question1.values())[0]  # general
    else:
        score1 = -list(json_answer_question1.values())[0]  # details

    if answer_key_question2 == "1" or "3":
        score2 = list(json_answer_question2.values())[0]  # General
    else:
        score2 = -list(json_answer_question2.values())[0]  # detail

    chunk_score = math.ceil((score1 + score2) / 2)

    return chunk_score


def get_info_relationship3(current_response):

    answer_question1 = current_response.answers.get(question__quest_numb=5)
    answer_question2 = current_response.answers.get(question__quest_numb=17)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]  # Sameness
    else:
        score1 = -list(json_answer_question1.values())[0]  # Difference


    if answer_key_question2 == "1" or "2":
        score2 = list(json_answer_question2.values())[0]   # sameness
    else:
        score2 = -list(json_answer_question2.values())[0]  # difference

    info_relationship_score = math.ceil((score1 + score2) / 2)

    return info_relationship_score


def get_rep_system3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=1)
    answer_question2 = current_response.answers.get(question__quest_numb=16)
    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]  # visual
    else:
        score1 = -list(json_answer_question1.values())[0]  # auditory

    if answer_key_question2 == "2" or "3":
        score2 = list(json_answer_question2.values())[0]  # visual
    else:
        score2 = -list(json_answer_question2.values())[0]  # auditory

    rep_system_score = math.ceil((score1 + score2) / 2)

    return rep_system_score


def get_reality_structure3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=1)
    answer_question2 = current_response.answers.get(question__quest_numb=16)
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
    info_relationship_score = math.ceil((score1 + score2) / 2)

    return info_relationship_score


def get_scenario_thinking3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=6)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    if answer_key_question1 == "2" or "4":
        score1 = list(json_answer_question1.values())[0]  # best scenario
    else:
        score1 = -list(json_answer_question1.values())[0]  # worst scenario

    scenario_thinking_score = math.ceil((score1))

    return scenario_thinking_score


def get_perceptual_category3(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=5)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0]  # Binary
    else:
        score1 = -list(json_answer_question1.values())[0]  # Shades

    perceptual_category_score = math.ceil(score1)

    return perceptual_category_score


# End Processing Informations

# Motivation

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
        frame_10 = (abs(frame_reference)) / 10
        motivation_direction = get_motivation_direction2(current_response)
        motivation_direction_10 = (abs(motivation_direction)) / 10
        pref_sort = get_preference_sort2(current_response)[0]
        pref_sort_10 = (abs(pref_sort)) / 10
        openess = get_openess2(current_response)
        openess_10 = (abs(openess)) / 10
        pref_sort_label = get_preference_sort2(current_response)[1]
        pref_label_array.update({current_response.user_id: pref_sort_label})
        motivation_array = [frame_reference, motivation_direction,
                            pref_sort, openess]
        member_motivation_array.update({current_response.user_id: motivation_array})
        motivation_array_10 = [frame_10, motivation_direction_10,
                               pref_sort_10, openess_10]
        member_motivation_array_10.update({current_response.user_id: motivation_array_10})

    return member_motivation_array, member_motivation_array_10, pref_label_array


def get_frame_reference2(current_response):

    answer_question1 = current_response.answers.get(question__quest_numb=16)
    answer_question2 = current_response.answers.get(question__quest_numb=4)
    answer_question3 = current_response.answers.get(question__quest_numb=8)
    answer_question4 = current_response.answers.get(question__quest_numb=12)

    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    json_answer_question3 = json.loads(answer_question3.body)
    json_answer_question4 = json.loads(answer_question4.body)

    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    answer_key_question3 = list(json_answer_question3.keys())[0][0]
    answer_key_question4 = list(json_answer_question4.keys())[0][0]

    if answer_key_question1 == "1" or "2":
        score1 = list(json_answer_question1.values())[0]  # external
    else:
        score1 = -list(json_answer_question1.values())[0]  # internal

    if answer_key_question2 == "2" or "4":
        score2 = list(json_answer_question2.values())[0]  # external
    else:
        score2 = -list(json_answer_question2.values())[0]  # internal

    if answer_key_question3 == "2":
        score3 = list(json_answer_question3.values())[0]  # external
    else:
        score3 = -list(json_answer_question3.values())[0]  # internal

    if answer_key_question4 == "1" or "4":
        score4 = list(json_answer_question4.values())[0]  # external
    else:
        score4 = -list(json_answer_question4.values())[0]  # internal

    frame_reference_score = math.ceil((score1+score2+score3+score4)/4)

    return frame_reference_score


def get_motivation_direction2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=15)
    answer_question2 = current_response.answers.get(question__quest_numb=7)
    answer_question3 = current_response.answers.get(question__quest_numb=4)

    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)
    json_answer_question3 = json.loads(answer_question2.body)

    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]
    answer_key_question3 = list(json_answer_question3.keys())[0][0]

    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0] # toward
    else:
        score1 = -list(json_answer_question1.values())[0] # away from

    if answer_key_question2 == "1" or "2":
        score2 = list(json_answer_question2.values())[0] # toward
    else:
        score2 = -list(json_answer_question2.values())[0] # away from

    if answer_key_question3 == "1" or "2":
        score3 = list(json_answer_question3.values())[0] # toward
    else:
        score3 = -list(json_answer_question3.values())[0] # away from

    motivation_direction_score = math.ceil((score1+score2+score3)/3)

    return motivation_direction_score


def get_preference_sort2(current_response):

    answer_question1 = current_response.answers.get(question__quest_numb=3)
    answer_question2 = current_response.answers.get(question__quest_numb=18)

    json_answer_question1 = json.loads(answer_question1.body)
    json_answer_question2 = json.loads(answer_question2.body)

    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    answer_key_question2 = list(json_answer_question2.keys())[0][0]

    score1 = list(json_answer_question1.values())[0]
    score2 = list(json_answer_question2.values())[0]

    if answer_key_question1 == "1" and answer_key_question2 == "1":
        pref_sort_score = math.ceil((score1+score2)/2)  # case both are people
        pref_label = "People"
    elif answer_key_question1 == "2" and answer_key_question2 == "3":
        pref_sort_score = math.ceil((score1+score2)/2)  # case both are Places
        pref_label = "Place"
    elif answer_key_question1 == "3" and answer_key_question2 == "2":
        pref_sort_score = math.ceil((score1+score2)/2)  # case both are things
        pref_label = "Things"
    elif answer_key_question1 == "4" and answer_key_question2 == "4":
        pref_sort_score = math.ceil((score1+score2)/2)  # case both are Intellect
        pref_label = "Intellect"

    else:
        if score1 > score2:
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
    answer_question1 = current_response.answers.get(question__quest_numb=7)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]


    if answer_key_question1 == "1" or "3":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    openess_score = math.ceil(score1)

    return openess_score

# End Motivation

# Action sort


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
        affil_label_array.update({current_response.user_id: affiliation_label})
        action_array = [active, affiliation, option, expect, sensor]
        member_action_array.update({current_response.user_id: action_array})
        action_array_10 = [active_10, affiliation_10, option_10,
                           expect_10, sensor_10]
        member_action_array_10.update({current_response.user_id: action_array_10})

    return member_action_array, member_action_array_10, affil_label_array


def get_active_reactive2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=14)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]

    if answer_key_question1 == "1" or "3":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    act_score = math.ceil(score1)

    return act_score


def get_affliation_management2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=10)
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
    answer_question1 = current_response.answers.get(question__quest_numb=2)
    answer_question2 = current_response.answers.get(question__quest_numb=14)
    answer_question3 = current_response.answers.get(question__quest_numb=6)

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
    answer_question1 = current_response.answers.get(question__quest_numb=9)
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

# End Action sort

# To Define


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
        locus_10 = (abs(locus)) / 10
        temper = get_temper_to_instruction2(current_response)
        temper_10 = (abs(temper)) / 10
        time = get_time_sorting2(current_response)
        time_10 = (abs(time)) / 10
        knowledge = get_knowledge_sort2(current_response)[0]
        knowledge_10 = (abs(knowledge)) / 10

        knowledge_label = get_knowledge_sort2(current_response)[1]
        knowledge_label_array.update({current_response.user_id: knowledge_label})
        behaviour_array = [locus, temper, time, knowledge]
        behaviour_array_10 = [locus_10, temper_10, time_10, knowledge_10]
        member_behaviour_array.update({current_response.user_id: behaviour_array})
        member_behaviour_array_10.update({current_response.user_id: behaviour_array_10})

    return member_behaviour_array, member_behaviour_array_10, knowledge_label_array


def get_locus_control2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=20)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    locus_score = math.ceil(score1)

    return locus_score


def get_temper_to_instruction2(current_response):

    answer_question1 = current_response.answers.get(question__quest_numb=21)
    json_answer_question1 = json.loads(answer_question1.body)
    answer_key_question1 = list(json_answer_question1.keys())[0][0]
    if answer_key_question1 == "1":
        score1 = list(json_answer_question1.values())[0]
    else:
        score1 = -list(json_answer_question1.values())[0]

    temper_score = math.ceil(score1)

    return temper_score


def get_time_sorting2(current_response):
    answer_question1 = current_response.answers.get(question__quest_numb=13)
    answer_question2 = current_response.answers.get(question__quest_numb=19)
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
    answer_question1 = current_response.answers.get(question__quest_numb=11)
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

    return knowledge_sort_score, knowledge_sort_label


def get_team_model_array(self, format=None, *args, **kwargs):
    info = get_employee_info_array(self)
    motiv = get_employee_motivation_array(self)
    action = get_employee_action_array(self)
    behave = get_employee_behav_array(self)
    user_id = list(info[0].keys())
    x = list(info[0].keys())
    x.remove(int(self.kwargs['pk2']))
    user_combi = []
    for i in x:
        user_combi.append(tuple((int(self.kwargs['pk2']), i)))

    value_array = []
    for val in user_id:
        complete = info[0][val] + motiv[0][val] + action[0][val] + behave[0][val]
        value_array.append({val: complete})
    return value_array, user_combi


def get_explanation(self, format=None, *args, **kwargs):
    team_array_list = get_team_model_array(self)[0]
    user_combi = get_team_model_array(self)[1]
    motiv_labels = get_employee_motivation_array(self)[2]
    action_labels = get_employee_action_array(self)[2]
    behav_labels = get_employee_behav_array(self)[2]

    team_array_dict = {}  # transforming team_array_list to a dict
    for val in team_array_list:
        team_array_dict.update(val)

    dic_combi_value = {}
    for i in user_combi:
        combi_val = list(zip(team_array_dict[i[0]], team_array_dict[i[1]]))
        dic_combi_value.update({i: combi_val})

    opposed_model = {}
    differ_model = {}
    for x, y in dic_combi_value.items():
        list_index_opposed = []
        list_index_differ = []
        for index, val in enumerate(y):
            if index == 8 or index == 11 or index == 18:
                if index == 8:
                    if motiv_labels[x[0]] != motiv_labels[x[1]]:
                        list_index_opposed.append(index)

                if index == 11:
                    if action_labels[x[0]] != motiv_labels[x[1]]:
                        list_index_opposed.append(index)

                if index == 18:
                    if behav_labels[x[0]] != motiv_labels[x[1]]:
                        list_index_opposed.append(index)

            else:
                if (val[0] ^ val[1]) >= 0:
                    if ((val[0] - val[1]) ** 2) > 900:
                        list_index_differ.append(index)
                else:
                    list_index_opposed.append(index)
        opposed_model.update({str(x[1]): list_index_opposed})
        differ_model.update({str(x[1]): list_index_differ})
    return opposed_model, differ_model


def get_gender(self):
    gender_array = {}
    current_team = Project.objects.get(id=self.kwargs['pk1']).team_id.members.all()
    for i in current_team:
        user_id = i.id
        user_gender = i.gender
        gender_array.update({user_id: user_gender})
    return gender_array
# 34
