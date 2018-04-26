from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from website.models import Project, Team
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from registration.views import MyUser
from website.forms import EditSelectTeam
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from survey.models import Survey
from survey.models.response import Response
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import math
from website.views.team_dashboard import *
from website.views.candidate_dashboard import *
from website.views.employee_dashboard import *
from website.views.team_dashboard import *


# class LinkTeam(generic.ListView):
#     template_name = 'link_project.html'
#
#     def get_queryset(self):
#         queryset = Team.objects.filter(team_hr_admin=self.request.user)
#         return queryset
#
#
# def TeamSelect(request, pk1=None):
#     # import pdb; pdb.set_trace()
#     if request.method == "POST":
#         select_form = EditSelectTeam(request.user, request.POST)
#         if select_form.is_valid():
#             data = select_form.cleaned_data['team_choice']
#             obj2 = Project.objects.filter(project_hr_admin=request.user)
#             obj3 = obj2.latest('id')
#             if obj3.team_id is None:
#                 obj3.team_id = data
#                 obj3.save()
#                 obj4 = obj3.team_id
#                 obj5 = obj4.members.all()
#
#                 for i in obj5:
#                     current_site = get_current_site(request)
#                     message = render_to_string('acc_join_email.html', {
#                         'user': i.first_name,
#                         'domain': current_site.domain,
#                     })
#                     mail_subject = 'You have been invited to SoftScores.com please LogIn to get access to the app'
#                     to_email = i.email
#                     email = EmailMessage(mail_subject, message, to=[to_email])
#                     email.send()
#                 messages.success(request, 'test')
#                 return HttpResponseRedirect(reverse('website:ProjectDetails', kwargs={'pk1': obj3.id}))
#             else:
#                 print('this project has already a team')
#         else:
#             print('Non Valid form')
#
#     else:
#         # import pdb; pdb.set_trace()
#         select_form = EditSelectTeam(request.user)
#     return render(request,'link_project.html',
#                             {'select_form':select_form })


class CreateProject(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['name']
    template_name = "create_project.html"

    def form_valid(self, form):
        form.instance.project_hr_admin = self.request.user
        self.request.user.credit = self.request.user.credit - 1
        self.request.user.save()
        return super(CreateProject, self).form_valid(form)

    def get_success_url(self):
        return reverse('website:create_team', kwargs={'pk1': self.object.pk})


class HRIndex(generic.ListView):
    template_name = "HR_index.html"
    model = Project

    def get_queryset(self):
        return Project.objects.filter(project_hr_admin_id=self.request.user).order_by('-created_at')


    def get_context_data(self, **kwargs):
        #import pdb; pdb.set_trace()
        context = super(HRIndex, self).get_context_data(**kwargs)
        status_dict = {}
        try:
            for project in Project.objects.filter(project_hr_admin_id=self.request.user):
                proj_team_id = project.team_id
                proj_memb = proj_team_id.members.all()
                open_close = 1
                for memb in proj_memb:
                    if not list(memb.response_set.all()):
                        status = False
                    else:
                        status = True
                    open_close = open_close * status

                status_dict.update({project.id: open_close})

                context['status_dict'] = status_dict
        except AttributeError:
            pass
        return context


class CreateTeam(CreateView):

    model = Team
    fields = ['team_name']
    template_name = 'create_team.html'

    def form_valid(self, form, *arg, **kwargs):
        valid = super(CreateTeam, self).form_valid(form)
        form.instance.team_hr_admin = self.request.user
        obj = form.save()
        # SELECT * FROM project WHERE user = 'current_user' AND team_id = NULL
        current_project = Project.objects.get(id=self.kwargs['pk1'])
        current_project.team_id = obj
        current_project.save()
        if self.request.user.is_manager:
            user_id = self.request.user.id
            current_team = current_project.team_id
            current_team.members.add(user_id)
        return valid
        return super(TeamCreate, self).form_valid(form)

    def get_success_url(self):
        # import pdb; pdb.set_trace()
        project = Project.objects.get(team_id=None, project_hr_admin=self.request.user)
        return reverse('registration:team_register3', kwargs={'pk1': project.id})


class TeamCreate(CreateView):

    model = Team
    fields = ['team_name']
    template_name = 'team_form.html'

    def form_valid(self, form):
        # import pdb; pdb.set_trace()
        valid = super(TeamCreate, self).form_valid(form)
        form.instance.team_hr_admin = self.request.user
        obj = form.save()
        # SELECT * FROM project WHERE user = 'current_user' AND team_id = NULL
        current_project = Project.objects.get(id=self.kwargs['pk1'])
        current_project.team_id = obj
        current_project.save()
        return valid
        return super(TeamCreate, self).form_valid(form)

    def get_success_url(self):
        #import pdb; pdb.set_trace()
        project = Project.objects.get(team_id=None, project_hr_admin=self.request.user)
        return project.get_absolute_url()


class CandidateIndex(TemplateView):
    #import pdb; pdb.set_trace()
    template_name = "candidate_index.html"


class EmployeeIndex(TemplateView):
    #import pdb; pdb.set_trace()
    template_name = "employee_index.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Project,id=self.kwargs['pk2'])

    def get_context_data(self, **kwargs):
        context = super(EmployeeIndex, self).get_context_data(**kwargs)
        surveys = Survey.objects.filter(is_published=True)
        user_response_count  = MyUser.objects.get(id = self.kwargs['pk2']).response_set.count()
        #current_user = MyUser.objects.get(id = )
        if not self.request.user.is_authenticated():
            surveys = surveys.filter(need_logged_user=False)
        context['surveys'] = surveys
        context['user_response_count'] = user_response_count
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
        return get_object_or_404(Project, id=self.kwargs['pk1'])

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
            innov_score = get_innovation_score(self)
            exec_score = get_execution_score(self)
            com_score = get_comunication_score(self)
            motiv_score = get_motiv_score(self)
            context['team_name'] = team_name
            context['score'] = score
            context['all_user_response'] = all_user_response
            context['innov_score'] = innov_score
            context['exec_score'] = exec_score
            context['com_score'] = com_score
            context['motiv_score'] = motiv_score

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

        context = {
            'employee_name': employee_name,
            'team_list': team_list,
            'team_list_pop': team_list_pop,
        }
        return context

    def pronoun(self, possessive=False):
        if possessive:
            return "his" if self.gender == 'male' else "her" if self.gender == 'female' else "their"
        else:
            return "he" if self.gender == 'male' else "she" if self.gender == 'female' else "they"


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
        employee_name = MyUser.objects.get(id=self.kwargs['pk2'])
        diff_score = get_applicant_cohesivenss_score(self)[0][0] - get_team_cohesivenss_score(self)[0]
        team_list_pop = Project.objects.get(id=self.kwargs['pk1']).team_id.members.all().exclude(id=self.kwargs['pk2'])
        context['team_score'] = team_score
        context['applicant_score'] = applicant_score
        context['diff_score'] = diff_score
        context['team_list_pop'] = team_list_pop
        context['employee_name'] = employee_name

        return context


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


#11#
