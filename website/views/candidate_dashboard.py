from registration.views import MyUser
from survey.models.response import Response
from rest_framework.views import APIView
from .employee_dashboard import *
from .team_dashboard import *
from .website_pages import *


class applicantChartData(APIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer,  # ProjectSerializer
    permission_classes = []
    http_method_names = ['get', ]
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'project_details.html'


    def get_serializer_class(self):
        return self.serializer_class


    def get(self, request, format=None, *args, **kwargs):
        from .team_dashboard import get_team_cohesivenss_score
        applicant_info_array = get_applicant_info_array(self)
        applicant_motivation_array = get_applicant_motivation_array(self)
        applicant_action_array = get_applicant_action_array(self)
        applicant_behav_array = get_applicant_behav_array(self)
        score = get_team_cohesivenss_score(self)
        applicant_cohesivenss_score = get_applicant_cohesivenss_score(self)
        applicant_complete_data = get_applicant_complete_data(self)
        current_user = get_current_user(self)

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
                           ["[motiv_team[1]['label']]"],
                           ["Variety", "Routine"],
                           ]
        action_label = [
                       ["Active", "Reaction"],
                       ["[action_team[1]['label']]"],
                       ["Option", "Procedure"],
                       ["Perfection", "Optimizing"],
                       ["Sensor", "Intuition"]
                       ]
        other_data_label = [
                           ["External locus", "Internal locus"],
                           ["Strong Will", "Compliant"],
                           ["In time", "Through time"],
                           ["[behav_team[1]['label']]"],
                           ]
        complete_label = [
                         ["General", "Details"],
                         ["Sameness", "Difference"],
                         ["Visual",  "Auditory"],
                         ["Static", "Process"],
                         ["Best Scenario", "Worst Scenario"],
                         ["Binary", "Shades"],
                         ["External", "Internal"],
                         ["Go Away", "Toward"],
                         ["[motiv_team[1]['label']]"],
                         ["Variety", "Routine"],
                         ["Active", "Reaction"],
                         ["[action_team[1]['label']]"],
                         ["Option", "Procedure"],
                         ["Perfection", "Optimizing"],
                         ["Sensor", "Intuition"],
                         ["External locus", "Internal locus"],
                         ["Strong Will",  "Compliant"],
                         ["In time", "Through time"],
                         ["[behav_team[1]['label']]"]
                         ]

        data = {
                # data
                'applicant_info_array': applicant_info_array,
                'applicant_motivation_array': applicant_motivation_array,
                'applicant_action_array': applicant_action_array,
                'applicant_behav_array': applicant_behav_array,

                # Label
                'complete_label': complete_label,
                'applicant_sim_label': applicant_cohesivenss_score[1],
                'applicant_sim_score': applicant_cohesivenss_score[2],

                'applicant_complete_data': applicant_complete_data,
                'current_user': current_user,
                'processing_information_label': processing_information_label,
                'motivation_label': motivation_label,
                'action_label': action_label,
                'other_data_label': other_data_label,


        }
        return Response(data)

##################################################################


def get_applicant_team_list(self, format=None, *args, **kwargs):
    current_team_member = list(Project.objects.get(id=self.kwargs['pk1']).team_id.members.all())
    current_applicant = MyUser.objects.get(id=self.kwargs['pk2'])
    current_team_member.append(current_applicant)
    applicant_response_list = []
    for member in current_team_member:
        applicant_id = member.id
        applicant_response = get_user_response(applicant_id)
        applicant_response_list.append({applicant_id: applicant_response})
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
    from .team_dashboard import get_team_cohesivenss_score2
    team_info_tupple = get_applicant_info_array(self)[0]
    team_motivation_tupple = get_applicant_motivation_array(self)[0]
    team_action_tupple = get_applicant_action_array(self)[0]
    team_behaviour_tupple = get_applicant_behav_array(self)[0]
    array_dict = {}
    for a in team_info_tupple:
        w = team_info_tupple[a]
        x = team_motivation_tupple[a]
        y = team_action_tupple[a]
        z = team_behaviour_tupple[a]
        test = w + x + y + z
        array_dict.update({a: test})

    score = get_team_cohesivenss_score2(array_dict)

    applicant = MyUser.objects.get(id=self.kwargs['pk2'])
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
    return(array_dict)


def get_applicant_response_context(app_id):
    applicant_response = get_user_response(app_id)
    applicant_response_dict = [{app_id: applicant_response}]
    info_array = get_info_array(applicant_response_dict)[0]
    motiv_array = get_motivation_array(applicant_response_dict)[0]
    action_array = get_action_array(applicant_response_dict)[0]
    behav_array = get_behaviour_array(applicant_response_dict)[0]
    array_dict = {}
    for a in info_array:
        w = info_array[a]
        x = motiv_array[a]
        y = action_array[a]
        z = behav_array[a]
        test = w + x + y + z
        array_dict.update({a: test})
    return(array_dict)
