from django import forms
from django.contrib.auth.models import User
from registration.models import MyUser
from .models import Team
from django.contrib.auth import get_user_model

User = get_user_model()


class EditSelectTeam(forms.Form):

    team_choice = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=None)

    def __init__(self, user, *args, **kwargs):
        super(EditSelectTeam, self).__init__(*args, **kwargs)
        self.fields['team_choice'].queryset = Team.objects.all().filter(team_hr_admin = user)

    # def team_select(self):
    #    data = self.cleaned_data['team_choice']
    #    return data
