from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .forms import HRForm, TeamMembersForm, TeamMembersFormUpdate, InviteForm2
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.core.mail import EmailMessage
from .models import MyUser
from website.models import Team, Project
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect


def registerHR(request):
    registered  = False
    if request.method == "POST":
        HR_form = HRForm(data=request.POST)

        if HR_form.is_valid():
            user = HR_form.save()
            user.set_password(user.password)
            user.is_hr = True
            user.save()
            registered = True
        else:
            print("Error!")
    else:
        HR_form = HRForm()
    return render(request,'HR_registration_form.html',
                            {'HR_form':HR_form,
                             'registered':registered})

@csrf_protect
def HR_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = MyUser.objects.filter(email=email)

        if user:
            user=user[0]
            if user.is_active & user.is_hr & user.check_password(password):
                login(request,user)
                return HttpResponseRedirect(reverse('website:hr_index'))
            elif user.is_active & user.is_employee & user.check_password(password):
                login(request,user)
                return HttpResponseRedirect(reverse('website:employee_index'))
            elif user.is_active & user.is_candidate & user.check_password(password):
                login(request,user)
                return HttpResponseRedirect(reverse('website:candidate_index'))
            else:
                HttpResponse("Account not active, please contact Admin")
        else:
            print("Someone tried to login and failed")
            return HttpResponse("Invalid login detailed supplied!")
    else:
        return render(request,'HR_login.html',{})



def TeamRegister2(request):
    import pdb; pdb.set_trace()
    InviteFormSet = formset_factory(InviteForm2)

    if request.method == 'POST':
        formset = InviteFormSet(request.POST)

        if(formset.is_valid()):
            for i in formset:
                mail = i.cleaned_data['Email']
                if MyUser.objects.filter(email = mail).exists():
                    invited_user = MyUser.objects.get(email = mail)
                    current_site = get_current_site(request)
                    message = render_to_string('acc_join_email.html', {
                        'user': invited_user.first_name,
                        'domain':current_site.domain,
                        })
                    mail_subject = 'You have been invited to SoftScores.com please LogIn to get access to the app'
                    to_email = mail
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.send()
                else:
                    user = MyUser(email = mail)
                    password = MyUser.objects.make_random_password()
                    user.set_password(password)
                    user.is_active = False
                    user.is_employee = True
                    user.save()
                    u1 = user.id
                    a1 = MyUser.objects.get(email = request.user.email)
                    a2 = Project.objects.filter(project_hr_admin = a1)
                    a3 = a2.latest('id')
                    a4 = a3.team_id
                    a4.members.add(u1)

                    current_site = get_current_site(request)
                    message = render_to_string('acc_active_email.html', {
                    'user':user,
                    'domain':current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                    })
                    mail_subject = 'You have been invited to SoftScores.com please sign in to get access to the app'
                    to_email = user.email
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.send()
            messages.success(request, 'testouille la fripouille')
            return HttpResponseRedirect(reverse('website:ProjectDetails', kwargs={'pk':a3.id}))
        else:
            print("The entered form is not valid")

    else:
        formset = InviteFormSet()
    return render(request,'team_register.html', {'formset':formset})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


def CandidateSignIn(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)

    registered  = False
    if request.method == "POST":
        form = TeamMembersFormUpdate(data=request.POST, instance=request.user)

        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()
            #registered = True
            return HttpResponseRedirect(reverse('registration:HRlogin'))

        else:
            print("Error!")
    else:
        form = TeamMembersFormUpdate()
    return render(request,'candidateSignIn.html',
                            {'form':form,
                            'registered':registered})
