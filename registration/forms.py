from django import forms
from django.contrib.auth.models import User
from .models import MyUser
from django.contrib.auth import get_user_model

User = get_user_model()

class HRForm(forms.ModelForm):
    password = forms.CharField(widget= forms.PasswordInput())

    class Meta():
        model = User
        fields = ('first_name','last_name','email','password','company')

class TeamMembersForm(forms.ModelForm):

    class Meta():
        model = User
        fields = ('email',)

class TeamMembersFormUpdate(forms.ModelForm):
    password = forms.CharField(widget= forms.PasswordInput())

    class Meta():
        model = User
        fields = ('first_name','last_name','password')


class InviteForm2(forms.Form):
    """
    Form for member email invite
    """
    Email = forms.EmailField(
                    widget=forms.EmailInput(attrs={
                        'placeholder': "Member's mail",
                    }),
                    required=False)
