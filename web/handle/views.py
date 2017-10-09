#!/usr/bin/env python
# coding: utf-8

from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib import auth
from django.contrib.auth.models import User
from django.template import RequestContext, Context


from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from handle.forms import RegisterForm, LoginForm, ProfileForm
from handle.models import Handle
import hashlib
from datetime import datetime
from ojutility.func import printError
from submission.models import *

def register_user(request, form):
    username = form.cleaned_data['username']
    password1 = form.cleaned_data['password1']
    password2 = form.cleaned_data['password2']
    email = form.cleaned_data['email']
    if password1 != password2: return "two password can't be different"
    try:
        user = User.objects.get(username__iexact = username)
        return 'User %s is exist alreadly' % username
    except User.DoesNotExist:
        user = User.objects.create_user(username = username, email = email, password = password1)
        user.is_active = True
        user.save()
        newHandle = Handle(
            user = user,
            grade = form.cleaned_data['grade'],
            school = form.cleaned_data['school'],
            realname = form.cleaned_data['realname'],
        )
        newHandle.save()
        if newHandle.id == 1:
            newHandle.user.is_superuser = True
            newHandle.user.save()
        return None
    return 'unknown error'

# todo: 如果用户已经登录，提示先退出
def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    form = RegisterForm()
    errors = []
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            error_msg = register_user(request, form)
            if error_msg:
                errors.append(error_msg)
            else:
                return HttpResponseRedirect("/")

    context = {'form': form}
    context.update({'errors': errors})
    return render_to_response("register.html", context, context_instance=RequestContext(request))

def editProfile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            if request.user.username != form.cleaned_data['username']:
                return printError('you can not modify this profile')
            username = form.cleaned_data['username']
            password = form.cleaned_data['orginalpassword']
            user = auth.authenticate(username = username, password = password)
            if user == None:
                return printError('your orignal password is wrong')
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if len(password1) > 0:
                if len(password1) <= 8:
                    return printError('passowrd is too short')
                if password1 != password2:
                    return printError('two password not match')
                user.password = hashlib.sha1(password1).hexdigest()

            user.email = form.cleaned_data['email']
            handle = Handle.objects.get(user = user)
            handle.signature = form.cleaned_data['signature']
            handle.headurl = form.cleaned_data['headurl']
            handle.school = form.cleaned_data['school']
            handle.grade = form.cleaned_data['grade']
            handle.realname = form.cleaned_data['realname']
            handle.save()
            return HttpResponseRedirect("/handle/profile/%s" % user.username)
    else:
        handle = Handle.objects.get(user = request.user)
        context = {'handle' : handle}
        return render_to_response('editprofile.html', context, context_instance = RequestContext(request))

# todo: 如果用户已经登录，提示先退出
def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    if 'next' in request.GET:
        REDIRECT_URL = request.GET['next']
    else:
        REDIRECT_URL = '/'

    form = LoginForm()
    errors = []
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username = username, password = password)
            if user == None:
                return printError('username or password not match')

            if not (user.is_active or user.is_superuser):
                return printError('your handle was unactivated, please contact the administration')

            if user is not None:
                auth.login(request, user)
                handle = Handle.objects.get(user = user)
                handle.save()
                return HttpResponseRedirect(REDIRECT_URL)
            else:
                errors.append('username and password not match')

    context = {'form': form, 'errors': errors}
    return render_to_response('login.html', context, context_instance = RequestContext(request))

def logout(request):
    auth.logout(request)
    form = LoginForm()
    context = {'form': form}
    return HttpResponseRedirect('/handle/login/', context)

def _get_user_solved_problem(user):
    s = Submission.objects.filter(user = user, status = 1)
    result = [each.pid for each in s]
    return list(set(result))

def profile_view(request, username):
    if not username: username = request.user
    user = get_object_or_404(User, username = username)
    profile = get_object_or_404(Handle, user = user)
    solved_problems= _get_user_solved_problem(user)
    user_profile = {}
    user_profile.update(user.__dict__)
    user_profile.update(profile.__dict__)
    content = {'user' : user_profile, 'solved_problems' : solved_problems}

    return render_to_response('profile.html', content, context_instance = RequestContext(request))

