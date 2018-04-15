from django.db import models
from registration.models import MyUser


from django.core.urlresolvers import reverse


class Team(models.Model):
    team_name = models.CharField(max_length=100, default='')
    team_hr_admin = models.ForeignKey(MyUser, blank=True, null=True)
    members = models.ManyToManyField(MyUser, related_name="members")

    def __str__(self):
        return self.team_name


class BaseProject(models.Model):
    name = models.CharField(max_length=250)
    team_id = models.ForeignKey(Team, blank=True, null=True)
    project_hr_admin = models.ForeignKey('registration.MyUser', blank=True, null=True)
    candidat_answers = models.ManyToManyField('survey.response', blank=True)
    applicant = models.ManyToManyField(MyUser, related_name="%(app_label)s_%(class)s_related", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def get_absolute_url(self):
        return reverse('website:ProjectDetails', kwargs={'pk1': self.pk})

    def __str__(self):
        return self.name


class Project(BaseProject):
    def has_member_responses(self, result=None):
        try:
            x = Project.objects.get(id=self.id).team_id.members.all()

            for i in x:
                result = 1
                if i.response_set.exists():
                    result = result * True
                else:
                    result = result * False
            return result
        except AttributeError:
            return False


class DemoProject(BaseProject):
    project_hr_admin = models.ManyToManyField('registration.MyUser', blank=True)

# class Project(models.Model):
#     ##################################################################
#     #### big bug if a someone created a two projects with no team ####
#     ##################################################################
#
#     name = models.CharField(max_length=250)
#     team_id = models.ForeignKey(Team, blank=True, null=True)
#     project_hr_admin = models.ForeignKey('registration.MyUser', blank=True, null=True)
#     candidat_answers = models.ManyToManyField('survey.response')
#     applicant = models.ManyToManyField(MyUser, related_name="applicant")
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def get_absolute_url(self):
#         return reverse('website:ProjectDetails', kwargs={'pk1': self.pk})
#
    # def has_member_responses(self, result=None):
    #     try:
    #         x = Project.objects.get(id=self.id).team_id.members.all()
    #
    #         for i in x:
    #             result = 1
    #             if i.response_set.exists():
    #                 result = result * True
    #             else:
    #                 result = result * False
    #         return result
    #     except AttributeError:
    #         return False

#     def __str__(self):
#         return self.name
