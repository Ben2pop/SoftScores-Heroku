from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from registration.models import MyUser
from website.models import Team,Project
from survey.models import Response

class MyUserSerializer(ModelSerializer):
    team = serializers.SerializerMethodField()
    class Meta:
        model = MyUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'team',
        )
    def get_team(self, obj):
        print(obj) # for you to understand what's happening
        teams = Team.objects.filter(members=obj)
        serialized_teams = TeamSerializer(teams,many=True)
        return serialized_teams.data

    def get_project(self, obj):
        print(obj) # for you to understand what's happening
        project = Project.objects.all()
        serialized_projects = ProjectSerializer(Project,many=True)
        return serialized_projects.data


class TeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = (
            'team_name',
            'team_hr_admin',
            'members',  # you can exclude this field since it may seem duplicate
        )

class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'name',
            'team_id',
            'project_hr_admin',
            'candidat_answers'  # you can exclude this field since it may seem duplicate
        )
