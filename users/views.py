from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .tokens import account_activation_token
from .models import User



def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('acc_active_email.html', {
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            send_mail('helo', message, settings.DEFAULT_FROM_EMAIL, [to_email,])
            return render(request, 'users/signup_done.html')
    else:
        form = CustomUserCreationForm(None)
    return render(request, 'users/signup.html', {'form': form})



def activate(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    user = User.objects.get(pk=uid)
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('اکانت شما با موفقيت تاييد شد. اکنون مي توانيد وارد اکانت خود شويد. با تشکر')
    else:
        return HttpResponse('Activation link is invalid!')


def profile(request, pointer=0):
    #displaying profile_form
    if request.method == 'GET' and pointer:
        form = CustomUserChangeForm(instance=request.user)
        '''i put befor instance=request.user, initial={'email':request.user.email,
        'phone':request.user.phone...} that is true but longer'''
        return render(request, 'users/profile_form.html', {
            'CustomUserChangeForm':form})
   
    #displaying profile_page
    elif request.method == 'GET':
        return render(request, 'users/profile_page.html', {'set_pointer':1})

    #saving profile_form
    else:
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        return redirect('users:profile')







    
