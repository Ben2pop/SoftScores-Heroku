from django import forms
from django.contrib.auth.models import User
from .models import MyUser
from django.contrib.auth import get_user_model

User = get_user_model()


class HRForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'company')


class ManagerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ['email', 'first_name', 'last_name', 'company', 'position',
                  'gender', 'password',
                  ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = email.lower()
        print(email)
        return email

    def clean(self):
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        company = self.cleaned_data.get('company')
        position = self.cleaned_data.get('position')
        gender = self.cleaned_data.get('gender')

        if not first_name or not last_name or not company or not position or not gender:
            raise forms.ValidationError(
                'You have empty values, please enter a valid value for each field'
            )

        return self.cleaned_data




class TeamMembersForm(forms.ModelForm):

    class Meta():
        model = User
        fields = ('email',)


class TeamMembersFormUpdate(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('first_name', 'last_name', 'password')


class InviteForm2(forms.Form):
    """
    Form for member email invite
    """
    Email = forms.EmailField(
                    widget=forms.EmailInput(attrs={
                        'placeholder': "Member's mail",
                    }),
                    required=False)


class ApplicantForm2(forms.Form):
    """
    Form for member email invite
    """
    Email = forms.EmailField(
                    widget=forms.EmailInput(attrs={
                        'placeholder': "Member's mail",
                    }),
                    required=False)
