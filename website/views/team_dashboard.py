from math import sqrt
import math
import random
import itertools as it
import numpy as np
from collections import Counter
from registration.views import MyUser
from survey.models.response import Response
from rest_framework.views import APIView
from website.serializers import MyUserSerializer
from .candidate_dashboard import *
from .employee_dashboard import *
from .website_pages import *


class TeamChartData(APIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = []
    http_method_names = ['get', ]

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
                           [[motiv_team[1]['label']]],
                           ["Variety", "Routine"],
                          ]
        action_label = [
                       ["Active", "Reaction"],
                       [[action_team[1]['label']]],
                       ["Option", "Procedure"],
                       ["Perfection", "Optimizing"],
                       ["Sensor", "Intuition"]
                       ]
        other_data_label = [
                           ["External locus", "Internal locus"],
                           ["Strong Will", "Compliant"],
                           ["In time", "Through time"],
                           [[behav_team[1]['label']]],
                           ]
        complete_label = [
                         ["General", "Details"],
                         ["Sameness", "Difference"],
                         ["Visual", "Auditory"],
                         ["Static", "Process"],
                         ["Best Scenario", "Worst Scenario"],
                         ["Binary", "Shades"],
                         ["External", "Internal"],
                         ["Go Away", "Toward"],
                         [[motiv_team[1]['label']]],
                         ["Variety", "Routine"],
                         ["Active", "Reaction"],
                         [[action_team[1]['label']]],
                         ["Option", "Procedure"],
                         ["Perfection", "Optimizing"],
                         ["Sensor", "Intuition"],
                         ["External locus", "Internal locus"],
                         ["Strong Will", "Compliant"],
                         ["In time", "Through time"],
                         [[behav_team[1]['label']]]
                         ]

        data = {
            "team_info_score": chunk_team,
            "team_motiv_score": motiv_team,
            "team_action_score": action_team,
            "team_behaviour_score": behav_team,
            "team_complete": team_complete,
            "cohesiveness_score": cohesiveness_score[0],
            "users": cohesiveness_score[1],
            "user_dist": cohesiveness_score[2],
            "info_dist": info_dist,
            "motiv_dist": motiv_dist,
            "action_dist": action_dist,
            "behav_dist": behav_dist,
            "complete_label": complete_label,
            "info_label": processing_information_label,
            "motivation_label": motivation_label,
            "action_label": action_label,
            "behav_label": other_data_label,
        }
        return Response(data)

# TEAM CALCULATION


def get_team_complete_data(self, format=None, *args, **kwargs):
    # get all models's score
    total_array = [get_team_info_score(self),
                   get_team_motivation_score(self)[0],
                   get_team_action_score(self)[0],
                   get_behaviour_action_score(self)[0]]
    complete_array = []
    for i in total_array:
        complete_array = complete_array + i
    return complete_array


def get_weighted_average_array(team_values):
    # get a list of all score per categories (4 lists)
    team_values_list = team_values
    np_team_values_list = np.array(team_values_list)
    numb = (list(range(len(np_team_values_list[0]))))
    team_score = []
    for n in numb:
        col = np_team_values_list[:, n]
        trend_a = np.sum(col > 0)
        trend_b = np.sum(col < 0)
        sum_value = 0
        for i in col:
            if i > 0:
                val = i*trend_a
                sum_value = sum_value + val
            else:
                val = i*trend_b
                sum_value = sum_value + val
        means_value = round((sum_value)/((trend_a ** 2)+(trend_b ** 2)))
        team_score.append(means_value)
    return(team_score)


def get_team_info_score(self, format=None, *args, **kwargs):
    # Information process score list
    team_info_tupple = get_employee_info_array(self)
    team_info_array = team_info_tupple[0]
    team_info_values = team_info_array.values()
    team_values = list(team_info_values)
    info_scores = get_weighted_average_array(team_values)
    return info_scores


def euclidean_distance(x, y):
    dist = sqrt(sum(pow(a-b, 2) for a, b in zip(x, y)))
    return dist


def get_team_motivation_score(self, format=None, *args, **kwargs):
    # get motivation category score and labels
    team_motivation_tupple = get_employee_motivation_array(self)
    team_motivation_array = team_motivation_tupple[0]
    team_motivation_values = team_motivation_array.values()
    team_values = list(team_motivation_values)
    motiv_scores = get_weighted_average_array(team_values)

    interest = get_trend(team_motivation_tupple, 2)
    motiv_scores[2] = list(interest.values())[0]
    team_motive_labels = {"label": list(interest.keys())[0]}
    return motiv_scores, team_motive_labels


def get_team_action_score(self, format=None, *args, **kwargs):

    team_action_tupple = get_employee_action_array(self)
    team_action_array = team_action_tupple[0]
    team_action_values = team_action_array.values()
    team_values = list(team_action_values)

    action_scores = get_weighted_average_array(team_values)
    analyzed_array = get_employee_action_array(self)
    action = get_trend(analyzed_array, 1)
    action_scores[1] = list(action.values())[0]
    team_action_labels = {"label": list(action.keys())[0]}
    return action_scores, team_action_labels


def get_behaviour_action_score(self, format=None, *args, **kwargs):

    team_behaviour_tupple = get_employee_behav_array(self)
    team_behaviour_array = team_behaviour_tupple[0]
    team_behaviour_values = team_behaviour_array.values()
    team_values = list(team_behaviour_values)
    behav_scores = get_weighted_average_array(team_values)
    analyzed_array = get_employee_behav_array(self)
    behav = get_trend(analyzed_array, 3)
    behav_scores[3] = list(behav.values())[0]

    team_behaviour_labels = {"label": list(behav.keys())[0]}
    return behav_scores, team_behaviour_labels


def get_trend(analyzed_array, index):
    analyzed_array2 = analyzed_array[0]
    num = len(analyzed_array2)
    analyzed_array_labels = analyzed_array[2]
    max_label_occ = Counter(analyzed_array_labels.values()).most_common()
    max_label_occ_dict = dict(max_label_occ)

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
                check.update({analyzed_array_labels[f]: list_go2})
    max_value = max(list(check.values()))
    tendence_label = []
    for x, y in check.items():
        if y == max_value:
            tendence = x
            tendence_label.append(tendence)

    max_label = random.choice(tendence_label)
    trend_array = {max_label: max_value}
    return trend_array


def get_team_cohesivenss_score(self, format=None, *args, **kwargs):
    team_info_tupple = get_employee_info_array(self)[0]
    team_motivation_tupple = get_employee_motivation_array(self)[0]
    team_action_tupple = get_employee_action_array(self)[0]
    team_behaviour_tupple = get_employee_behav_array(self)[0]
    array_dict = {}
    for a in team_info_tupple:
        w = team_info_tupple[a]
        x = team_motivation_tupple[a]
        y = team_action_tupple[a]
        z = team_behaviour_tupple[a]
        test = w + x + y + z
        array_dict.update({a: test})

    score = get_team_cohesivenss_score2(array_dict)
    return score


def get_team_cohesivenss_score2(array_dict):
    list_keys = list(array_dict.keys())
    list_combi = list(it.combinations(list_keys, 2))

    final_dic = []
    for i in list_combi:
        temp_dict = {}
        for j in i:
            temp_dict.update({j: array_dict[j]})
        final_dic.append(temp_dict)
    dist_list = []
    max_dist = math.sqrt(19*(200**2))
    similarity_dict = {}
    users = []
    for val in final_dic:
        x = list(val.values())
        x_keys = list(val.keys())
        x_keys_str = str(x_keys[0]) + "-" + str(x_keys[1])

        distance = (euclidean_distance(x[0], x[1]))
        dist_score = round((1-(distance/max_dist))*100)
        dist_list.append(dist_score)
        user_1 = MyUser.objects.get(id=x_keys[0]).first_name + " " + MyUser.objects.get(id = x_keys[0]).last_name
        user_2 = MyUser.objects.get(id=x_keys[1]).first_name + " " + MyUser.objects.get(id = x_keys[1]).last_name
        user_pair = user_1 + ' - ' + user_2
        users.append(user_pair)
        similarity_dict.update({user_pair: dist_score})

    team_score = round(np.mean(dist_list))
    return team_score, users, dist_list


def get_question_similarities(self, format=None, *args, **kwargs):
    team_info_tupple = get_employee_info_array(self)[0]
    team_motivation_tupple = get_employee_motivation_array(self)[0]
    team_action_tupple = get_employee_action_array(self)[0]
    team_behaviour_tupple = get_employee_behav_array(self)[0]
    dict_user_answers = {}
    for a in team_info_tupple:
        w = team_info_tupple[a]
        x = team_motivation_tupple[a]
        y = team_action_tupple[a]
        z = team_behaviour_tupple[a]
        merged_array = w + x + y + z
        dict_user_answers.update({a: merged_array})

    numb_answers = len(list(dict_user_answers.values())[0])
    list_answers_values = list(dict_user_answers.values())

    answer_per_question = []
    for number in range(0, numb_answers):
        temp_array = []
        for val in list_answers_values:
            answer_value = val[number]
            temp_array.append(answer_value)
        answer_per_question.append(temp_array)
    question_similarities = euclid_array(answer_per_question)
    motiv_trend = get_dist_multiple_variable(get_employee_motivation_array(self), 2)
    question_similarities[8] = motiv_trend
    action_trend = get_dist_multiple_variable(get_employee_action_array(self), 1)
    question_similarities[11] = action_trend
    behav_trend = get_dist_multiple_variable(get_employee_behav_array(self), 3)
    question_similarities[11] = behav_trend
    info_index = len((list(team_info_tupple.values())[0]))
    info_similarities = question_similarities[0:info_index]
    motiv_index = info_index + len((list(team_motivation_tupple.values())[0]))
    motiv_similarities = question_similarities[(info_index):motiv_index]
    action_index = motiv_index + len((list(team_action_tupple.values())[0]))
    action_similarities = question_similarities[motiv_index:action_index]
    behav_index = action_index + len((list(team_behaviour_tupple.values())[0]))
    behav_similarities = question_similarities[action_index:behav_index]
    return info_similarities, motiv_similarities, action_similarities, behav_similarities


def euclid_array(answer_per_question):
    go = []
    max_dist = round(math.sqrt(len(answer_per_question[0]*(200**2))))
    for i in answer_per_question:
        combi = list(it.combinations(i, 2))

        sum_diff = 0
        for lst in combi:
            diff = (lst[0] - lst[1])**2
            sum_diff = sum_diff + diff
        sqrd_val = math.sqrt(sum_diff)
        final_val = round((1-(sqrd_val/max_dist))*100)
        go.append(final_val)
    return go


def get_dist_multiple_variable(array, index):
    labels_dict = array[2]
    list_combi_user_id = list(it.combinations(labels_dict, 2))
    max_dist = round(math.sqrt(len(array)*(200**2)))
    list_dis = []
    for combi in list_combi_user_id:
        dict_lab = {}
        for id_val in combi:
            lab = labels_dict[id_val]
            dict_lab.update({id_val: lab})
        if dict_lab[combi[0]] == dict_lab[combi[1]]:
            x1 = array[0][combi[0]][index]
            x2 = array[0][combi[1]][index]
        else:
            x1 = array[0][combi[0]][2]
            x2 = -array[0][combi[1]][2]
        dist_x = (x1-x2) ** 2
        list_dis.append(dist_x)
    euc_dist = sqrt(np.sum(list_dis))
    trend_similarity = round((1-(euc_dist/max_dist))*100)
    return trend_similarity


# 14
